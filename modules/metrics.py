import threading
from datetime import datetime
from typing import Dict, Union

class MetricsRegistry:
    """
    Thread-safe registry for Application Performance Monitoring (APM).
    """
    def __init__(self):
        self._lock = threading.Lock()
        self.start_time = datetime.now()
        self._counts: Dict[str, int] = {
            "build_requests": 0,
            "roll_success": 0,
            "roll_failed": 0
        }

    def increment(self, metric: str) -> None:
        """Safely increments a counter."""
        with self._lock:
            if metric in self._counts:
                self._counts[metric] += 1

    def get_report(self) -> Dict[str, Union[int, float]]:
        """Calculates and returns a snapshot of system health."""
        with self._lock:
            # Calculation logic for success_rate...
            return self._counts.copy()

metrics = MetricsRegistry()
