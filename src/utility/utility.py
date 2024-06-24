import binascii
import datetime
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import subprocess
from typing import Tuple, Dict, List
import cv2
import pandas as pd
from PIL import Image, ExifTags
from jsonschema import validate
from jsonschema.exceptions import ValidationError

logging.basicConfig(level=logging.INFO)


class DatabaseManager:
    """
    Utility class for handling all database interactions
    """

    __instance = None
    database_directory = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(DatabaseManager, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

    def check_tables_exist(self) -> bool:
        """
        Checks if all required tables exist in the database
        :return: True if all tables exist, False otherwise
        """
        logging.info('Checking database integrity')
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()
        # List of tables to check
        tables = ["investigators", "cases", "incidents", "evidence", "victims", "suspects", "flags"]
        for table in tables:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone() is None:
                logging.info('Database tables missing or corrupted')
                return False  # Table does not exist
        logging.info('Database tables OK')
        connection.close()
        return True  # All tables exist

    def create_tables(self, case_directory: str) -> None:
        """
        Creates tables with the necessary attributes
        :return:
        """
        self.database_directory = os.path.join(case_directory, "cst.db")
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()
        # SQL commands to create tables
        logging.info('Creating investigators table')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investigators (
                investigator_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                email TEXT
            )
        ''')

        logging.info('Creating cases table')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                case_number INTEGER PRIMARY KEY,
                case_name TEXT,
                referral_source TEXT,
                investigator_id INTEGER,
                is_active INTEGER,
                FOREIGN KEY (investigator_id) REFERENCES investigators (investigator_id)
            )
        ''')

        logging.info('Creating incidents table')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id INTEGER PRIMARY KEY,
                case_number INTEGER,
                type_of_sextortion TEXT,
                threats_made TEXT,
                demands_made TEXT,
                start_date_time TEXT,
                end_date_time TEXT,
                FOREIGN KEY (case_number) REFERENCES cases (case_number)
            )
        ''')

        logging.info('Creating evidence table')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS evidence (
                        evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        case_number INTEGER,
                        file_name TEXT,
                        description TEXT,
                        evidence_type TEXT,
                        hash_value TEXT,
                        exif_data TEXT,
                        FOREIGN KEY (case_number) REFERENCES cases (case_number)
                        
                    )
                ''')

        logging.info('Creating victims table')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS victims (
                        victim_id INTEGER PRIMARY KEY,
                        incident_id INTEGER,
                        name TEXT,
                        dob TEXT,
                        nationality TEXT,
                        special_considerations TEXT,
                        address TEXT,
                        email TEXT,
                        phone TEXT,
                        profiles TEXT,
                        screen_names TEXT,
                        school TEXT,
                        additional_info TEXT,
                        FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
                        
                    )
                ''')

        logging.info('Creating suspects table')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS suspects (
                        suspect_id INTEGER PRIMARY KEY,
                        incident_id INTEGER,
                        name TEXT,
                        dob TEXT,
                        nationality TEXT,
                        special_considerations TEXT,
                        address TEXT,
                        email TEXT,
                        phone TEXT,
                        profiles TEXT,
                        screen_names TEXT,
                        school TEXT,
                        occupation TEXT,
                        business_address TEXT,
                        relationship_to_victim TEXT,
                        additional_info TEXT,
                        FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)

                    )
                ''')

        logging.info('Creating flags table')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS flags (
                        flag_id INTEGER PRIMARY KEY,
                        file_name TEXT,
                        file_type TEXT,
                        flagged_text TEXT
                    )
                ''')

        connection.commit()
        connection.close()

    def insert_case(self, case_number: int, case_name: str, referral_source: str, investigator_id: int) -> None:
        """
        Inserts or replaces new case into database
        :param investigator_id:
        :param case_number:
        :param case_name:
        :param referral_source:
        :return:
        """
        logging.info('Inserting or replacing case in database')
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = '''
                   INSERT OR REPLACE INTO cases (case_number, case_name, referral_source, investigator_id, is_active)
                   VALUES (?, ?, ?, ?, ?)
               '''

        # No current investigator assigned initially, and case set to active
        values = (case_number, case_name, referral_source, investigator_id, 1)

        # Execute insert query
        cursor.execute(query, values)

        # Commit the changes to the database
        connection.commit()
        logging.info('Case saved successfully to database')
        connection.close()

    def insert_incident(self, case_number: int, type_of_sextortion: str, threats_made: str, demands_made: str,
                        start_date_time: str,
                        end_date_time: str) -> None:
        """
        Inserts or replaces incident into database
        :param case_number:
        :param type_of_sextortion:
        :param threats_made:
        :param demands_made:
        :param start_date_time:
        :param end_date_time:
        :return:
        """
        logging.info('Inserting or replacing incident in database')
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = '''
                       INSERT OR REPLACE INTO incidents (incident_id, case_number, type_of_sextortion, threats_made, demands_made, start_date_time, end_date_time)
                       VALUES (1, ?, ?, ?, ?, ?, ?)
                   '''

        values = (case_number, type_of_sextortion, threats_made, demands_made, start_date_time, end_date_time)

        # Execute insert query
        cursor.execute(query, values)

        # Commit the changes to the database
        connection.commit()
        logging.info('Incident saved successfully to database')
        connection.close()

    def insert_investigator(self, first_name: str, last_name: str, phone: str, email: str) -> None:
        """
        Inserts new investigator into database
        :param first_name: investigators first name
        :param last_name: investigators surname
        :param phone: investigators phone number
        :param email: investigators email address
        :return:
        """

        logging.info('Saving investigator to database: {} {}'.format(first_name, last_name))
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = '''
                     INSERT INTO investigators (first_name, last_name, phone, email)
                     VALUES (?, ?, ?, ?)
                 '''

        # Investigator fields
        values = (first_name, last_name, phone, email)

        # Execute insert query
        cursor.execute(query, values)

        # Commit the changes to the database
        connection.commit()
        logging.info('Investigator successfully saved to database: {} {}'.format(first_name, last_name))
        connection.close()

    def insert_suspect(self, name, dob, nationality, special_considerations, address, email, phone, profiles,
                       screen_names, school, occupation, business_address, relationship_to_victim, additional_info):
        """
        Inserts or updates a suspect in the database
        :param name: Suspect's name
        :param dob: Suspect's date of birth
        :param nationality: Suspect's nationality
        :param special_considerations: Suspect's special considerations
        :param address: Suspect's address
        :param email: Suspect's email
        :param phone: Suspect's phone number
        :param profiles: Suspect's profiles
        :param screen_names: Suspect's screen names
        :param school: Suspect's school
        :param occupation: Suspect's occupation
        :param business_address: Suspect's business address
        :param relationship_to_victim: Suspect's relationship to victim
        :param additional_info: Additional information about the suspect
        :return:
        """
        logging.info('Saving or updating suspect in database: {}'.format(name))
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        try:
            # Construct the SQL query
            query = '''
                INSERT OR REPLACE INTO suspects (suspect_id, incident_id, name, dob, nationality, special_considerations, address, email, phone,
                                                 profiles, screen_names, school, occupation, business_address,
                                                 relationship_to_victim, additional_info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            # Values to be inserted or replaced
            values = (
                1, 1, name, dob, nationality, special_considerations, address, email, phone, profiles, screen_names,
                school, occupation, business_address, relationship_to_victim, additional_info)

            # Execute the query
            cursor.execute(query, values)

            # Commit the changes to the database
            connection.commit()
            logging.info('Suspect saved or updated successfully in database: {}'.format(name))

        except sqlite3.Error as e:
            logging.error('Error occurred while inserting or updating suspect: {}'.format(e))

        finally:
            # Close the connection
            connection.close()

    def insert_victim(self, name, dob, nationality, special_considerations, address, email, phone, profiles,
                      screen_names, school, additional_info):
        """
        Insert or update victim in the database
        :param name: Victim's name
        :param dob: Victim's date of birth
        :param nationality: Victim's nationality
        :param special_considerations: Victim's special considerations
        :param address: Victim's address
        :param email: Victim's email
        :param phone: Victim's phone number
        :param profiles: Victim's profiles
        :param screen_names: Victim's screen names
        :param school: Victim's school
        :param additional_info: Additional information about the victim
        :return:
        """
        logging.info('Saving or updating victim in database: {}'.format(name))
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = '''
               INSERT OR REPLACE INTO victims (victim_id, incident_id, name, dob, nationality, special_considerations, address, 
               email, phone, profiles, screen_names, school, additional_info)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           '''
        values = (1, 1, name, dob, nationality, special_considerations, address, email, phone, profiles, screen_names,
                  school, additional_info)
        cursor.execute(query, values)

        # Commit the changes to the database
        connection.commit()
        logging.info('Victim saved or updated successfully in database: {}'.format(name))
        connection.close()

    def insert_evidence(self, case_number, file_name, description, evidence_type, hash_value, exif_data):
        """
        Insert or update victim in the database
        :param case_number: Case number for the case
        :param file_name: name of file
        :param description: any description about the file
        :param evidence_type: whether it's a media or chat log file
        :param hash_value: initial hash computed on upload
        :param exif_data: and extracted exif models
        :return:
        """

        logging.info('Saving evidence to database: {}'.format(file_name))
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = '''
                     INSERT INTO evidence (case_number, file_name, description, evidence_type, hash_value, exif_data)
                     VALUES (?, ?, ?, ?, ?, ?)
                 '''

        # Evidence fields
        values = (case_number, file_name, description, evidence_type, hash_value, exif_data)

        # Execute insert query
        cursor.execute(query, values)

        # Commit the changes to the database
        connection.commit()
        logging.info('Evidence successfully saved to database: {}'.format(file_name))
        connection.close()

    def insert_flag(self, file_name, file_type, flagged_text=None):

        logging.info(f"Saving {file_type} flag from '{file_name}' to database")
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = '''
                         INSERT INTO flags (file_name, file_type, flagged_text)
                         VALUES (?, ?, ?)
                     '''

        # Evidence fields
        values = (file_name, file_type, flagged_text)

        # Execute insert query
        cursor.execute(query, values)

        # Commit the changes to the database
        connection.commit()
        logging.info(f"{file_type} flag from '{file_name}' to successfully saved to database")

        connection.close()

    def fetch_flagged_clogs(self):
        """
        Fetch all flagged clog filenames
        :return:
        """

        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = ''' SELECT DISTINCT file_name FROM flags WHERE file_type = ?'''

        cursor.execute(query, ('clog',))

        result = cursor.fetchall()

        connection.close()
        return result

    def fetch_flag_by_file_name(self, file_name):
        """
        Fetch all flagged clog entries for filename
        :param file_name:
        :return:
        """
        logging.info(f"Fetching all flagged text for file '{file_name}'")
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = ''' SELECT * FROM flags WHERE file_name = ?'''

        cursor.execute(query, (file_name,))

        result = cursor.fetchall()

        connection.close()
        return result

    def fetch_evidence_desc_by_file_name(self, file_name):
        """
        Fetch all evidence descriptions for a filename
        :param file_name:
        :return:
        """
        logging.info(f"Fetching comments for evidence file {file_name}")
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = ''' SELECT description FROM evidence WHERE file_name = ? '''

        cursor.execute(query, (file_name,))

        result = cursor.fetchone()

        connection.close()
        return result

    def fetch_flagged_media_files(self):
        """
        Fetch all flagged media files
        :return:
        """
        logging.info(f"Fetching all flagged media files")
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = ''' SELECT * FROM flags WHERE file_type = ?'''

        cursor.execute(query, ('media',))

        result = cursor.fetchall()

        connection.close()
        return result

    def fetch_evidence_by_type(self, evidence_type: str):
        """
        Get evidence by the evidence type (chat log or media)
        :param evidence_type: chat log or media
        :return: evidence entry tuple
        """
        logging.info(f"Fetching all evidence where evidence type is '{evidence_type}'")
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = ''' SELECT * FROM evidence WHERE evidence_type = ? '''

        cursor.execute(query, (evidence_type,))

        result = cursor.fetchall()  # List of tuples

        connection.close()
        return result

    def fetch_investigator_by_name(self, first_name: str, last_name: str):
        """
        Get investigator by the first and last name
        :param first_name:
        :param last_name:
        :return: tuple for result e.g., (1, 'John', 'Doe', '123-456-7890', 'john.doe@example.com')
        """

        logging.info('Fetching investigator from database by name: {} {}'.format(first_name, last_name))
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = '''
                    SELECT * FROM investigators
                    WHERE first_name = ? AND last_name = ?
                '''

        # Execute the query
        cursor.execute(query, (first_name, last_name))

        # Stores the result as a tuple e.g., (1, 'John', 'Doe', '123-456-7890', 'john.doe@example.com')
        result = cursor.fetchone()

        if result is None:
            logging.error('Investigator was not found in database: {} {}'.format(first_name, last_name))

        else:
            logging.info('Investigator successfully fetched from database: {} {}'.format(first_name, last_name))

        connection.close()

        # Return the tuple
        return result

    def fetch_investigator_by_id(self, investigator_id):
        """
        Get investigator by their ID
        :param investigator_id: ID of the investigator
        :return: Tuple representing the investigator's details, e.g., (1, 'John', 'Doe', '123-456-7890', 'john.doe@example.com')
        """
        logging.info('Fetching investigator from database by ID: {}'.format(investigator_id))
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = '''
            SELECT * FROM investigators
            WHERE investigator_id = ?
        '''

        # Execute the query
        cursor.execute(query, (investigator_id,))

        # Fetch the result as a tuple
        result = cursor.fetchone()

        if result is None:
            logging.error('Investigator with ID {} not found in database'.format(investigator_id))
        else:
            logging.info('Investigator successfully fetched from database: {}'.format(result))

        connection.close()

        return result

    def fetch_all_investigators(self) -> [Tuple]:
        """
        Get all investigators in the investigators table
        :return:
        """

        logging.info('Fetching all investigators in the investigators table')
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = ''' SELECT * FROM investigators'''

        cursor.execute(query)

        result = cursor.fetchall()  # List of tuples

        if result is None:
            logging.error('Investigators table empty')

        else:
            logging.info('Investigators successfully fetched from the investigators table')

        connection.close()
        return result

    def fetch_evidence_filename_hash(self) -> [Dict[str, str]]:
        """
        Fetch filenames and corresponding hashes
        :return: list of dictionaries for filename hash mappings
        """

        logging.info('Fetching all filename hash mappings from evidence table')
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query
        query = ''' SELECT file_name, hash_value FROM evidence'''

        cursor.execute(query)

        result = cursor.fetchall()  # List of tuples

        filename_hash_list = []  # List to store dictionaries

        # Convert each tuple into a dictionary and add to the list
        for row in result:
            filename, hash_value = row
            filename_hash_list.append({"file_name": filename, "hash_value": hash_value})

        connection.close()
        return filename_hash_list

    def fetch_suspect(self) -> Tuple:
        """
        Fetch suspect fields
        :return:
        """
        logging.info('Fetching suspect from database')
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query - only ever 1 suspect
        query = '''SELECT * FROM suspects
                   WHERE suspect_id = 1'''

        cursor.execute(query)

        result = cursor.fetchone()

        if result is None:
            logging.error('No suspect found in the database')

        else:
            logging.info('Suspect fetched successfully from the database')

        return result

    def fetch_victim(self):
        """
        Fetch victim fields
        :return:
        """
        logging.info('Fetching victim from database')
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query - only ever 1 victim
        query = '''SELECT * FROM victims
                   WHERE victim_id = 1'''

        cursor.execute(query)

        result = cursor.fetchone()

        if result is None:
            logging.error('No victim found in the database')

        else:
            logging.info('Victim fetched successfully from the database')

        return result

    def fetch_incident(self):
        """
        Fetch incident fields
        :return:
        """
        logging.info('Fetching incident from database')
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query - only ever 1 incident
        query = '''SELECT * FROM incidents
                      WHERE incident_id = 1'''

        cursor.execute(query)

        result = cursor.fetchone()

        if result is None:
            logging.error('No incident found in the database')

        else:
            logging.info('Incident fetched successfully from the database')

        return result

    def delete_media_flag(self, media_file):
        """
        Deletes media flag with certain filename
        :param media_file:
        :return:
        """

        logging.info(f"Deleting media file '{media_file}' from flags table in database")
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query to delete the entry
        query = '''DELETE FROM flags WHERE file_type = ? AND file_name = ?'''

        # Execute the query
        cursor.execute(query, ('media', media_file))

        # Commit the transaction
        connection.commit()

        # Close the connection
        connection.close()

    def delete_clog_text_flag(self, clog_file, flag_text):
        """
        Deletes CLog flag with certain filename and flagged text
        :param clog_file:
        :param flag_text:
        :return:
        """
        logging.info(f"Deleting CLog flag '{flag_text}' in '{clog_file}' from flags table in database")
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query to delete the entry
        query = '''DELETE FROM flags WHERE file_type = ? AND file_name = ? AND flagged_text = ?'''

        # Execute the query
        cursor.execute(query, ('clog', clog_file, flag_text))

        # Commit the transaction
        connection.commit()

        # Close the connection
        connection.close()

    def fetch_case(self):
        """
        Fetch case fields
        :return:
        """
        logging.info('Fetching case from database')
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Construct the SQL query - only ever 1 case
        query = '''SELECT * FROM cases LIMIT 1'''

        cursor.execute(query)

        result = cursor.fetchone()

        if result is None:
            logging.error('No case found in the database')

        else:
            logging.info('Case fetched successfully from the database')

        return result

    def fetch_current_investigator_name(self) -> str:
        """
        Fetches the full name of the current investigator
        :return:
        """
        current_id = self.fetch_case()[3]
        current = self.fetch_investigator_by_id(current_id)
        full_name = f"{current[1]} {current[2]}"
        logging.info("Fetched current investigator name: {}".format(full_name))

        return full_name

    def update_evidence_description(self, file_name, comments):
        """
        Updates evidence description
        :param file_name: file name to update description for
        :param comments: comments to add to description
        :return:
        """
        logging.info(f"Updating description for evidence with file name '{file_name}' with description '{comments}'")

        # Connect to the database
        connection = sqlite3.connect(self.database_directory)
        cursor = connection.cursor()

        # Execute the SQL update statement
        query = '''
            UPDATE evidence
            SET description = ?
            WHERE file_name = ?
        '''
        cursor.execute(query, (comments, file_name))
        connection.commit()
        logging.info(f"{file_name} description updated successfully with {comments}")

        connection.close()


class FileManager:
    """
    Utility class for all file operations
    """

    __instance = None
    case_directory = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(FileManager, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

    def setup_directories(self, case_directory):
        """
        Setup the case directories
        :param case_directory:
        :return:
        """
        self.case_directory = case_directory
        self.create_directories()

    def create_directories(self) -> None:
        """
        Creates file structure for a case
        :return:
        """
        # Create case directory if it doesn't exist
        if not os.path.exists(self.case_directory):
            os.makedirs(self.case_directory)

        # Create evidence directory and subdirectories
        evidence_directory = os.path.join(self.case_directory, 'evidence')
        os.makedirs(evidence_directory)
        evidence_chatlog_directory = os.path.join(evidence_directory, 'chatlogs')
        os.makedirs(evidence_chatlog_directory)
        evidence_media_directory = os.path.join(evidence_directory, 'media')
        os.makedirs(evidence_media_directory)

        # Create reports directory and subdirectories
        report_directory = os.path.join(self.case_directory, 'reports')
        os.makedirs(report_directory)

    @staticmethod
    def move_file(file_path: str, destination_dir: str) -> None:
        """
        Moves file to destination directory
        :param file_path: file to move
        :param destination_dir: destination to move file to
        :return:
        """

        # If for some reason destination directory doesn't exist, create it
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        try:
            # Try moving file to destination directory
            shutil.move(file_path, destination_dir)
            logging.info("Moved file {} to directory {}".format(file_path, destination_dir))
        except FileNotFoundError as e:
            logging.error("Error: File not found - {}".format(e))
        except shutil.Error as e:
            logging.error("Error: moving file - {}".format(e))

    def write_to_activity_log(self, entry: str) -> None:
        """
        Creates new CoC log if one doesn't exist
        Writes to CoC log
        :return:
        """
        log_file_path = os.path.join(self.case_directory, 'reports', 'ActivityLog.txt')
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{entry}\n")

    @staticmethod
    def compute_md5_hash(file_path: str) -> str:
        """
        Computes MD5 hash of a file at specified file path
        :param file_path: file to compute MD5 hash of
        :return: MD5 hash
        """
        logging.info("Computing MD5 hash for {}".format(file_path))

        # Make MD5 hash object
        md5_hash = hashlib.md5()

        # Open file in binary moad and read in chunks
        with open(file_path, "rb") as f:
            # Read file in chunks of 4096 bytes to make more memory efficient
            for chunk in iter(lambda: f.read(4096), b""):
                # Update hash with the next chunk
                md5_hash.update(chunk)

        return md5_hash.hexdigest()

    def compute_md5_hashes_in_directory(self, target_dir: str) -> List[Dict[str, str]]:
        """
        Compute MD5 hashes for files in a given directory.
        :param target_dir: The target directory to compute hashes of.
        :return: List of dictionaries containing filename:hash pairs.
        """

        logging.info("Computing hashes in directory: {}".format(target_dir))

        file_hashes = []

        # Check if the directory exists
        if os.path.isdir(target_dir):
            # Iterate over each file in the directory
            for filename in os.listdir(target_dir):
                # Skip hidden files or directories (those starting with a dot)
                if not filename.startswith('.'):
                    file_path = os.path.join(target_dir, filename)
                    # Check if it's a file
                    if os.path.isfile(file_path):
                        # Compute MD5 hash
                        hash_value = self.compute_md5_hash(file_path)
                        # Add filename and hash to the list
                        file_hashes.append({"file_name": filename, "hash_value": hash_value})
        else:
            logging.error("Directory was not found: {}".format(target_dir))

        return file_hashes

    @staticmethod
    def parse_insta_json(file_path: str) -> pd.DataFrame:
        """
        Parses Instagram JSON chat log file into Pandas DataFrame
        :param file_path: Instagram JSON file to parse
        :return: Pandas DataFrame version of the chat log
        """
        # Open JSON file at file_path
        with open(file_path) as file:
            data = json.load(file)

        # Flip order of messages
        messages = data['messages'][::-1]

        # Initialise lists
        timestamps = []
        senders = []
        contents = []

        # Iterate through messages and add to lists
        for message in messages:
            # Encode sender and content to latin1 then to utf8 to avoid 'mojibake'
            timestamp = datetime.datetime.fromtimestamp(message['timestamp_ms'] / 1000).strftime('%H:%M %Y-%m-%d')
            sender = message['sender_name'].encode('latin1').decode('utf8')
            content = message['content'].encode('latin1').decode('utf8')

            # Separate into lists
            timestamps.append(timestamp)
            senders.append(sender)
            contents.append(content)

        # Combine lists into DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'sender': senders,
            'message': contents
        })

        return df

    @staticmethod
    def parse_snap_json(file_path: str) -> [(str, pd.DataFrame)]:
        """
        Parses snapchat JSON chat log file into Pandas DataFrame
        :param file_path: Snapchat JSON file to parse
        :return: [(name of other sender, Pandas DF for conversation),...]
        """
        # Open JSON file at file_path
        with open(file_path) as file:
            data = json.load(file)

        # Initialise list to hold DataFrames
        dfs = []

        # Iterate over sender names
        for sender_name, messages in data.items():
            # Initialize lists to store data
            timestamps = []
            senders = []
            contents = []

            # Flip order of messages for each sender
            messages = messages[::-1]
            # Iterate through messages of each sender
            for message in messages:

                # Skip if Null message
                if message is None:
                    return

                # Get timestamp, sender and message content from message line
                timestamp = message['Created(microseconds)']
                sender = message['From']
                content = message['Content']

                # If each field isn't null then format as required
                if timestamp is not None:
                    timestamp = datetime.datetime.fromtimestamp(timestamp / 1000).strftime(
                        '%H:%M %Y-%m-%d')
                if sender is not None:
                    sender = sender.encode('latin1', 'ignore').decode('utf8')
                if content is not None:
                    content = content.encode('latin1', 'ignore').decode('utf8')

                # Add data to lists
                timestamps.append(timestamp)
                senders.append(sender)
                contents.append(content)

            # Combine lists into Pandas DataFrame
            df = pd.DataFrame({
                'timestamp': timestamps,
                'sender': senders,
                'message': contents
            })

            # Where there is no message drop the row
            df = df[(df['message'] != "") & (df['message'].notna())]

            # If the df has entries then add to dfs
            if not df.empty:
                dfs.append((sender_name, df))

        return dfs

    @staticmethod
    def parse_txt_file(file_path: str) -> str:
        """
        Gets contents of txt file
        :param file_path:
        :return:
        """
        with open(file_path, 'r') as file:
            file_contents = file.read()
        return file_contents

    def validate_clog(self, file_path: str) -> str:
        """
        Validates CLog file to determine type of CLog
        If a valid CLog parses as appropriate format
        :param file_path: path to CLog
        :return: True if parsing successful, False if unsuccessful
        """
        logging.info(f"Attempting to parse file at {file_path}")

        file_extension = os.path.splitext(file_path)[1]

        if file_extension == ".json":
            with open(file_path) as file:
                try:
                    data = json.load(file, strict=False)
                except Exception as e:
                    logging.error(e)
                    return 'invalid-json'
                if self.valid_instagram_json(data):
                    return 'instagram-json'
                elif self.valid_snapchat_json(data):
                    return 'snapchat-json'
                else:
                    return 'invalid-json'
        elif file_extension == ".txt":
            # This may range in formatting so there's no one-size-fits-all
            return 'plaintext'
        else:
            return 'invalid'

    @staticmethod
    def valid_instagram_json(json_data) -> bool:
        """
        Validate CLog file against Instagram JSON schema
        :param json_data: JSON data to validate
        :return: True if validation successful, False otherwise
        """
        with open(os.path.join(os.path.dirname(__file__), 'schemas', 'insta-chatlog-schema.json')) as file:
            schema = json.load(file)
        try:
            validate(instance=json_data, schema=schema)
            logging.info(f"Validation Successful: File is a valid Instagram JSON CLog")
            return True
        except ValidationError as e:
            logging.error(f"Validation Failed: {e}")
            return False

    @staticmethod
    def valid_snapchat_json(json_data) -> bool:
        """
        Validate CLog file against Snapchat JSON schema
        :param json_data: JSON data to validate
        :return: True if validation successful, False otherwise
        """
        with open(os.path.join(os.path.dirname(__file__), 'schemas', 'snap-chatlog-schema.json')) as file:
            schema = json.load(file)
        try:
            validate(instance=json_data, schema=schema)
            logging.info(f"Validation Successful: File is a valid Snapchat JSON CLog")
            return True
        except ValidationError as e:
            logging.error(f"Validation Failed: {e}")
            return False

    @staticmethod
    def generate_thumbnail(video_file, width, height):
        """
        Generates thumbnail for video file
        :param video_file:
        :param width:
        :param height:
        :return:
        """
        # Open the video file
        cap = cv2.VideoCapture(video_file)

        # Read the first frame
        ret, frame = cap.read()

        # Resize the frame
        frame = cv2.resize(frame, (width, height))

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to PIL Image
        img = Image.fromarray(frame_rgb)

        # Close the video file
        cap.release()

        return img

    @staticmethod
    def extract_hex(file_path: str, bytes_per_line=16) -> str:
        """
        Extract hex from file with hex to left of string and plaintext to the right
        :param file_path:
        :param bytes_per_line:
        :return:
        """
        hex_view = []
        ascii_view = []
        byte_count = 0
        line_hex = []
        line_ascii = []

        with open(file_path, 'rb') as file:
            # Read binary data from the file
            while True:
                byte = file.read(1)
                if not byte:
                    break
                byte_hex = binascii.hexlify(byte).decode('utf-8').upper()
                line_hex.append(byte_hex)
                byte_ascii = chr(byte[0]) if 32 <= byte[0] <= 126 else '.'
                line_ascii.append(byte_ascii)
                byte_count += 1
                if byte_count % bytes_per_line == 0:
                    hex_view.append(' '.join(line_hex))
                    ascii_view.append(''.join(line_ascii))
                    line_hex = []
                    line_ascii = []

        # Format hexadecimal and ASCII views as strings
        hex_string = '\n'.join(hex_view)
        ascii_string = '\n'.join(ascii_view)

        # Combine the hex and ASCII strings side by side
        combined_string = "\n".join(
            ["{:48} {}".format(hex_line, ascii_line) for hex_line, ascii_line in zip(hex_view, ascii_view)])

        return combined_string

    @staticmethod
    def extract_exif(file_path) -> str:
        """
        Extracts EXIF data from an image file.
        :param file_path: Path to the image file.
        :return: String containing EXIF data or 'no exif found'.
        """
        try:
            # Open the image
            img = Image.open(file_path)
            exif_data = img.getexif()

            if exif_data:
                # EXIF data exists
                exif_string = ""
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_string += f"{tag}: {value}\n"
                return exif_string
            else:
                # No EXIF data found
                logging.info(f"No EXIF data was found for: {file_path}")
                return "no exif found"
        except Exception as e:
            # Exception occurred
            logging.error(f"Failed to extract EXIF from media: {str(e)}")
            return "no exif found"

    @staticmethod
    def extract_metadata(file_path) -> str:
        """
        Extracts detailed metadata from file
        :param file_path:
        :return:
        """
        try:
            cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            metadata = json.loads(result.stdout)

            # Extract relevant metadata
            video_info = metadata.get("streams", [])[0]
            format_info = metadata.get("format", {})

            # Format metadata into separate lines
            metadata_str = f"Media Metadata:\n"
            for key, value in video_info.items():
                metadata_str += f"{key}: {value}\n"

            metadata_str += f"\nFormat Metadata:\n"
            for key, value in format_info.items():
                metadata_str += f"{key}: {value}\n"

            return metadata_str
        except Exception as e:
            # Exception occurred
            logging.error(f"Failed to extract metadata from media: {str(e)}")
            return "no metadata found"
