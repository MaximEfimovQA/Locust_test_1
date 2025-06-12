from locust import LoadTestShape
from config.config import cfg, logger


class CustomLoadShape(LoadTestShape):
    """
        Здесь должны быть описаны типы нагрузки с помощью stages
    """
    match cfg.loadshape_type:
        case 'baseline':
            stages = [
                {'duration': 50, 'users':10, 'spawn_rate': 1}
            ]
        case 'fixeload':
            stages = [
                {'duration': 300, 'users': 10, 'spawn_rate': 2}
            ]
        case 'stages':
            stages = [
                {'duration': 600, 'users': 5, 'spawn_rate': 1},
                {'duration': 600, 'users': 10, 'spawn_rate': 1},
                {'duration': 600, 'users': 15, 'spawn_rate': 1},
                {'duration': 600, 'users': 20, 'spawn_rate': 1},
                {'duration': 600, 'users': 25, 'spawn_rate': 1},
            ]

    def tick(self):
        run_time = self.get_run_time()
        cumulative_time = 0  # Накопленное время всех предыдущих ступеней

        for stage in self.stages:
            cumulative_time += stage["duration"]
            if run_time < cumulative_time:  # Сравниваем с накопленным временем
                return (stage["users"], stage["spawn_rate"])

        return None