from src.utility.utility import DatabaseManager


class EvidenceModel:
    """
    Model responsible for storing information regarding evidence stored in the evidence directories
    """

    def __init__(self, case_number=None, file_name=None, description=None, evidence_type=None,
                 hash_value=None, exif_data=None):
        self.case_number = case_number
        self.file_name = file_name
        self.description = description
        self.evidence_type = evidence_type
        self.hash_value = hash_value
        self.exif_data = exif_data

    def save(self) -> None:
        """
        Saves to db
        :return:
        """
        DatabaseManager().insert_evidence(case_number=self.case_number,
                                          file_name=self.file_name,
                                          description=self.description,
                                          evidence_type=self.evidence_type,
                                          hash_value=self.hash_value,
                                          exif_data=self.exif_data)
