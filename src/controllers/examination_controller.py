import logging
import os
import re
import tkinter
import tkinter as tk
from asyncio import Event
from tkinter import messagebox
import customtkinter
import cv2
from PIL import Image
from urlextract import URLExtract

from src.ai.grooming_detection.groomingdetector import GroomingDetector
from src.ai.object_detection.objectdetection import ObjectDetection
from src.models.activitylog import ActivityLogModel
from src.models.flags import FlagManager
from src.utility.utility import FileManager, DatabaseManager
from src.views.examination_view import ExaminationView
from src.views.ui_components.popups import EXIFPopup, ObjectsPopup, URLsPopup, UnflagTextPopup, MetaPopup, HexPopup, \
    DetectedGroomingPopup

logging.basicConfig(level=logging.INFO)


class ExaminationController:
    """
    Controller for the Examination tab
    """

    def __init__(self, view: ExaminationView) -> None:
        # Examination view
        self.view = view

        # Bindings to view
        self.view.clog_select.configure(command=self.select_clog)
        self.view.media_select.configure(command=self.select_media)
        self.view.bind_update_clog_selection(self.update_clog_selection)
        self.view.bind_update_media_selection(self.update_media_selection)
        self.view.view_button.configure(command=self.preview_media)
        self.view.exif_button.configure(command=self.extract_exif)
        self.view.metadata_button.configure(command=self.extract_meta)
        self.view.od_button.configure(command=self.detect_objects)
        self.view.gd_button.configure(command=self.detect_grooming)
        self.view.search_button.configure(command=self.search_regex)
        self.view.find_urls.configure(command=self.extract_urls)
        self.view.flag_text_button.configure(command=self.flag_highlighted_text)
        self.view.flag_media_button.configure(command=self.flag_selected_media)
        self.view.unflag_text_button.configure(command=self.unflag_text)
        self.view.comment_clog_button.configure(command=self.comment_clog)
        self.view.comment_media_button.configure(command=self.comment_media)
        self.view.hex_button.configure(command=self.view_hex)
        self.view.bind('<Button-1>', lambda event: self.view.focus_set())

    def comment_clog(self, event: Event = None) -> None:
        """
        Logic for adding comments to CLog file
        :param event:
        :return:
        """
        # Show dialog for entering comments
        file = self.view.clog_select.get()
        input_dialog = customtkinter.CTkInputDialog(text="Enter Comments",
                                                    title=f"{file} Comments")

        # Store comments in db
        comments = input_dialog.get_input()
        DatabaseManager().update_evidence_description(file, comments)

        # Log activity
        (ActivityLogModel().
         insert(f"Comment '{comments}' added to chat log file '{file}'"))

    def comment_media(self, event: Event = None) -> None:
        """
        Logic for adding comments to media file
        :param event:
        :return:
        """
        # Show dialog for entering comments
        file = self.view.media_select.get()
        input_dialog = customtkinter.CTkInputDialog(text="Enter Comments",
                                                    title=f"{file} Comments")

        # Store comments in db
        comments = input_dialog.get_input()
        DatabaseManager().update_evidence_description(file, comments)

        # Log activity
        (ActivityLogModel().
         insert(f"Comment '{comments}' added to media file '{file}'"))

    def select_clog(self, event: Event = None) -> None:
        """
        Logic for handling selection of CLog to examine
        :param event:
        :return:
        """
        # Grab selected CLog
        selection = self.view.clog_select.get()
        logging.info(f"Selecting CLog for examination: {selection}")

        # Parse selected CLog
        try:
            self.parse_clog()
        except Exception as e:
            messagebox.showerror("ERROR", "Could not parse chat log, unsupported or corrupted format.")


    def select_media(self, event: Event = None) -> None:
        """
        Logic for handling selection of media to examine
        :param event:
        :return:
        """
        # Grab selected media
        selection = self.view.media_select.get()
        flagged_files = FlagManager().load_flagged_media_files()
        logging.info(f"Selecting media for examination: {selection}")
        if selection in flagged_files:
            # Already flagged so show unflag button
            self.view.flag_media_button.configure(text="UNFLAG MEDIA FILE")
        else:
            # Not flagged to show flag button
            self.view.flag_media_button.configure(text="FLAG MEDIA FILE")

    def update_clog_selection(self, event: Event = None) -> None:
        """
        Logic for handling updating chat_logs to select from
        :param event:
        :return:
        """
        logging.info("Updating CLog selection box")
        clogs_dir = os.path.join(FileManager().case_directory, "evidence", "chatlogs")
        clog_files = [fname for fname in os.listdir(clogs_dir)]
        self.view.clog_select.configure(values=clog_files)

    def update_media_selection(self, event: Event = None) -> None:
        """
        Logic for handling updating media to select from
        :param event:
        :return:
        """
        logging.info("Updating media selection box")
        media_dir = os.path.join(FileManager().case_directory, "evidence", "media")
        media_files = [fname for fname in os.listdir(media_dir)]
        self.view.media_select.configure(values=media_files)

    def preview_media(self, event: Event = None) -> None:
        """
        Logic for previewing media files images/videos
        :param event:
        :return:
        """
        # Get the selected media name and directory
        media_name = self.view.media_select.get()
        file_path = self.get_current_media()

        # Check the file extension
        _, file_extension = os.path.splitext(media_name)

        # Attempt to load and display the media
        try:
            if file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                # Preview for images
                self.preview_image(media_name, file_path)
            elif file_extension.lower() in ['.mp4', '.avi', '.mov']:
                # Preview for videos
                self.preview_video(media_name, file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load media: {file_path}")
            logging.error(f"Failed to load media: {str(e)}")

    def extract_exif(self, event: Event = None) -> None:
        """
        Extracts EXIF data from the current selected photo.
        """
        # Get the selected media name and directory
        media_name = self.view.media_select.get()
        file_path = self.get_current_media()

        logging.info(f"Extracting EXIF models from {file_path}")

        # Extract EXIF data
        exif_data = FileManager().extract_exif(file_path)

        # Popup to show EXIF models of image
        popup = EXIFPopup(media_name, self.view)

        # Display EXIF data
        popup.data_dump.insert(tk.END, exif_data)

        # Log activity
        (ActivityLogModel().
         insert(f"Extracted EXIF data from '{media_name}'"))

    def extract_meta(self, event: Event = None) -> None:
        """
        Extract more detailed metadata from media
        :param event:
        :return:
        """
        media_name = self.view.media_select.get()
        file_path = self.get_current_media()

        # Extract metadata from file
        meta_data = FileManager().extract_metadata(file_path)

        # Show popup
        popup = MetaPopup(media_name, self.view)

        # Display EXIF data
        popup.data_dump.insert(tk.END, meta_data)

        # Log activity
        (ActivityLogModel().
         insert(f"Extracted metadata from '{media_name}'"))

    def view_hex(self, event: Event = None) -> None:
        """
        View hex representation of file data alongside the plaintext
        :param event:
        :return:
        """
        media_name = self.view.media_select.get()
        file_path = self.get_current_media()

        # Extract hex data from file
        hex_string = FileManager().extract_hex(file_path)

        # Show popup
        popup = HexPopup(media_name, self.view)

        # Display EXIF data
        popup.data_dump.insert(tk.END, hex_string)

        # Log activity
        (ActivityLogModel().
         insert(f"Viewed hex from '{media_name}'"))

    def preview_image(self, file_name: str, file_path: str) -> None:
        """
        Logic for previewing images using PIL
        :param file_name: file name of image to preview
        :param file_path: file path of image to preview
        :return:
        """
        # Load and display the image
        image = Image.open(file_path)
        width, height = image.size
        ctk_image = customtkinter.CTkImage(dark_image=image, light_image=image, size=(400, 550))

        # Create a popup window
        popup = customtkinter.CTkToplevel(self.view)
        popup.title(file_name)
        popup.geometry('400x550')

        # Display the image in the popup window
        image_label = customtkinter.CTkLabel(popup, image=ctk_image, text="")
        image_label.pack(fill='both', expand=True)

        logging.info(f"Previewing image: {file_path}")

        # Log activity
        (ActivityLogModel().
         insert(f"Viewed preview of image '{file_name}'"))

    @staticmethod
    def preview_video(media_name: str, file_path: str) -> None:
        """
        Logic for previewing images using CV2 library
        :param media_name:
        :param file_path:
        :return:
        """

        logging.info(f"Previewing video: {file_path}")

        # Display the video using OpenCV
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            messagebox.showerror("Error", f"Failed to open video: {file_path}")
            return

        # Create a popup window
        cv2.namedWindow(media_name, cv2.WINDOW_NORMAL)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv2.imshow(media_name, frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break

        # Release the video capture object and close OpenCV windows
        cap.release()
        cv2.destroyAllWindows()

        # Log activity
        (ActivityLogModel().
         insert(f"Viewed preview of video '{media_name}'"))

    def detect_objects(self, event: Event = None) -> None:
        """
        Logic for detecting objects using YOLO
        :param event:
        :return:
        """
        media = self.get_current_media()
        _, file_extension = os.path.splitext(media)

        # Call object detection function for appropriate media type
        results = None
        if file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            results = ObjectDetection().detect_objects_photo(media)
        elif file_extension.lower() in ['.mp4', '.avi', '.mov']:
            results = ObjectDetection().detect_objects_video(media)
        else:
            logging.error(f"Invalid file extension: {file_extension}")

        # Only show results if object(s) were found
        if results == '' or results is None:
            # No objects were found
            logging.info(f"No objects could be detected in media {media}")
            messagebox.showinfo("No objects found", f"No objects could be detected in {os.path.basename(media)}")
        else:
            # Objects were found
            popup = ObjectsPopup(os.path.basename(media), self.view)
            popup.objects_box.insert(tk.END, results)

        # Log activity
        (ActivityLogModel().
         insert(f"Detected objects in '{media}'"))

    def get_current_media(self) -> str:
        """
        Get the filepath for the current selected media
        :return:
        """
        # Get the selected media name and directory
        media_name = self.view.media_select.get()
        media_dir = os.path.join(FileManager().case_directory, "evidence", "media")
        file_path = os.path.join(media_dir, media_name)
        return file_path

    def get_current_clog(self) -> str:
        """
        Get the filepath for the current selected CLog
        :return:
        """
        # Get the selected clog name and directory
        clog_name = self.view.clog_select.get()
        clog_dir = os.path.join(FileManager().case_directory, "evidence", "chatlogs")
        file_path = os.path.join(clog_dir, clog_name)
        return file_path

    def parse_clog(self):
        """
        Logic for parsing Instagram JSON, Snapchat JSON and plaintext chat logs
        :return:
        """
        # Get filepath of currently select CLog
        clog_dir = self.get_current_clog()

        clog_type = FileManager().validate_clog(clog_dir)

        if clog_type == 'instagram-json':
            # Valid Instagram JSON chatlog
            # Contains a single conversation with one user
            df = FileManager().parse_insta_json(clog_dir)
            self.view.reset_clog_view_box()
            for _, row in df.iterrows():
                timestamp = row['timestamp']
                sender = row['sender']
                message = row['message']
                self.view.display_clog_line(f"[{timestamp}] {sender}: {message}")
        elif clog_type == 'snapchat-json':
            # Valid Snapchat JSON chatlog
            # May contain multiple converstions with different users in the one file
            sender_df_tuples = FileManager().parse_snap_json(clog_dir)
            self.view.reset_clog_view_box()
            for sender, df in sender_df_tuples:
                self.view.display_clog_line('-' * 50)
                self.view.display_clog_line(sender)
                self.view.display_clog_line('-' * 50)
                for _, row in df.iterrows():
                    timestamp = row['timestamp']
                    sender = row['sender']
                    message = row['message']
                    self.view.display_clog_line(f"[{timestamp}] {sender}: {message}")
        elif clog_type == 'plaintext':
            # Plaintext chat log, could be in any format
            # Read as a string
            text = FileManager().parse_txt_file(clog_dir)
            self.view.reset_clog_view_box()
            self.view.display_clog_line(text)
        else:
            # Invalid CLog
            # May be an invalid file type or was invalid when compared with the schemas
            logging.error(f"Unsupported chat log {os.path.basename(clog_dir)}")
            messagebox.showerror("Error", "Unsupported chat log: this chat log format is currently not supported.")
            return

        # Get stored flags and highlight in the clog viewer
        flagged_text = FlagManager().load_flagged_text(clog_file=self.view.clog_select.get())
        if len(flagged_text) > 0:
            self.tag_flagged_text(flagged_text)

    def search_regex(self, event: Event = None) -> None:
        """
        Logic for searching chat log view using regular expressions
        :param event:
        :return:
        """
        # Search box from UI
        search_box = self.view.clog_searchbox
        clog_file = self.view.clog_select.get()

        # Get search pattern from entry box
        search_pattern = search_box.get()

        logging.info(f"Searching for '{search_pattern}' in '{clog_file}'")

        # Perform the search
        self.search(search_pattern)

        # Log activity
        (ActivityLogModel().
         insert(f"Searched with regex '{search_pattern}' '{clog_file}'"))

    def search(self, search_pattern):
        """
        Perform search with search pattern in CLog view
        :param search_pattern:
        :return:
        """
        clog_viewer = self.view.clog_viewer

        # Remove highlighted tags
        clog_viewer.tag_remove("highlight", "1.0", "end")

        # Perform regex search
        matches = list(re.finditer(search_pattern, clog_viewer.get("1.0", "end")))

        # Highlight matches
        for match in matches:
            start_index = "1.0 + {} chars".format(match.start())
            end_index = "1.0 + {} chars".format(match.end())
            clog_viewer.tag_add("highlight", start_index, end_index)

        # Jump to the first highlighted match
        if matches:
            first_match_start_index = "1.0 + {} chars".format(matches[0].start())
            clog_viewer.see(first_match_start_index)

    def extract_urls(self, event: Event = None) -> None:
        """
        Logic for extracting URLs from chat log view
        :param event:
        :return:
        """
        file_name = self.view.clog_select.get()
        logging.info(f"Finding URLs in {file_name}")

        # View box for CLogs
        clogs_view = self.view.clog_viewer

        # Get content of the CLogs view
        clogs_text = clogs_view.get("1.0", "end")

        # Extract URLs
        extractor = URLExtract()
        urls = extractor.find_urls(clogs_text)

        # Create popup
        popup = URLsPopup(urls, self.view)
        for url in urls:
            popup.urls_box.insert(tk.END, url + '\n')
            # Log activity
            (ActivityLogModel().
             insert(f"Extracted URL '{url}' from '{file_name}'"))

    def flag_highlighted_text(self, event: Event = None) -> None:
        """
        Logic for flagging text in the clog viewer
        :param event:
        :return:
        """
        try:
            selected_text = self.view.clog_viewer.get(tk.SEL_FIRST, tk.SEL_LAST)
            clog_filename = self.view.clog_select.get()
            FlagManager().flag_text(clog_filename, selected_text)
            logging.info("Text flagged successfully")
            self.tag_flagged_text(FlagManager.load_flagged_text(clog_filename))
            # Log activity
            (ActivityLogModel().
             insert(f"Flagged text '{selected_text}' in '{clog_filename}'"))
        except tkinter.TclError as e:
            messagebox.showerror("No Text Selected",
                                 "No text was selected to flag, highlight text in the window and try again")

    def tag_flagged_text(self, flagged_text: [str]) -> None:
        """
        Tag flagged text in the chat log viewer with the 'flag' tag.
        :param flagged_text: List of flagged text strings
        """
        logging.info("Tagging all flagged text in CLog viewer")
        clog_viewer = self.view.clog_viewer
        for text in flagged_text:
            start_index = '1.0'
            while True:
                start_index = clog_viewer.search(text, start_index, stopindex=tk.END)
                if not start_index:
                    break
                end_index = f"{start_index}+{len(text)}c"
                clog_viewer.tag_add("flag", start_index, end_index)
                start_index = end_index

    def flag_selected_media(self, event: Event = None) -> None:
        """
        Logic for flagging the currently selected media file
        :return:
        """
        flagged_media_files = FlagManager().load_flagged_media_files()
        current_media_file = self.view.media_select.get()

        if current_media_file in flagged_media_files:
            # The media is already flagged so unflag
            self.view.flag_media_button.configure(text="FLAG MEDIA FILE")
            logging.info(f"Unflagging currently selected media file '{current_media_file}'")
            FlagManager().delete_media_file_flag(current_media_file)
        else:
            # The media isn't flagged so flag it
            self.view.flag_media_button.configure(text="UNFLAG MEDIA FILE", bg_color='darkred')
            logging.info(f"Flagging currently selected media file '{current_media_file}'")
            FlagManager().flag_media(current_media_file)

    def unflag_text(self, event: Event = None) -> None:
        """
        Logic for unflagging flagged text
        :param event:
        :return:
        """
        logging.info("Displaying unflag popup")
        popup = UnflagTextPopup(self.view)
        popup.bind_delete_flag(lambda e: self.delete_text_flag(popup.flags_listbox.get(), popup))
        flagged_texts = FlagManager().load_flagged_text(self.view.clog_select.get())
        popup.update_listbox(flagged_texts)

    def delete_text_flag(self, flag_text: str, popup: UnflagTextPopup) -> None:
        """
        Logic for deleting text flag and refreshing the popup
        :param flag_text:
        :param popup:
        :return:
        """
        logging.info(f"Deleting text flag {flag_text}")
        clog_file = self.view.clog_select.get()
        FlagManager().delete_clog_text_flag(clog_file, flag_text)
        flagged_texts = FlagManager().load_flagged_text(self.view.clog_select.get())
        popup.update_listbox(flagged_texts)
        try:
            self.parse_clog()
        except Exception as e:
            logging.error("Unable to parse CLog")
        # Log activity
        (ActivityLogModel().
         insert(f"Unflagged text '{flag_text}' in '{clog_file}'"))

    def detect_grooming(self, event: Event = None) -> None:
        # Get filepath of currently select CLog to detect grooming in
        clog_dir = self.get_current_clog()

        clog_type = FileManager().validate_clog(clog_dir)
        results = []
        results_text = []


        if clog_type == 'instagram-json':
            # Valid Instagram JSON chatlog
            df = FileManager().parse_insta_json(clog_dir)
            for _, row in df.iterrows():
                message = row['message']
                result = GroomingDetector().detect_grooming(message)
                if result is not None:
                    results.append(result)
                    results_text.append(message)
        elif clog_type == 'snapchat-json':
            # Valid Snapchat JSON chatlog
            sender_df_tuples = FileManager().parse_snap_json(clog_dir)
            for sender, df in sender_df_tuples:
                for _, row in df.iterrows():
                    message = row['message']
                    result = GroomingDetector().detect_grooming(message)
                    if result is not None:
                        results.append(result)
                        results_text.append(message)
        elif clog_type == 'plaintext':
            # Plaintext chat log
            text = FileManager().parse_txt_file(clog_dir)
            for line in text.splitlines():
                result = GroomingDetector().detect_grooming(line)
                if result is not None:
                    results.append(result)
                    results_text.append(line)
        else:
            # Invalid format can't parse it
            logging.error(f"Unable to detect grooming in {os.path.basename(clog_dir)}")
            messagebox.showerror("Error", f"Unable to detect grooming, please select a chat log to detect grooming in")
            return

        # Display popup with detected instances of grooming
        clog_name = self.view.clog_select.get()
        if len(results) == 0:
            logging.info(f"No instances of grooming to display in '{clog_name}'")
            messagebox.showinfo("NO GROOMING DETECTED", "No instances of grooming were found")
        else:
            logging.info(f"Displaying {len(results)} instances of potential grooming in '{clog_name}'")
            popup = DetectedGroomingPopup(results=results, master=self.view)
            popup.bind_highlight(lambda e: self.highlight_gd_text(results_text, popup))


    def load(self):
        # Reset selection
        self.view.clog_select.set('Select a chat log to examine')
        self.view.media_select.set('Select a media file to examine')
        # Reset clog viewer
        self.view.reset_clog_view_box()
        # Reset media flag button
        self.view.flag_media_button.configure("FLAG MEDIA FILE")

    def highlight_gd_text(self, results_text, popup):
        """
        Logic for highlighting detected grooming text in the CLog view
        :param results_text:
        :return:
        """
        popup.destroy()

        # Formulate regex to search for all instances of grooming at the same time
        search_pattern = '|'.join(map(re.escape, results_text))

        # Perform the search
        self.search(search_pattern)
