import logging
from src.utility.utility import DatabaseManager
logging.basicConfig(level=logging.INFO)


class IncidentModel:
    """
    Model responsible for storing all Incident related information.
    """
    __instance = None
    type_of_sextortion = None
    threats_made = None
    demands_made = None
    start_date_time = None
    end_date_time = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(IncidentModel, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

    def save(self, case_number):
        """
        Saves incident to local database
        :return:
        """
        DatabaseManager().insert_incident(case_number,
                                          self.type_of_sextortion,
                                          self.threats_made,
                                          self.demands_made,
                                          self.start_date_time,
                                          self.end_date_time)

    def set_fields(self, type_of_sextortion, threats_made, demands_made, start_date_time, end_date_time):
        """
        Sets the fields of the incident
        :return:
        """
        logging.info('Setting incident fields: type_of_sextortion={}, '
                     'threats_made={}, demands_made={}, start_date_time={}, end_date_time={}'
                     .format(type_of_sextortion, threats_made, demands_made, start_date_time, end_date_time))

        self.type_of_sextortion = type_of_sextortion
        self.threats_made = threats_made
        self.demands_made = demands_made
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time

    def update(self) -> None:
        """
        Fetch incident fields from the database
        :return:
        """
        fields = DatabaseManager().fetch_incident()
        if not fields is None:
            type_of_sextortion = fields[2]
            threats_made = fields[3]
            demands_made = fields[4]
            start_date_time = fields[5]
            end_date_time = fields[6]

            self.set_fields(type_of_sextortion, threats_made, demands_made, start_date_time,
                            end_date_time)
        else:
            logging.info("No incident to update incident model with")
            self.set_fields(None, None, None, None,
                            None)
