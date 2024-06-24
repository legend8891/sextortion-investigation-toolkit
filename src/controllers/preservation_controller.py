import logging
import os
import tkinter as tk
from asyncio import Event
from src.models.activitylog import ActivityLogModel
from src.utility.utility import DatabaseManager, FileManager
from src.views.preservation_view import PreservationView
logging.basicConfig(level=logging.INFO)


class PreservationController:
    """
    Controller for the Preservation tab
    """

    def __init__(self, view: PreservationView) -> None:
        # Preservation view
        self.view = view

        # Bindings to view
        self.view.integrity_button.configure(command=self.check_integrity_all)

        # Bind updating log view to log model
        ActivityLogModel().insert_callback = self.update_activity_log_view
        ActivityLogModel().controller = self

    def check_integrity_all(self, event: Event = None) -> None:
        """
        Recomputes hashes and checks against originals to ensure integrity of files
        :param event:
        :return:
        """
        logging.info("Checking integrity of ALL files")

        # Log activity
        (ActivityLogModel().
         insert(f"File integrity check started on all files"))

        # Clear the file/hash view
        self.view.integrity_view_box.clear()

        # Original filenames and their hashes computed when uploaded fetched from db
        original_file_hashes = DatabaseManager().fetch_evidence_filename_hash()

        # Get the directories with files to re-hash
        case_directory = FileManager().case_directory
        media_dir = os.path.join(case_directory, "evidence", "media")
        chatlogs_dir = os.path.join(case_directory, "evidence", "chatlogs")

        # Get all the recomputed hashes for each file
        new_chatlog_file_hashes = FileManager().compute_md5_hashes_in_directory(chatlogs_dir)
        new_media_file_hashes = FileManager().compute_md5_hashes_in_directory(media_dir)
        new_file_hashes = new_chatlog_file_hashes + new_media_file_hashes

        # Holds file hashes that don't match original
        failed_hashes = []

        # Iterate through all recomputed hashes and compare to original hashes
        for new_file_hash in new_file_hashes:
            filename = new_file_hash["file_name"]
            recomputed_hash_value = new_file_hash["hash_value"]
            original_hash = next((item for item in original_file_hashes if item["file_name"] == filename), None)
            logging.info("File {} original hash {} recomputed hash {}".format(filename, original_hash["hash_value"],
                                                                              recomputed_hash_value))
            if original_hash is not None and original_hash["hash_value"] != recomputed_hash_value:
                # Filename and new hash for each failed hash
                failed_hashes.append({"file_name": filename, "new_hash": recomputed_hash_value})
                # Log to system
                logging.warning("{} failed integrity check".format(filename))
                # Log to activity log
                (ActivityLogModel().
                 insert(f"File {filename} failed integrity check: original MD5 Hash '{original_hash["hash_value"]}' "
                        f"did not match recomputed MD5 hash '{recomputed_hash_value}' "))
            elif original_hash is not None and original_hash["hash_value"] == recomputed_hash_value:
                # Log to system
                logging.info("{} passed integrity check".format(filename))
                # Log to activity log
                (ActivityLogModel().
                 insert(f"File {filename} passed integrity check: original MD5 Hash '{original_hash["hash_value"]}' "
                        f"matched recomputed MD5 hash '{recomputed_hash_value}' "))

        # Display on view table
        for new_file_hash in new_file_hashes:
            filename = new_file_hash["file_name"]
            recomputed_hash_value = new_file_hash["hash_value"]
            original_hash = next((item for item in original_file_hashes if item["file_name"] == filename), None)
            if original_hash is not None:
                if {"file_name": filename, "new_hash": recomputed_hash_value} in failed_hashes:
                    self.view.integrity_view_box.insert('', 'end', values=(
                        filename, original_hash["hash_value"], recomputed_hash_value), tags='failed')
                else:
                    self.view.integrity_view_box.insert('', 'end', values=(
                        filename, original_hash["hash_value"], recomputed_hash_value), tags='passed')

    def update_activity_log_view(self):
        """
        Logic for updating the activity view textbox from the activity log file
        :return:
        """
        logging.info("Updating activity log view")

        # Location of the log file
        log_dir = os.path.join(FileManager().case_directory, "reports", "ActivityLog.txt")

        # Clear the log textbox
        self.view.coc_view_box.delete(1.0, tk.END)

        # Attempt to get the file contents and update log view box
        try:
            with open(log_dir, 'r') as file:
                self.view.coc_view_box.delete(1.0, tk.END)
                self.view.coc_view_box.insert(1.0, file.read())
        except FileNotFoundError:
            self.view.coc_view_box.insert(tk.END, 'end')

        # Always scroll to bottom
        self.view.coc_view_box.yview_moveto(1.0)

    def load(self) -> None:
        """
        Handle loading of controller
        :return:
        """
        self.update_activity_log_view()
