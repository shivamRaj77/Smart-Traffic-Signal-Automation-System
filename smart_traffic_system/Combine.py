if __name__ == "__main__":

    # Step 1: Collect traffic data
    traffic_data = TrafficData(vehicle_count=80, average_speed=20.0)

    # Step 2: Analyze congestion
    analyzer = CongestionAnalyzer(low_threshold=2.0, high_threshold=5.0)
    congestion_level = analyzer.analyze_congestion(traffic_data)

    print("Congestion Level:", congestion_level)

    # Step 3: Adjust signal timing
    controller = SignalController(min_green_time=20, max_green_time=60)
    timing = controller.compute_signal_timing(congestion_level)

    # Step 4: Update signal
    controller.update_signal_timing(timing)
