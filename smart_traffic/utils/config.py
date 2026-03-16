"""
Central configuration constants for the application.
In production these would come from environment variables / a secrets manager.
"""

# JWT settings
SECRET_KEY: str = "super-secret-traffic-key-change-in-production"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

# Default admin credentials (created on first startup)
DEFAULT_ADMIN_USERNAME: str = "admin"
DEFAULT_ADMIN_PASSWORD: str = "admin123"

# Traffic simulation constants
JUNCTIONS: list[str] = [f"J{i}" for i in range(1, 10)]
DIRECTIONS: list[str] = ["north", "south", "east", "west"]
BASE_SIGNAL_CYCLE_SECONDS: int = 120
MIN_GREEN_TIME_SECONDS: int = 10

# Logging
MAX_SIMULATION_LOGS: int = 100
