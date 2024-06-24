import logging
from src.utility.utility import DatabaseManager
logging.basicConfig(level=logging.INFO)


class SuspectModel:
    """
    Model to represent child or adult suspect and their information
    """

    __instance = None
    name = None
    dob = None
    nationality = None
    special_considerations = None
    address = None
    email = None
    phone = None
    profiles = None
    screen_names = None
    school = None
    occupation = None
    business_address = None
    relationship_to_victim = None
    additional_info = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(SuspectModel, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

    def is_empty(self) -> bool:
        """
        Is there a suspect
        :return:
        """
        if self.name is None:
            return True
        else:
            return False

    def set_fields(self, name, dob, nationality, special_considerations, address, email, phone, profiles, screen_names, school,
                   occupation, business_address, relationship_to_victim, additional_info) -> None:
        """
        Updates fields with new values
        :return:
        """
        self.name = name
        self.dob = dob
        self.nationality = nationality
        self.special_considerations = special_considerations
        self.address = address
        self.email = email
        self.phone = phone
        self.profiles = profiles
        self.screen_names = screen_names
        self.school = school
        self.occupation = occupation
        self.business_address = business_address
        self.relationship_to_victim = relationship_to_victim
        self.additional_info = additional_info
        logging.info('Updated suspect model with new fields')

    def save(self):
        """
        Saves suspect attributes to the database
        :return:
        """
        logging.info('Attempting to save suspect to DB')
        if not self.name or self.name == "":
            # Requires fields not there
            logging.info("No suspect to save")
        else:
            DatabaseManager().insert_suspect(self.name,
                                             self.dob,
                                             self.nationality,
                                             self.special_considerations,
                                             self.address,
                                             self.email,
                                             self.phone,
                                             self.profiles,
                                             self.screen_names,
                                             self.school,
                                             self.occupation,
                                             self.business_address,
                                             self.relationship_to_victim,
                                             self.additional_info)

    def update(self) -> None:
        """
        Fetch all suspect fields
        :return:
        """
        fields = DatabaseManager().fetch_suspect()
        if not fields is None:
            name = fields[2]
            dob = fields[3]
            nationality = fields[4]
            special_considerations = fields[5]
            address = fields[6]
            email = fields[7]
            phone = fields[8]
            profiles = fields[9]
            screen_names = fields[10]
            school = fields[11]
            occupation = fields[12]
            business_address = fields[13]
            relationship_to_victim = fields[14]
            additional_info = fields[15]

            # Update model with new fields
            self.set_fields(name, dob, nationality, special_considerations, address, email, phone, profiles,
                            screen_names,
                            school,
                            occupation, business_address, relationship_to_victim, additional_info)
        else:
            logging.info("No suspect to update suspect model with")
            self.set_fields(None, None, None, None, None, None, None, None,
                            None,
                            None,
                            None, None, None, None)


class VictimModel:
    """
    Model to represent child victim and their information
    """

    __instance = None
    name = None
    dob = None
    nationality = None
    special_considerations = None
    address = None
    email = None
    phone = None
    profiles = None
    screen_names = None
    school = None
    additional_info = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(VictimModel, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

    def set_fields(self, name, dob, nationality, special_considerations, address, email, phone, profiles, screen_names,
                   school, additional_info) -> None:
        """
        Updates fields with new values
        :param name:
        :param dob:
        :param nationality:
        :param special_considerations:
        :param address:
        :param email:
        :param phone:
        :param profiles:
        :param screen_names:
        :param school:
        :param additional_info:
        :return:
        """
        self.name = name
        self.dob = dob
        self.nationality = nationality
        self.special_considerations = special_considerations
        self.address = address
        self.email = email
        self.phone = phone
        self.profiles = profiles
        self.screen_names = screen_names
        self.school = school
        self.additional_info = additional_info

    def is_empty(self) -> bool:
        """
        Is there a victim
        :return:
        """
        if self.name is None:
            return True
        else:
            return False

    def save(self):
        """
        Saves victim attributes to the database
        :return:
        """
        logging.info("Attempting to save victim to database")
        if not self.name or self.name == "":
            # Requires fields not there
            logging.info("No victim to save")
        else:
            DatabaseManager().insert_victim(self.name,
                                            self.dob,
                                            self.nationality,
                                            self.special_considerations,
                                            self.address,
                                            self.email,
                                            self.phone,
                                            self.profiles,
                                            self.screen_names,
                                            self.school,
                                            self.additional_info)

    def update(self) -> None:
        """
        Fetch all victim fields
        :return:
        """
        fields = DatabaseManager().fetch_victim()
        if not fields is None:
            name = fields[2]
            dob = fields[3]
            nationality = fields[4]
            special_considerations = fields[5]
            address = fields[6]
            email = fields[7]
            phone = fields[8]
            profiles = fields[9]
            screen_names = fields[10]
            school = fields[11]
            additional_info = fields[12]

            # Update model with new fields
            self.set_fields(name, dob, nationality, special_considerations, address, email, phone, profiles,
                            screen_names,
                            school, additional_info)
        else:
            logging.info("No victim to update victim model with")
            self.set_fields(None, None, None, None, None, None, None, None,
                            None,
                            None, None)
