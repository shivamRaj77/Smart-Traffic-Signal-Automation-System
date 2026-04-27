"""
=============================================================================
 MODULE: synthetic_traffic_generator.py
 Smart Traffic Congestion Control System
=============================================================================
 DESCRIPTION:
   A comprehensive synthetic traffic data generator that simulates realistic
   urban traffic patterns for a 3×3 city grid (9 junctions).

   Generates data across multiple real-world scenarios:
     • Rush Hour  (morning / evening peaks)
     • Night      (low volume, high speed)
     • Weekend    (scattered, moderate flow)
     • Rain       (slow speed, moderate count)
     • Accident   (blocked direction spike)
     • Normal     (baseline weekday traffic)

   Each sample includes:
     - Vehicle count per direction   [N, S, E, W]
     - Average speed per direction   [N, S, E, W]
     - Congestion label per direction (computed ground truth)
     - Scenario tag + junction ID

 OUTPUT FORMATS:
   • NumPy arrays  (for ML training)
   • CSV file      (for logging / analysis)
   • Summary stats (printed to console)

 DEPENDENCIES: numpy | csv | dataclasses
=============================================================================
"""

import numpy as np
import csv
import os
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from enum import Enum

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
DIRECTIONS    = ["North", "South", "East", "West"]
NUM_JUNCTIONS = 9
MAX_VEHICLES  = 100
MAX_SPEED     = 80    # km/h
MIN_SPEED     = 5     # km/h
RANDOM_SEED   = 42

np.random.seed(RANDOM_SEED)


# ─────────────────────────────────────────────
#  SCENARIO DEFINITIONS
# ─────────────────────────────────────────────
class Scenario(Enum):
    NORMAL      = "Normal"
    RUSH_HOUR   = "Rush Hour"
    NIGHT       = "Night"
    WEEKEND     = "Weekend"
    RAIN        = "Rain"
    ACCIDENT    = "Accident"


@dataclass
class ScenarioProfile:
    """
    Defines the statistical profile of a traffic scenario.
    count_range  : (min, max) vehicles per direction
    speed_range  : (min, max) km/h
    noise_std    : Gaussian noise sigma added on top
    weight       : Probability of this scenario being sampled
    """
    name        : str
    count_range : Tuple[int, int]
    speed_range : Tuple[float, float]
    noise_std   : float
    weight      : float
    description : str


# All six real-world scenario profiles
SCENARIO_PROFILES: Dict[Scenario, ScenarioProfile] = {

    Scenario.NORMAL: ScenarioProfile(
        name        = "Normal",
        count_range = (10, 60),
        speed_range = (25, 65),
        noise_std   = 5.0,
        weight      = 0.30,
        description = "Baseline weekday traffic — moderate flow, steady speed"
    ),

    Scenario.RUSH_HOUR: ScenarioProfile(
        name        = "Rush Hour",
        count_range = (60, 100),
        speed_range = (5, 25),
        noise_std   = 8.0,
        weight      = 0.25,
        description = "Morning/evening peak — high vehicle count, crawling speeds"
    ),

    Scenario.NIGHT: ScenarioProfile(
        name        = "Night",
        count_range = (0, 15),
        speed_range = (50, 80),
        noise_std   = 3.0,
        weight      = 0.15,
        description = "Late night — near-empty roads, vehicles moving fast"
    ),

    Scenario.WEEKEND: ScenarioProfile(
        name        = "Weekend",
        count_range = (20, 55),
        speed_range = (30, 60),
        noise_std   = 6.0,
        weight      = 0.15,
        description = "Weekend flow — scattered traffic, relaxed pace"
    ),

    Scenario.RAIN: ScenarioProfile(
        name        = "Rain",
        count_range = (30, 70),
        speed_range = (10, 35),
        noise_std   = 7.0,
        weight      = 0.10,
        description = "Wet weather — moderate vehicles but significantly reduced speed"
    ),

    Scenario.ACCIDENT: ScenarioProfile(
        name        = "Accident",
        count_range = (70, 100),
        speed_range = (5, 15),
        noise_std   = 4.0,
        weight      = 0.05,
        description = "Incident on road — one direction severely blocked, backlog builds"
    ),
}


