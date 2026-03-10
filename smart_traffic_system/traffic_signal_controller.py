"""
=============================================================================
 MODULE: traffic_signal_controller.py
 Smart Traffic Congestion Control System
=============================================================================
 DESCRIPTION:
   Core ML module that:
     1. Generates synthetic traffic data for a 3x3 city grid (9 junctions)
     2. Trains a PyTorch neural network to predict congestion per direction
     3. Dynamically allocates green signal timings based on predictions
     4. Runs a city-level analysis to identify critical junctions

 ARCHITECTURE FLOW:
   Synthetic Data → Neural Network → Congestion Score →
   Signal Timing Controller → City Analysis Report

 FUTURE HOOK:
   All raw inputs are isolated in TrafficDataPacket so they can later be
   replaced with homomorphically-encrypted tensors without changing the
   model inference or timing logic.
=============================================================================
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from dataclasses import dataclass, field
from typing import List, Tuple
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
DIRECTIONS          = ["North", "South", "East", "West"]
NUM_JUNCTIONS       = 9           # 3×3 city grid
TOTAL_GREEN_CYCLE   = 120         # seconds per full signal cycle
MIN_GREEN_TIME      = 10          # minimum green time per direction (seconds)
RANDOM_SEED         = 42
NUM_SAMPLES         = 5_000       # synthetic training samples
EPOCHS              = 40
BATCH_SIZE          = 64
LEARNING_RATE       = 1e-3

torch.manual_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ─────────────────────────────────────────────
#  DATA STRUCTURES
# ─────────────────────────────────────────────
@dataclass
class DirectionData:
    """Holds raw sensor readings for one direction of a junction."""
    name        : str
    vehicle_count: float   # number of vehicles
    avg_speed   : float    # km/h


@dataclass
class TrafficDataPacket:
    """
    Encapsulates all sensor data for one junction.
    Designed as the single boundary point for future encryption:
    swap `DirectionData` values with encrypted equivalents here.
    """
    junction_id : int
    directions  : List[DirectionData]   # always [N, S, E, W]

    def to_feature_vector(self) -> np.ndarray:
        """Flatten to [N_count, N_speed, S_count, S_speed, E_count, E_speed, W_count, W_speed]."""
        return np.array([v for d in self.directions for v in (d.vehicle_count, d.avg_speed)],
                        dtype=np.float32)


@dataclass
class SignalPlan:
    """Green-time allocation for one junction after ML inference."""
    junction_id         : int
    congestion_scores   : List[float]      # [N, S, E, W]  — 0.0 … 1.0
    green_times         : List[float]      # seconds per direction
    avg_congestion      : float = field(init=False)

    def __post_init__(self):
        self.avg_congestion = float(np.mean(self.congestion_scores))


# ─────────────────────────────────────────────
#  SYNTHETIC DATA GENERATOR
# ─────────────────────────────────────────────
class SyntheticTrafficGenerator:
    """
    Produces labelled (features, congestion_level) pairs.

    Congestion formula (per direction):
        congestion = clip( (count/max_count) * (1 - speed/max_speed), 0, 1 )
    This mimics real-world intuition: high vehicle count + low speed → high congestion.
    """

    MAX_VEHICLES = 100
    MAX_SPEED    = 80   # km/h

    def generate(self, n_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        counts = np.random.randint(0, self.MAX_VEHICLES + 1,
                                   size=(n_samples, 4)).astype(np.float32)
        speeds = np.random.uniform(5, self.MAX_SPEED,
                                   size=(n_samples, 4)).astype(np.float32)

        # Interleave: [c0, s0, c1, s1, c2, s2, c3, s3]
        X = np.empty((n_samples, 8), dtype=np.float32)
        X[:, 0::2] = counts
        X[:, 1::2] = speeds

        # Congestion label per direction
        c_norm = counts / self.MAX_VEHICLES
        s_norm = speeds / self.MAX_SPEED
        y = np.clip(c_norm * (1.0 - s_norm), 0.0, 1.0).astype(np.float32)

        return X, y

    @staticmethod
    def normalize(X: np.ndarray,
                  mean: np.ndarray = None,
                  std : np.ndarray = None):
        if mean is None:
            mean = X.mean(axis=0)
            std  = X.std(axis=0) + 1e-8
        return (X - mean) / std, mean, std


# ─────────────────────────────────────────────
#  NEURAL NETWORK MODEL
# ─────────────────────────────────────────────
class CongestionNet(nn.Module):
    """
    Fully-connected feed-forward network.

    Input  : 8 features  [count_N, speed_N, count_S, speed_S, …]
    Output : 4 congestion scores (sigmoid → 0–1 per direction)

    Architecture chosen for:
      • Low latency inference (fits edge deployment)
      • Sigmoid output compatible with future encrypted activation approximations
    """

    def __init__(self, input_dim: int = 8, hidden_dims: Tuple = (64, 128, 64)):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU()]
            prev = h
        layers += [nn.Linear(prev, 4), nn.Sigmoid()]
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ─────────────────────────────────────────────
#  TRAINER
# ─────────────────────────────────────────────
class ModelTrainer:
    """Handles training loop, validation split, and best-model checkpointing."""

    def __init__(self, model: CongestionNet, lr: float = LEARNING_RATE):
        self.model     = model
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()
        self.history   = {"train_loss": [], "val_loss": []}

    def train(self, X: np.ndarray, y: np.ndarray,
              epochs: int = EPOCHS, batch_size: int = BATCH_SIZE,
              val_split: float = 0.15) -> None:

        # Train / validation split
        split = int(len(X) * (1 - val_split))
        X_tr, X_v = X[:split], X[split:]
        y_tr, y_v = y[:split], y[split:]

        tr_loader = DataLoader(
            TensorDataset(torch.tensor(X_tr), torch.tensor(y_tr)),
            batch_size=batch_size, shuffle=True)

        best_val, best_state = float("inf"), None

        print(f"\n{'─'*55}")
        print(f"  Training CongestionNet  |  {epochs} epochs  |  "
              f"{len(X_tr):,} train / {len(X_v):,} val samples")
        print(f"{'─'*55}")

        for epoch in range(1, epochs + 1):
            # ── Train ──
            self.model.train()
            t_loss = 0.0
            for xb, yb in tr_loader:
                self.optimizer.zero_grad()
                loss = self.criterion(self.model(xb), yb)
                loss.backward()
                self.optimizer.step()
                t_loss += loss.item() * len(xb)
            t_loss /= len(X_tr)

            # ── Validate ──
            self.model.eval()
            with torch.no_grad():
                v_pred = self.model(torch.tensor(X_v))
                v_loss = self.criterion(v_pred, torch.tensor(y_v)).item()

            self.history["train_loss"].append(t_loss)
            self.history["val_loss"].append(v_loss)

            if v_loss < best_val:
                best_val   = v_loss
                best_state = {k: v.clone() for k, v in self.model.state_dict().items()}

            if epoch % 8 == 0 or epoch == 1:
                print(f"  Epoch {epoch:>3}/{epochs}  │  "
                      f"Train Loss: {t_loss:.6f}  │  Val Loss: {v_loss:.6f}")

        self.model.load_state_dict(best_state)
        print(f"\n  ✅ Best validation loss: {best_val:.6f}")
        print(f"{'─'*55}\n")


# ─────────────────────────────────────────────
#  SIGNAL TIMING CONTROLLER
# ─────────────────────────────────────────────
class SignalTimingController:
    """
    Converts congestion scores → green-time allocation.

    Algorithm:
      1. Scale each score by its proportion of the total congestion.
      2. Guarantee every direction gets at least MIN_GREEN_TIME seconds.
      3. Distribute remaining time proportionally.
    """

    def allocate(self, junction_id: int,
                 congestion_scores: List[float]) -> SignalPlan:

        scores = np.array(congestion_scores, dtype=np.float64)
        total  = scores.sum()

        if total < 1e-6:
            # No congestion detected → equal time split
            green_times = [TOTAL_GREEN_CYCLE / 4] * 4
        else:
            reserved    = MIN_GREEN_TIME * 4
            extra_pool  = TOTAL_GREEN_CYCLE - reserved
            proportions = scores / total
            green_times = (MIN_GREEN_TIME + proportions * extra_pool).tolist()

        return SignalPlan(
            junction_id       = junction_id,
            congestion_scores = congestion_scores,
            green_times       = [round(t, 1) for t in green_times]
        )


# ─────────────────────────────────────────────
#  CITY TRAFFIC ANALYZER
# ─────────────────────────────────────────────
class CityTrafficAnalyzer:
    """
    Runs the full pipeline for all 9 junctions and produces a city report.
    """

    GRID_LABELS = {
        1: "J1 (NW)", 2: "J2 (N)",  3: "J3 (NE)",
        4: "J4 (W)",  5: "J5 (C)",  6: "J6 (E)",
        7: "J7 (SW)", 8: "J8 (S)",  9: "J9 (SE)"
    }

    def __init__(self, model: CongestionNet,
                 norm_mean: np.ndarray, norm_std: np.ndarray):
        self.model      = model
        self.norm_mean  = norm_mean
        self.norm_std   = norm_std
        self.controller = SignalTimingController()

    def _infer(self, packet: TrafficDataPacket) -> List[float]:
        """Run ML inference for one junction. Returns [N,S,E,W] congestion scores."""
        raw_x  = packet.to_feature_vector().reshape(1, -1)
        norm_x = (raw_x - self.norm_mean) / self.norm_std
        self.model.eval()
        with torch.no_grad():
            pred = self.model(torch.tensor(norm_x, dtype=torch.float32))
        return pred.squeeze().tolist()

    def analyze_city(self, packets: List[TrafficDataPacket]) -> List[SignalPlan]:
        plans = []
        for packet in packets:
            scores = self._infer(packet)
            plan   = self.controller.allocate(packet.junction_id, scores)
            plans.append(plan)
        return plans

    def print_junction_report(self, plan: SignalPlan) -> None:
        jlabel = self.GRID_LABELS.get(plan.junction_id, f"J{plan.junction_id}")
        bar_max = 20

        print(f"\n  ┌─{'─'*44}┐")
        print(f"  │  🚦 Junction {jlabel:<32} │")
        print(f"  ├─{'─'*44}┤")
        print(f"  │  {'Direction':<8} │ {'Congestion':>10} │ {'Green Time':>12} │  {'Bar':<15}  │")
        print(f"  ├─{'─'*44}┤")

        for d, score, gtime in zip(DIRECTIONS,
                                   plan.congestion_scores,
                                   plan.green_times):
            bar_len = int(score * bar_max)
            bar     = "█" * bar_len + "░" * (bar_max - bar_len)
            icon    = "🔴" if score > 0.65 else "🟡" if score > 0.35 else "🟢"
            print(f"  │  {d:<8} │ {icon} {score:>6.3f}   │  {gtime:>7.1f}s     │  {bar}  │")

        print(f"  ├─{'─'*44}┤")
        print(f"  │  Avg Congestion: {plan.avg_congestion:.3f}   "
              f"Cycle: {sum(plan.green_times):.0f}s{'':<12}│")
        print(f"  └─{'─'*44}┘")

    def print_city_summary(self, plans: List[SignalPlan]) -> None:
        avg_scores = [(p.junction_id, p.avg_congestion) for p in plans]
        sorted_asc = sorted(avg_scores, key=lambda x: x[1])
        critical   = sorted_asc[-1]
        least      = sorted_asc[0]

        print(f"\n{'═'*52}")
        print("  🏙️  CITY-LEVEL TRAFFIC ANALYSIS REPORT")
        print(f"{'═'*52}")
        print(f"\n  Junction │ Avg Congestion │ Status")
        print(f"  {'─'*38}")
        for jid, score in sorted_asc:
            label  = self.GRID_LABELS.get(jid, f"J{jid}")
            status = ("🚨 CRITICAL" if score > 0.65
                      else "⚠️  MODERATE" if score > 0.35
                      else "✅ CLEAR")
            print(f"  {label:<10} │ {score:>12.3f}   │ {status}")

        print(f"\n  {'─'*48}")
        print(f"  🚨 Most  Congested : {self.GRID_LABELS[critical[0]]}"
              f"  (score={critical[1]:.3f})")
        print(f"  ✅ Least Congested : {self.GRID_LABELS[least[0]]}"
              f"  (score={least[1]:.3f})")
        print(f"\n  📌 Smart Suggestions:")
        print(f"     • Re-route traffic away from {self.GRID_LABELS[critical[0]]}")
        print(f"     • Extend green cycles at {self.GRID_LABELS[critical[0]]} by +20%")
        print(f"     • {self.GRID_LABELS[least[0]]} can absorb overflow traffic")
        print(f"{'═'*52}\n")


# ─────────────────────────────────────────────
#  DEMO PACKET BUILDER
# ─────────────────────────────────────────────
def build_demo_packets() -> List[TrafficDataPacket]:
    """
    Constructs realistic-looking traffic packets for all 9 junctions.
    In production, replace these with live sensor feeds.
    """
    # (vehicle_count, avg_speed_kmh) per direction [N, S, E, W]
    scenarios = [
        [(80, 12), (60, 20), (70, 15), (90, 10)],  # J1 – heavy congestion
        [(40, 35), (30, 40), (50, 30), (20, 50)],  # J2 – moderate
        [(10, 65), (15, 60), (5,  70), (8,  68)],  # J3 – clear
        [(55, 22), (65, 18), (45, 28), (70, 14)],  # J4 – heavy
        [(35, 38), (40, 32), (30, 42), (25, 48)],  # J5 – moderate (city centre)
        [(20, 52), (18, 55), (22, 50), (15, 60)],  # J6 – clear
        [(75, 11), (85, 9),  (60, 17), (80, 12)],  # J7 – critical
        [(50, 26), (45, 30), (55, 23), (40, 33)],  # J8 – moderate
        [(12, 62), (8,  68), (10, 65), (14, 60)],  # J9 – clear
    ]

    packets = []
    for jid, dirs in enumerate(scenarios, start=1):
        directions = [
            DirectionData(name=DIRECTIONS[i],
                          vehicle_count=dirs[i][0],
                          avg_speed    =dirs[i][1])
            for i in range(4)
        ]
        packets.append(TrafficDataPacket(junction_id=jid, directions=directions))
    return packets


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────
def main():
    print("\n" + "═"*55)
    print("  🔐🚦 Smart Traffic Signal Automation System")
    print("  Module: traffic_signal_controller.py")
    print("═"*55)

    # ── 1. Generate & Normalise Training Data ──────────────
    print("\n[1/4] Generating synthetic training data …")
    generator = SyntheticTrafficGenerator()
    X_raw, y  = generator.generate(NUM_SAMPLES)
    X, mean, std = SyntheticTrafficGenerator.normalize(X_raw)
    print(f"      Dataset shape  : X={X.shape}, y={y.shape}")
    print(f"      Feature mean   : {mean.round(2)}")
    print(f"      Feature std    : {std.round(2)}")

    # ── 2. Train Model ─────────────────────────────────────
    print("\n[2/4] Training CongestionNet …")
    model   = CongestionNet(input_dim=8, hidden_dims=(64, 128, 64))
    trainer = ModelTrainer(model, lr=LEARNING_RATE)
    trainer.train(X, y, epochs=EPOCHS, batch_size=BATCH_SIZE)

    # ── 3. Build Demo Junction Packets ────────────────────
    print("[3/4] Loading demo junction data …")
    packets = build_demo_packets()
    print(f"      Loaded {len(packets)} junction packets for the 3×3 city grid.")

    # ── 4. Analyse City ────────────────────────────────────
    print("\n[4/4] Running city-wide analysis …\n")
    analyzer = CityTrafficAnalyzer(model, mean, std)
    plans    = analyzer.analyze_city(packets)

    print("─"*52)
    print("  JUNCTION-LEVEL SIGNAL PLANS")
    print("─"*52)
    for plan in plans:
        analyzer.print_junction_report(plan)

    analyzer.print_city_summary(plans)


if __name__ == "__main__":
    main()
