from abc import ABC, abstractmethod
from typing import Dict, Any

class StatisticsServiceInterface(ABC):
    @abstractmethod
    def get_dashboard_stats(self) -> Dict[str, Any]:
        pass