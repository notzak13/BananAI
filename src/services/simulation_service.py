from src.services.statistics_service import StatisticsService
from src.services.economics_service import EconomicsService


class SimulationService:


    @staticmethod
    def simulate(batch, quantity: int) -> dict:
        stats = StatisticsService.batch_statistics(batch)
        economics = EconomicsService.estimate(batch, quantity)

        return {
            "quantity": quantity,
            "statistics": stats,
            "economics": economics,
            "ripeness_distribution": batch.ripeness_distribution(),
            "estimated_shelf_life_days": batch.estimated_shelf_life_days(),
        }
