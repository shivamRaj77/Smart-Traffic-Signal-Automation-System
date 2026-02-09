class CongestionAnalyzer:
    def __init__(self, low_threshold: float, high_threshold: float):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def analyze_congestion(self, data: TrafficData) -> str:
        density = data.calculate_density()

        if density < self.low_threshold:
            return "LOW"
        elif self.low_threshold <= density < self.high_threshold:
            return "MEDIUM"
        else:
            return "HIGH"
