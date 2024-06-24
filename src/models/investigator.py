from src.utility.utility import DatabaseManager


class InvestigatorModel:
    """
    Model responsible for storing investigator information
    """
    def __init__(self, first_name, last_name, phone, email):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email

    def save(self):
        DatabaseManager().insert_investigator(first_name=self.first_name,
                                              last_name=self.last_name,
                                              phone=self.phone,
                                              email=self.email)











