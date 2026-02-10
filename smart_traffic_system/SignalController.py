class SignalController:
    def __init__(self, min_green_time: int, max_green_time: int):
        self.min_green_time = min_green_time
        self.max_green_time = max_green_time
        self.current_mode = "NORMAL"

    def compute_signal_timing(self, congestion_level: str) -> int:

        if congestion_level == "LOW":
            self.current_mode = "LIGHT_TRAFFIC"
            return self.min_green_time

        elif congestion_level == "MEDIUM":
            self.current_mode = "MODERATE_TRAFFIC"
            return (self.min_green_time + self.max_green_time) // 2

        elif congestion_level == "HIGH":
            self.current_mode = "HEAVY_TRAFFIC"
            return self.max_green_time

        else:
            self.current_mode = "NORMAL"
            return self.min_green_time

    def update_signal_timing(self, time: int):
        print(f"Signal updated to green time: {time} seconds")
        print(f"Current Mode: {self.current_mode}")
