import logging
import tkinter as tk
import customtkinter
from src.views.ui_components.widgets import IntegrityViewBox
logging.basicConfig(level=logging.INFO)


class PreservationView(customtkinter.CTkFrame):
    """
    View for the Preservation tab
    """

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)

        logging.info("Creating Preservation Tab")

        # Setup grid for the tab
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Viewing and checking integrity of files
        self.integrity_frame = customtkinter.CTkFrame(self, border_width=1)
        self.integrity_frame.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        self.integrity_label = customtkinter.CTkLabel(self.integrity_frame, text="FILE INTEGRITY",
                                                      font=customtkinter.CTkFont(size=15, weight="bold"))
        self.integrity_label.pack(padx=20, pady=5, fill=tk.X)

        self.integrity_view_box = IntegrityViewBox(self.integrity_frame)
        self.integrity_view_box.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        self.integrity_button = customtkinter.CTkButton(self.integrity_frame, text="CHECK INTEGRITY OF ALL FILES")
        self.integrity_button.pack(padx=20, pady=20, fill=tk.X)

        # Viewing Chain of Custody log
        self.coc_frame = customtkinter.CTkFrame(self, border_width=1)
        self.coc_frame.grid(row=0, column=1, padx=(5, 20), pady=20, sticky='nsew')

        self.coc_label = customtkinter.CTkLabel(self.coc_frame, text="INVESTIGATION ACTIVITY LOG",
                                                font=customtkinter.CTkFont(size=15, weight="bold"))
        self.coc_label.pack(padx=20, pady=5, fill=tk.X)

        self.coc_view_box = customtkinter.CTkTextbox(self.coc_frame)
        self.coc_view_box.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Add all content to the frame
        self.pack(fill="both", expand=True)
        self.pack_propagate(False)

