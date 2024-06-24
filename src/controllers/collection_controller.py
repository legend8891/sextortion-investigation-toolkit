import logging
import mimetypes
import os
from asyncio import Event
from tkinter import filedialog, messagebox
from src.models.activitylog import ActivityLogModel
from src.models.case import CaseModel
from src.models.evidence import EvidenceModel
from src.utility.utility import DatabaseManager, FileManager
from src.views.collection_view import CollectionView

logging.basicConfig(level=logging.INFO)


class CollectionController:
    """
    Controller for the Collection tab
    """

    def __init__(self, view: CollectionView) -> None:
        # Collection view
        self.view = view

        # Bindings to view
        self.view.file_upload_button.configure(command=self.upload_file)
        self.view.export_hashes_button.configure(command=self.export_hashes)

    def upload_file(self, event: Event = None) -> None:
        """
        Logic for handling file upload
        :param event:
        :return:
        """
        logging.info("Opening file upload dialog")

        # Allowed file types
        file_whitelist = [
            # Chat log files
            ("Text files", "*.txt"),
            ("JSON files", "*.json"),
            # Image files
            ("JPG files", "*.jpg"),
            ("JPEG files", "*.jpeg"),
            ("PNG files", "*.png"),
            ("GIF files", "*.gif"),
            ("BMP files", "*.bmp"),
            # Video files
            ("MP4 files", "*.mp4"),
            ("MOV files", "*.mov"),
            ("AVI files", "*.avi"),
            ("MKV files", "*.mkv"),
        ]

        # Ask user for files
        file_paths = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=file_whitelist
        )

        # Iterate through files and save
        if file_paths:
            for file_path in file_paths:
                logging.info(f"Uploading file: {file_path}")

                # Check no mismatch between expected MIME and true MIME types
                if self.mime_extension_mismatch(file_path):
                    messagebox.showerror('Error', 'Mismatch between file extension and MIME type detected for '
                                                  'file: {}. Upload has been skipped for this file'.format(file_path))
                    continue  # Skip to the next file if there's a MIME type mismatch

                # Check if file with the same name already exists in the evidence table
                existing_files = [entry['file_name'] for entry in DatabaseManager().fetch_evidence_filename_hash()]
                if os.path.basename(file_path) in existing_files:
                    logging.info(f"File '{file_path}' already exists, skipping upload")
                    messagebox.showerror('Error',
                                         'File with the same name already exists. Upload has been skipped '
                                         'for this file. If you wish to add this file too then rename it and try '
                                         'again.')
                    continue  # Skip to the next file if the file already exists in the database

                # Move file to appropriate evidence folder
                destination_dir = self.move_file(file_path)

                # Compute MD5 hash of file
                new_file_path = f"{destination_dir}/{os.path.basename(file_path)}"
                md5_hash = FileManager().compute_md5_hash(new_file_path)
                logging.info("MD5 Hash computed for {}: {}".format(file_path, md5_hash))

                # Store file details in db
                self.save_evidence_to_db(os.path.basename(file_path), destination_dir, md5_hash)

                # Update evidence viewer
                self.update_evidence_view_box()

                # Log activity
                (ActivityLogModel().
                 insert(f"New file uploaded '{new_file_path}'"))

    @staticmethod
    def mime_extension_mismatch(file_path: str) -> bool:
        """
        Compares file extension and MIME type to check for a mismatch
        :param file_path: file path to check
        :return: true if mismatch, false otherwise
        """

        # Get mime type of file
        mime_type = mimetypes.guess_type(file_path)[0]
        expected_mime_type, _ = mimetypes.guess_type(file_path, strict=False)

        # Check if MIME type matches expected MIME type
        if mime_type and expected_mime_type:
            if mime_type != expected_mime_type:
                logging.info(
                    "Mismatch between true MIME type {} and expected MIME type {} for file: {}".
                    format(mime_type, expected_mime_type, file_path))
                return True
            else:
                logging.info("True MIME type matches expected MIME type for file: {}".format(file_path))
                return False
        else:
            logging.info("Unable to determine MIME type or file extension for file: {}".format(file_path))
            return True

    @staticmethod
    def move_file(file_path: str):
        """
        Logic for moving uploaded file to correct evidence folder
        :param file_path:
        :return:
        """

        # Where case is stored
        case_directory = FileManager().case_directory

        # Define evidence folders
        evidence_media_dir = os.path.join(case_directory, "evidence", "media")
        evidence_chatlogs_dir = os.path.join(case_directory, "evidence", "chatlogs")

        # Define which files are chatlogs and which are media
        chatlog_filetypes = [".txt", ".json"]
        # Images and videos
        media_filetypes = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp4", ".mov", ".avi", ".mkv"]

        # Check file extension
        _, file_extension = os.path.splitext(file_path)

        # Get destination directory based on extension
        if file_extension.lower() in chatlog_filetypes:
            # Move to evidence/chatlogs folder
            FileManager().move_file(file_path, evidence_chatlogs_dir)
            # Return evidence/chatlogs directory
            return evidence_chatlogs_dir
        elif file_extension.lower() in media_filetypes:
            # Move to evidence/media folder
            FileManager().move_file(file_path, evidence_media_dir)
            # Return evidence/media directory
            return evidence_media_dir
        else:
            # If the file type is not recognized, you may handle it accordingly.
            logging.error("Unsupported file type:", file_extension)
            # No directory to return, return nothing
            return None

    @staticmethod
    def save_evidence_to_db(file_name, destination_dir, md5_hash) -> None:
        """
        Save evidence info to the db
        :param file_name: name of the file
        :param destination_dir: evidence folder storing the file
        :param md5_hash: hash of the file
        :return:
        """

        # Get type (media/chatlog)
        evidence_type = os.path.basename(destination_dir)

        # Create evidence model instance
        evidence = EvidenceModel(case_number=CaseModel().case_number,
                                 file_name=file_name,
                                 description=None,
                                 evidence_type=evidence_type,
                                 hash_value=md5_hash,
                                 exif_data=None)

        # Save instance to DB
        evidence.save()

    def update_evidence_view_box(self) -> None:
        """
        Logic for handling updating the evidene view box with up-to-date evidence from db
        :return:
        """
        # Get the filename hash maps from db
        filename_hash_maps = DatabaseManager().fetch_evidence_filename_hash()

        # Update evidence view box
        self.view.update_evidence_box(filename_hash_maps)

    @staticmethod
    def export_hashes(event: Event = None) -> None:
        """
        Logic for exporting media hashes
        :param event:
        :return:
        """

        # Ask user for directory to export hashes to
        export_path = filedialog.askdirectory(
            title="Export Media Hashes",
        )

        # Check if user canceled the dialog
        if not export_path:
            logging.info("Export canceled by user.")
            return

        # Get the hash values of all files from db where evidence type is media
        # [(id, case_num, file_name, desc, type, hash, exif),...]
        evidence_tuple_list = DatabaseManager().fetch_evidence_by_type('media')

        # Get hashes from list of tuples
        hashes = [item[5] for item in evidence_tuple_list]

        # Writes hashes to file
        path = os.path.join(export_path, f"{CaseModel().case_name}-media-hashes.txt")
        with open(path, 'w') as f:
            # Write each hash on a new line
            for hash_val in hashes:
                f.write(hash_val + '\n')

        logging.info(f"Media hashes exported to {path} ")

        # Log activity
        (ActivityLogModel().
         insert(f"Media hashes exported to '{path}'"))

    def load(self) -> None:
        """
        Logic for loading collection tab for the current case
        :return:
        """
        logging.info("Loading Collection...")

        # Update evidence view box to show evidence from DB
        self.update_evidence_view_box()
