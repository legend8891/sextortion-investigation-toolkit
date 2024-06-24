import logging
import tkinter as tk
from typing import Dict
import customtkinter
from src.views.ui_components.widgets import EvidenceViewBox
logging.basicConfig(level=logging.INFO)


class CollectionView(customtkinter.CTkFrame):
    """
    View for the Collection tab
    """

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)

        logging.info("Creating Collection Tab")

        # Box for previewing uploaded evidence and their hashes
        self.evidence_view_box = EvidenceViewBox(self)
        self.evidence_view_box.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Button to upload files
        self.file_upload_button = customtkinter.CTkButton(self, text="UPLOAD MEDIA OR CHAT LOG FILES")
        self.file_upload_button.pack(padx=20, pady=20, expand=False, fill=tk.BOTH)

        # Button to export hashes
        self.export_hashes_button = customtkinter.CTkButton(self, text="EXPORT HASHES OF MEDIA FILES")
        self.export_hashes_button.pack(padx=20, pady=20, expand=False, fill=tk.BOTH)

        # Add all content to the frame
        self.pack(fill="both", expand=True)
        self.pack_propagate(False)

    def update_evidence_box(self, filename_hash_maps: [Dict[str, str]]) -> None:
        """
        Updates evidence view box with files and their hashes
        :param filename_hash_maps: list of dictionaries for filename to hash value mappings
        :return:
        """

        # Clear the view box
        self.evidence_view_box.delete(*self.evidence_view_box.get_children())

        # Populate with up-to-date entries
        for filename_hash_map in filename_hash_maps:
            logging.info("Inserting {} into evidence view".format(filename_hash_map))
            filename = filename_hash_map["file_name"]
            hash_value = filename_hash_map["hash_value"]
            self.evidence_view_box.insert("", "end", values=(filename, hash_value))
