import logging
from src.utility.utility import DatabaseManager
logging.basicConfig(level=logging.INFO)


class CaseModel:
    """
    Model responsible for storing main information about the case.
    """

    __instance = None
    case_number = None
    case_name = None
    referral_source = None
    investigator_id = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(CaseModel, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

    def set_fields(self, case_number, case_name, referral_source, investigator_id):
        """
        Update case fields
        :param case_number:
        :param case_name:
        :param referral_source:
        :param investigator_id:
        :return:
        """
        self.case_number = case_number
        self.case_name = case_name
        self.referral_source = referral_source
        self.investigator_id = investigator_id

    def save(self):
        """
        Save case attributes to database
        :return:
        """
        DatabaseManager().insert_case(self.case_number, self.case_name, self.referral_source, self.investigator_id)

    def update(self) -> None:
        """
        Fetch case fields from the database
        :return:
        """
        fields = DatabaseManager().fetch_case()
        logging.info(fields)
        if not fields is None:
            case_number = fields[0]
            case_name = fields[1]
            referral_source = fields[2]
            investigator_id = fields[3]

            self.set_fields(case_number, case_name, referral_source, investigator_id)
        else:
            logging.info("No case to update case model with")
            self.set_fields(None, None, None, None)
