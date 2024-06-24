import logging
from src.utility.utility import DatabaseManager
logging.basicConfig(level=logging.INFO)


class FlagManager:
    """
    Model for managing flagged media and CLog files
    """

    __instance = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(FlagManager, cls).__new__(cls)

        return cls.__instance

    def __init__(self):
        pass

    @staticmethod
    def flag_text(clog_file: str, flagged_text: str) -> None:
        """
        Stores flagged text for clog in db
        :param clog_file:
        :param flagged_text:
        :return:
        """
        logging.info(f"Flagged text {flagged_text} in {clog_file}")
        DatabaseManager().insert_flag(file_name=clog_file,
                                      file_type='clog',
                                      flagged_text=flagged_text)

    @staticmethod
    def flag_media(media_file: str) -> None:
        """
        Stores media file flag in db
        :param media_file:
        :return:
        """
        logging.info(f"Flagged media file {media_file}")
        DatabaseManager().insert_flag(file_name=media_file,
                                      file_type='media')

    @staticmethod
    def load_flagged_clogs() -> [str]:
        """
        Loads CLog files that have had text flagged in
        :return:
        """
        flagged_clog_filenames = DatabaseManager().fetch_flagged_clogs()
        return flagged_clog_filenames

    @staticmethod
    def load_flagged_text(clog_file: str) -> [str]:
        """
        Load flagged text for a specific chat log
        :param clog_file: CLog file to get flagged text for
        :return list of flagged text from the chat log
        """
        logging.info(f"Loading flagged text from {clog_file}")
        # Ensure clog_file is passed as a tuple if not already a tuple
        if not isinstance(clog_file, tuple):
            clog_file = (clog_file,)
        clog_flag_tuples = DatabaseManager().fetch_flag_by_file_name(*clog_file)  # Unpack tuple
        flagged_texts = [clog_flag_tuple[3] for clog_flag_tuple in clog_flag_tuples]
        return flagged_texts

    @staticmethod
    def load_flagged_media_files() -> [str]:
        """
        Load all flagged media file names
        :return:
        """
        flagged_media_files = DatabaseManager().fetch_flagged_media_files()
        flagged_media_files = [clog_flag_tuple[1] for clog_flag_tuple in flagged_media_files]
        logging.info(f"Loaded flagged media files: {flagged_media_files}")
        return flagged_media_files

    @staticmethod
    def delete_media_file_flag(media_file_name: str) -> None:
        """
        Deletes media file flag
        :param media_file_name: media file to delete flag for
        :return:
        """
        DatabaseManager().delete_media_flag(media_file=media_file_name)
        logging.info(f"Flag for media file '{media_file_name}' was successfully deleted")

    @staticmethod
    def delete_clog_text_flag(clog_file, flag_text):
        """
        Deletes text flag for clog file
        :param clog_file:
        :param flag_text:
        :return:
        """
        DatabaseManager().delete_clog_text_flag(clog_file=clog_file,
                                                flag_text=flag_text)
        logging.info(f"Flag '{flag_text}'for clog file '{clog_file}' was successfully deleted")