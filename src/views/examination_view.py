import logging
import tkinter as tk
from typing import Callable
import customtkinter
logging.basicConfig(level=logging.INFO)


class ExaminationView(customtkinter.CTkFrame):
    """
    View for the Examination tab
    """

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)

        logging.info("Creating Examination Tab")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        # 2 frames to hold everything chatlog related and media related
        self.clogs_frame = customtkinter.CTkFrame(self, border_width=1)
        self.clogs_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky='nsew')
        self.media_frame = customtkinter.CTkFrame(self, border_width=1)
        self.media_frame.grid(row=0, column=2, columnspan=1, padx=20, pady=20, sticky='nsew')

        # Top titles
        self.clogs_label = customtkinter.CTkLabel(self.clogs_frame, text="CHAT LOGS",
                                                  font=customtkinter.CTkFont(size=20, weight="bold"))
        self.media_label = customtkinter.CTkLabel(self.media_frame, text="MEDIA",
                                                  font=customtkinter.CTkFont(size=20, weight="bold"))
        self.clogs_label.pack(padx=20, pady=20, fill='x', expand=False)
        self.media_label.pack(padx=20, pady=20, fill='x', expand=False)

        # Selection dropdowns
        self.clog_select = customtkinter.CTkOptionMenu(self.clogs_frame, values=['Select a chat log to examine'])
        self.media_select = customtkinter.CTkOptionMenu(self.media_frame, values=['Select a media file to examine'])
        self.clog_select.pack(padx=20, pady=20, fill='x', expand=False)
        self.media_select.pack(padx=20, pady=20, fill='x', expand=False)

        # CLog viewer
        self.clog_view_frame = customtkinter.CTkFrame(self.clogs_frame)
        self.clog_view_frame.pack(padx=20, pady=10, fill='both', expand=True)
        self.clog_viewer = tk.Text(self.clog_view_frame, width=1, height=1, font=("Arial", 16), background="#252525")
        self.clog_viewer.tag_configure("highlight", background="blue", foreground='white')
        self.clog_viewer.tag_configure("flag", background="red", foreground='white')

        self.clog_viewer.pack(fill='both', expand=True)

        # CLog search box
        self.clog_searchbox = customtkinter.CTkEntry(self.clogs_frame, placeholder_text="enter search regex")
        self.clog_searchbox.pack(padx=20, pady=10, fill='x', expand=False)

        # Enter search
        self.search_button = customtkinter.CTkButton(self.clogs_frame, text="SEARCH FOR IN CHAT LOG")
        self.search_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Flag button
        self.flag_text_button = customtkinter.CTkButton(self.clogs_frame, text='FLAG HIGHLIGHTED TEXT')
        self.flag_text_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Button for unflagging flagged text
        self.unflag_text_button = customtkinter.CTkButton(self.clogs_frame, text="UNFLAG FLAGGED TEXT")
        self.unflag_text_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Find external link button
        self.find_urls = customtkinter.CTkButton(self.clogs_frame, text="FIND URLS")
        self.find_urls.pack(padx=20, pady=10, fill='x', expand=False)

        # Grooming detection trigger button
        self.gd_button = customtkinter.CTkButton(self.clogs_frame, text="PREDICT GROOMING IN CHAT LOG")
        self.gd_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Button to carry out object detection and find objects in media
        self.od_button = customtkinter.CTkButton(self.media_frame, text="SAFE VIEW (DETECT OBJECTS)")
        self.od_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Button to preview photo/video
        self.view_button = customtkinter.CTkButton(self.media_frame, text="PREVIEW IMAGE/VIDEO")
        self.view_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Buttons to flag and unflag media file
        self.flag_media_button = customtkinter.CTkButton(self.media_frame, text="FLAG MEDIA FILE")
        self.flag_media_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Button to extract EXIF from image
        self.exif_button = customtkinter.CTkButton(self.media_frame, text="EXTRACT EXIF DATA")
        self.exif_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Button to extract metadata from video
        self.metadata_button = customtkinter.CTkButton(self.media_frame, text="EXTRACT METADATA")
        self.metadata_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Button to view hex for media file
        self.hex_button = customtkinter.CTkButton(self.media_frame, text="VIEW HEXADECIMAL")
        self.hex_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Button to add comments to current CLog file
        self.comment_clog_button = customtkinter.CTkButton(self.clogs_frame, text="ADD COMMENTS")
        self.comment_clog_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Button to add comments to current media file
        self.comment_media_button = customtkinter.CTkButton(self.media_frame, text="ADD COMMENTS")
        self.comment_media_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Add all content to the frame
        self.pack(fill="both", expand=True)
        self.pack_propagate(False)

    def bind_update_clog_selection(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binds mouse enter on CLog selector to updating contents
        :param callback:
        :return:
        """
        self.clog_select.bind("<Enter>", callback)

    def bind_update_media_selection(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binds mouse enter on media selector to updating contents
        :param callback:
        :return:
        """
        self.media_select.bind("<Enter>", callback)

    def reset_clog_view_box(self) -> None:
        """
        Clears all text from CLog view box
        :return:
        """
        self.clog_viewer.delete(1.0, tk.END)

    def display_clog_line(self, line: str) -> None:
        """
        Displays CLog line to view box
        :param line:
        :return:
        """
        self.clog_viewer.insert(tk.END, line + '\n')