# ─────────────────────────────────────────────
#  GENERATED SAMPLE DATACLASS
# ─────────────────────────────────────────────
@dataclass
class TrafficSample:
    """
    One complete traffic observation for a single junction.
    Stores raw readings, computed congestion, and metadata.
    """
    junction_id         : int
    scenario            : str
    vehicle_counts      : List[float]    # [N, S, E, W]
    avg_speeds          : List[float]    # [N, S, E, W]
    congestion_scores   : List[float]    # [N, S, E, W]  ground truth 0–1
    overall_congestion  : float = field(init=False)

    def __post_init__(self):
        self.overall_congestion = round(float(np.mean(self.congestion_scores)), 4)

    def to_feature_vector(self) -> np.ndarray:
        """Returns [c_N, s_N, c_S, s_S, c_E, s_E, c_W, s_W]"""
        vec = []
        for c, s in zip(self.vehicle_counts, self.avg_speeds):
            vec += [c, s]
        return np.array(vec, dtype=np.float32)

    def to_label_vector(self) -> np.ndarray:
        return np.array(self.congestion_scores, dtype=np.float32)


# ─────────────────────────────────────────────
#  CORE GENERATOR
# ─────────────────────────────────────────────
class SyntheticTrafficGenerator:
    """
    Generates synthetic traffic samples for a 3×3 city junction grid.

    Key design choices:
      1.  Scenario-weighted sampling — realistic distribution of conditions
      2.  Per-direction independence — each direction drawn separately
      3.  Accident injection — one random direction gets a spike in one sample
      4.  Gaussian noise — adds natural measurement variance
      5.  Ground-truth congestion label derived analytically:
              congestion = clip( (count/MAX_C) × (1 − speed/MAX_S), 0, 1 )
    """

    def __init__(self, seed: int = RANDOM_SEED):
        np.random.seed(seed)
        self._profiles  = SCENARIO_PROFILES
        self._scenarios = list(self._profiles.keys())
        self._weights   = [p.weight for p in self._profiles.values()]
        # Normalise weights to sum = 1
        total = sum(self._weights)
        self._weights = [w / total for w in self._weights]

    # ── Congestion Formula ────────────────────
    @staticmethod
    def _compute_congestion(counts: np.ndarray,
                            speeds: np.ndarray) -> np.ndarray:
        c_norm = np.clip(counts / MAX_VEHICLES, 0, 1)
        s_norm = np.clip(speeds / MAX_SPEED,    0, 1)
        return np.clip(c_norm * (1.0 - s_norm), 0.0, 1.0)

    # ── Single Sample Generator ───────────────
    def _generate_one(self, junction_id: int) -> TrafficSample:
        # Pick scenario
        scenario: Scenario = np.random.choice(self._scenarios, p=self._weights)
        profile  = self._profiles[scenario]

        lo_c, hi_c = profile.count_range
        lo_s, hi_s = profile.speed_range

        # Raw counts & speeds (4 directions)
        counts = np.random.uniform(lo_c, hi_c, 4)
        speeds = np.random.uniform(lo_s, hi_s, 4)

        # Add Gaussian noise
        counts += np.random.normal(0, profile.noise_std, 4)
        speeds += np.random.normal(0, profile.noise_std / 2, 4)

        # Accident: one random direction is severely blocked
        if scenario == Scenario.ACCIDENT:
            blocked_dir = np.random.randint(0, 4)
            counts[blocked_dir] = np.random.uniform(85, 100)
            speeds[blocked_dir] = np.random.uniform(2, 8)

        # Clip to valid physical range
        counts = np.clip(counts, 0, MAX_VEHICLES)
        speeds = np.clip(speeds, MIN_SPEED, MAX_SPEED)

        congestion = self._compute_congestion(counts, speeds)

        return TrafficSample(
            junction_id       = junction_id,
            scenario          = profile.name,
            vehicle_counts    = counts.round(1).tolist(),
            avg_speeds        = speeds.round(1).tolist(),
            congestion_scores = congestion.round(4).tolist()
        )

    # ── Batch Generator ───────────────────────
    def generate(self, n_samples: int,
                 for_junction: int = None) -> List[TrafficSample]:
        """
        Generate `n_samples` TrafficSample objects.
        If `for_junction` is None, samples are spread across all 9 junctions.
        """
        samples = []
        for i in range(n_samples):
            jid = for_junction if for_junction else (i % NUM_JUNCTIONS) + 1
            samples.append(self._generate_one(jid))
        return samples

    # ── NumPy Array Export ────────────────────
    def to_numpy(self, samples: List[TrafficSample]
                 ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns:
          X : shape (n, 8)  — feature matrix [c_N,s_N, c_S,s_S, c_E,s_E, c_W,s_W]
          y : shape (n, 4)  — congestion labels [N, S, E, W]
        """
        X = np.stack([s.to_feature_vector() for s in samples])
        y = np.stack([s.to_label_vector()   for s in samples])
        return X, y

    # ── CSV Export ────────────────────────────
    def to_csv(self, samples: List[TrafficSample],
               filepath: str = "traffic_data.csv") -> str:
        """Saves all samples to a CSV file. Returns the filepath."""
        headers = [
            "junction_id", "scenario",
            "count_N", "count_S", "count_E", "count_W",
            "speed_N", "speed_S", "speed_E", "speed_W",
            "cong_N",  "cong_S",  "cong_E",  "cong_W",
            "overall_congestion"
        ]
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for s in samples:
                writer.writerow({
                    "junction_id"       : s.junction_id,
                    "scenario"          : s.scenario,
                    "count_N"           : s.vehicle_counts[0],
                    "count_S"           : s.vehicle_counts[1],
                    "count_E"           : s.vehicle_counts[2],
                    "count_W"           : s.vehicle_counts[3],
                    "speed_N"           : s.avg_speeds[0],
                    "speed_S"           : s.avg_speeds[1],
                    "speed_E"           : s.avg_speeds[2],
                    "speed_W"           : s.avg_speeds[3],
                    "cong_N"            : s.congestion_scores[0],
                    "cong_S"            : s.congestion_scores[1],
                    "cong_E"            : s.congestion_scores[2],
                    "cong_W"            : s.congestion_scores[3],
                    "overall_congestion": s.overall_congestion,
                })
        return filepath

    # ── Summary Statistics ────────────────────
    def print_summary(self, samples: List[TrafficSample]) -> None:
        n = len(samples)
        scenario_counts: Dict[str, int] = {}
        all_congestion = []

        for s in samples:
            scenario_counts[s.scenario] = scenario_counts.get(s.scenario, 0) + 1
            all_congestion.append(s.overall_congestion)

        all_cong = np.array(all_congestion)

        print(f"\n{'='*56}")
        print(f"  SYNTHETIC TRAFFIC DATA — GENERATION SUMMARY")
        print(f"{'='*56}")
        print(f"  Total Samples    : {n:,}")
        print(f"  Junctions        : {NUM_JUNCTIONS}  (3x3 grid)")
        print(f"  Features / Sample: 8   [count + speed × 4 dirs]")
        print(f"  Labels  / Sample : 4   [congestion × 4 dirs]")

        print(f"\n  {'─'*52}")
        print(f"  SCENARIO DISTRIBUTION")
        print(f"  {'─'*52}")
        BAR = 25
        for scenario, count in sorted(scenario_counts.items(),
                                      key=lambda x: -x[1]):
            pct     = count / n * 100
            bar_len = int(pct / 100 * BAR)
            bar     = "#" * bar_len + "." * (BAR - bar_len)
            print(f"  {scenario:<12} | {count:>5} ({pct:>5.1f}%)  [{bar}]")

        print(f"\n  {'─'*52}")
        print(f"  CONGESTION STATISTICS (overall, all junctions)")
        print(f"  {'─'*52}")
        print(f"  Mean   : {all_cong.mean():.4f}")
        print(f"  Std    : {all_cong.std():.4f}")
        print(f"  Min    : {all_cong.min():.4f}")
        print(f"  Max    : {all_cong.max():.4f}")
        print(f"  Median : {np.median(all_cong):.4f}")

        # Congestion level buckets
        low  = (all_cong <  0.35).sum()
        med  = ((all_cong >= 0.35) & (all_cong < 0.65)).sum()
        high = (all_cong >= 0.65).sum()
        print(f"\n  {'─'*52}")
        print(f"  CONGESTION LEVEL BUCKETS")
        print(f"  {'─'*52}")
        print(f"  LOW  (< 0.35)  : {low:>5} samples  ({low/n*100:.1f}%)")
        print(f"  MED  (0.35–0.65): {med:>5} samples  ({med/n*100:.1f}%)")
        print(f"  HIGH (> 0.65)  : {high:>5} samples  ({high/n*100:.1f}%)")
        print(f"{'='*56}\n")

    def print_sample_preview(self, samples: List[TrafficSample],
                             n_preview: int = 5) -> None:
        """Prints a human-readable preview of the first n samples."""
        print(f"\n  SAMPLE PREVIEW  (first {n_preview} records)")
        print(f"  {'─'*60}")
        header = (f"  {'#':<4} {'Junction':<10} {'Scenario':<12} "
                  f"{'Counts (N,S,E,W)':<24} {'Cong (N,S,E,W)'}")
        print(header)
        print(f"  {'─'*60}")

        for i, s in enumerate(samples[:n_preview]):
            counts = ",".join(f"{c:>5.0f}" for c in s.vehicle_counts)
            congs  = ",".join(f"{c:.2f}"   for c in s.congestion_scores)
            print(f"  {i+1:<4} J{s.junction_id:<9} {s.scenario:<12} "
                  f"[{counts}]  [{congs}]")
        print(f"  {'─'*60}\n")


# ─────────────────────────────────────────────
#  MAIN — DEMO RUN
# ─────────────────────────────────────────────
def main():
    print("\n" + "="*56)
    print("  Smart Traffic Signal Automation System")
    print("  Module : synthetic_traffic_generator.py")
    print("="*56)

    # ── 1. Print scenario profiles ─────────────
    print("\n  SCENARIO PROFILES LOADED")
    print(f"  {'─'*52}")
    for sc, prof in SCENARIO_PROFILES.items():
        print(f"  [{prof.name:<12}]  weight={prof.weight:.2f}  "
              f"count={prof.count_range}  speed={prof.speed_range}")
        print(f"              → {prof.description}")

    # ── 2. Generate 5,000 samples ──────────────
    print(f"\n  Generating 5,000 samples across all 9 junctions ...")
    gen     = SyntheticTrafficGenerator(seed=RANDOM_SEED)
    samples = gen.generate(n_samples=5_000)

    # ── 3. Summary statistics ──────────────────
    gen.print_summary(samples)

    # ── 4. Preview first 5 raw samples ────────
    gen.print_sample_preview(samples, n_preview=5)

    # ── 5. Export to NumPy ─────────────────────
    X, y = gen.to_numpy(samples)
    print(f"  NumPy Export")
    print(f"  {'─'*40}")
    print(f"  X (features) shape : {X.shape}   dtype={X.dtype}")
    print(f"  y (labels)   shape : {y.shape}   dtype={y.dtype}")
    print(f"  X[0] = {X[0]}")
    print(f"  y[0] = {y[0]}")

    # ── 6. Export to CSV ──────────────────────
    csv_path = "/mnt/user-data/outputs/traffic_data.csv"
    gen.to_csv(samples, filepath=csv_path)
    size_kb = os.path.getsize(csv_path) / 1024
    print(f"\n  CSV Export")
    print(f"  {'─'*40}")
    print(f"  File    : {csv_path}")
    print(f"  Rows    : {len(samples):,}  (+ 1 header)")
    print(f"  Columns : 15")
    print(f"  Size    : {size_kb:.1f} KB")

    # ── 7. Per-junction breakdown ─────────────
    print(f"\n  PER-JUNCTION AVERAGE CONGESTION")
    print(f"  {'─'*40}")
    BAR = 20
    for jid in range(1, NUM_JUNCTIONS + 1):
        j_samples = [s for s in samples if s.junction_id == jid]
        avg       = np.mean([s.overall_congestion for s in j_samples])
        bar_len   = int(avg * BAR)
        bar       = "#" * bar_len + "." * (BAR - bar_len)
        level     = "HIGH" if avg > 0.65 else "MED " if avg > 0.35 else "LOW "
        print(f"  J{jid}  avg={avg:.3f}  [{bar}]  {level}  "
              f"({len(j_samples)} samples)")

    print(f"\n  Done. Data ready for ML training pipeline.\n")


if __name__ == "__main__":
    main()
