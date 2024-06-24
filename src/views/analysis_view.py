import logging
import os
import customtkinter
from PIL import Image
from src.utility.utility import FileManager
logging.basicConfig(level=logging.INFO)


class AnalysisView(customtkinter.CTkFrame):
    """
    View for the Analysis tab
    """

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)

        logging.info("Creating Analysis Tab")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)

        self.sidebar = customtkinter.CTkFrame(self)
        self.sidebar.grid(row=0, column=0, columnspan=1, padx=20, pady=20, sticky="nsew")

        self.clogs_button = customtkinter.CTkButton(self.sidebar, text="FLAGGED \n CHAT LOGS")
        self.clogs_button.pack(padx=20, pady=20, fill="both", expand=True)

        self.media_button = customtkinter.CTkButton(self.sidebar, text="FLAGGED \n MEDIA")
        self.media_button.pack(padx=20, pady=20, fill="both", expand=True)

        self.report_button = customtkinter.CTkButton(self.sidebar, text="GENERATE \n REPORT")
        self.report_button.pack(padx=20, pady=20, fill="both", expand=True)

        self.frame = customtkinter.CTkScrollableFrame(self)
        self.frame.grid(row=0, column=1, columnspa=3, padx=20, pady=20, sticky="nsew")

        # Add all content to the frame
        self.pack(fill="both", expand=True)
        self.pack_propagate(False)

    def highlight_button(self, button_name: str) -> None:
        """
        Highlights sidebar buttons depending which is selected
        :param button_name:
        :return:
        """
        if button_name == 'clogs':
            self.clogs_button.configure(border_width=2)
            self.media_button.configure(border_width=0)
            self.report_button.configure(border_width=0)
        elif button_name == 'media':
            self.clogs_button.configure(border_width=0)
            self.media_button.configure(border_width=2)
            self.report_button.configure(border_width=0)
        elif button_name == 'report':
            self.clogs_button.configure(border_width=0)
            self.media_button.configure(border_width=0)
            self.report_button.configure(border_width=2)
        else:
            return

    def clear_frame(self):
        """
        Clears contents inside the frame
        :return:
        """
        frame = self.frame
        for widget in frame.winfo_children():
            widget.destroy()


class FlaggedClogView(customtkinter.CTkFrame):
    """
    View for flagged CLogs
    """

    def __init__(self, master, file_name, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)

        # Title is the filename of the CLog
        self.title = customtkinter.CTkLabel(self, text=file_name, font=customtkinter.CTkFont(size=20, weight='bold'))
        self.title.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        # View flagged text
        self.flagged_text_label = customtkinter.CTkLabel(self, text='Flagged Text',
                                                         font=customtkinter.CTkFont(weight='bold'))
        self.flagged_text_label.grid(row=1, column=0, padx=20, pady=0, sticky='nsew')
        self.flagged_text_box = customtkinter.CTkLabel(self, text="")
        self.flagged_text_box.grid(row=2, column=0, padx=20, pady=20, sticky='nsew')

        # View comments
        self.comments_label = customtkinter.CTkLabel(self, text='Comments', font=customtkinter.CTkFont(weight='bold'))
        self.comments_label.grid(row=3, column=0, padx=20, pady=0, sticky='nsew')
        self.comments_box = customtkinter.CTkLabel(self, text="")
        self.comments_box.grid(row=4, column=0, padx=20, pady=20, sticky='nsew')

        # Add all content to the frame
        self.pack(fill="both", expand=True)
        self.pack_propagate(False)

    def add_flagged_text(self, flagged_texts: [str]) -> None:
        """
        Populates flagged text box with flagged texts
        :param flagged_texts:
        :return:
        """

        # Clear the box
        self.flagged_text_box.configure(text="")

        # Populate with flagged text
        flagged_text = "\n".join(flagged_texts)
        self.flagged_text_box.configure(text=flagged_text)

    def add_comments(self, comments: str) -> None:
        """
        Populates comment box with comments
        :param comments:
        :return:
        """
        self.comments_box.configure(text=comments)


class FlaggedMediaView(customtkinter.CTkFrame):
    """
    View for single flagged media file
    """

    def __init__(self, master, file_name, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)

        # Title is the filename of the media file
        self.title = customtkinter.CTkLabel(self, text=file_name, font=customtkinter.CTkFont(size=20, weight='bold'))
        self.title.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')

        # Media preview
        media_file_path = os.path.join(FileManager().case_directory, 'evidence', 'media', file_name)
        file_extension = os.path.splitext(file_name)[1]
        if file_extension in [".mp4", ".mov", ".avi", ".mkv"]:
            # Is video
            thumbnail = FileManager().generate_thumbnail(media_file_path, width=300, height=200)
            photo = customtkinter.CTkImage(thumbnail, size=(300, 300))
        else:
            # Is photo
            image = Image.open(media_file_path)
            photo = customtkinter.CTkImage(image, size=(300, 300))

        self.preview = customtkinter.CTkLabel(self, image=photo, text="")
        self.preview.grid(row=1, column=0, padx=20, pady=20, sticky='nsew')

        # View comments
        self.comments_label = customtkinter.CTkLabel(self, text='Comments', font=customtkinter.CTkFont(weight='bold'))
        self.comments_label.grid(row=3, column=0, padx=20, pady=0, sticky='nsew')
        self.comments_box = customtkinter.CTkLabel(self, text="")
        self.comments_box.grid(row=4, column=0, padx=20, pady=20, sticky='nsew')

        # View EXIF / Metadata / Hex
        self.meta_label = customtkinter.CTkLabel(self, text='Extracted Data', font=customtkinter.CTkFont(weight='bold'))
        self.meta_label.grid(row=5, column=0, padx=20, pady=0, sticky='nsew')
        self.meta_box = customtkinter.CTkLabel(self, text="")
        self.meta_box.grid(row=6, column=0, padx=20, pady=20, sticky='nsew')

        # Add all content to the frame
        self.pack(fill="both", expand=True)
        self.pack_propagate(False)

    def add_comments(self, comments: str) -> None:
        """
        Populates comment box with comments
        :param comments:
        :return:
        """
        self.comments_box.configure(text=comments)

    def add_meta(self, metadata: str) -> None:
        """
        Populates meta box with metadata
        :param metadata:
        :return:
        """
        self.meta_box.configure(text=metadata)


