class AnalyticsService:
    def __init__(self, history_repo):
        self.history_repo = history_repo

    def get_profit_over_time(self):
        # Logic to group history by date for a Line Chart
        history = self.history_repo.load_all()
        data = {}
        for entry in history:
            date = entry['timestamp'][:10] # YYYY-MM-DD
            data[date] = data.get(date, 0) + entry['net_profit']
        return data

    def get_inventory_health(self, inventory):
        # Group by shelf life for a Pie/Bar Chart
        health = {"Critical (1-2d)": 0, "Warning (3-5d)": 0, "Fresh (6d+)": 0}
        for b in inventory.batches:
            days = b.estimated_shelf_life_days()
            if days <= 2: health["Critical (1-2d)"] += 1
            elif days <= 5: health["Warning (3-5d)"] += 1
            else: health["Fresh (6d+)"] += 1
        return health