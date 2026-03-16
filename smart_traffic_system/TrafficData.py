from datetime import datetime


class TrafficData:
    def __init__(self, vehicle_count: int, average_speed: float):
        self.vehicle_count = vehicle_count
        self.average_speed = average_speed
        self.timestamp = datetime.now()

    def calculate_density(self) -> float:
        """
        Density is a simple metric:
        higher vehicle count + lower speed = higher congestion
        """
        if self.average_speed == 0:
            return float('inf')

        return self.vehicle_count / self.average_speed

    def get_traffic_metrics(self) -> dict:
        return {
            "vehicle_count": self.vehicle_count,
            "average_speed": self.average_speed,
            "density": self.calculate_density(),
            "timestamp": self.timestamp
        }
