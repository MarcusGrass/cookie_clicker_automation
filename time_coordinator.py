from datetime import datetime, timedelta


class TimeCoordinator(object):
    def __init__(self):
        self.last_save_time = datetime.now()
        self.last_garden_plant_time = datetime.now() - timedelta(seconds=4*3600 + 1)
        self.last_economy_report = datetime.now() - timedelta(seconds=301)

    def time_to_save(self):
        if (datetime.now() - self.last_save_time).seconds > 300:
            return True
        return False

    def time_to_plant_seeds(self):
        if (datetime.now() - self.last_garden_plant_time).seconds > 4*3600:
            return True
        return False

    def time_to_log_economy(self):
        if (datetime.now() - self.last_economy_report).seconds > 300:
            return True
        return False


if __name__ == "__main__":
    pass
