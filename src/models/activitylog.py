import datetime
from src.utility.utility import FileManager


class ActivityLogModel:
    """
    Model responsible for handling formatting and entries into the automated Activity Log.
    """

    __instance = None
    controller = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(ActivityLogModel, cls).__new__(cls)

        return cls.__instance

    def __init__(self):
        pass

    def insert(self, activity: str) -> None:
        """
        Inserts entry into log
        :param activity:
        :return:
        """

        if FileManager().case_directory is None:
            return

        # Get the current time
        current_time = datetime.datetime.now()

        # String timestamp in format HH:MM YYYY-MM-DD
        timestamp = current_time.strftime("%H:%M %Y-%m-%d")

        # Write to the file
        FileManager().write_to_activity_log(f"{timestamp} {activity}")

        # Updates preservation view via preservation controller
        self.controller.update_activity_log_view()
