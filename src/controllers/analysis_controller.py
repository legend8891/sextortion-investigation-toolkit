import logging
import os
from src.models.activitylog import ActivityLogModel
from src.models.flags import FlagManager
from src.utility.pdfmanager import PDFManager
from src.utility.utility import DatabaseManager, FileManager
from src.views.analysis_view import AnalysisView, FlaggedClogView, FlaggedMediaView

logging.basicConfig(level=logging.INFO)


class AnalysisController:
    """
    Controller for the Analysis tab
    """

    def __init__(self, view: AnalysisView) -> None:
        # Analysis view
        self.view = view

        # Linking analysis controller to flag manager so flagged files can change as user flags/unflags
        FlagManager().controller = self

        # Bind selecting file in either
        self.view.clogs_button.configure(command=self.clogs_view)
        self.view.media_button.configure(command=self.media_view)
        self.view.report_button.configure(command=self.generate_report)

    def clogs_view(self):
        """
        Logic for displaying a summary of flagged chat logs
        :return:
        """
        self.view.highlight_button('clogs')
        self.view.clear_frame()
        flagged_clogs = FlagManager().load_flagged_clogs()
        for flagged_clog in flagged_clogs:
            # File name
            file_name = flagged_clog[0]
            clogs_view = FlaggedClogView(self.view.frame, file_name=file_name)
            # Flagged text from file
            flagged_texts = FlagManager().load_flagged_text(file_name)
            clogs_view.add_flagged_text(flagged_texts)
            # Comments
            clog_comments = DatabaseManager().fetch_evidence_desc_by_file_name(file_name)[0]
            if clog_comments is not None:
                clogs_view.add_comments(clog_comments)

    def media_view(self):
        """
        Logic for displaying a summary of flagged media files
        :return:
        """
        self.view.highlight_button('media')
        self.view.clear_frame()
        flagged_media = FlagManager().load_flagged_media_files()
        for media_file in flagged_media:
            file_path = os.path.join(FileManager().case_directory, 'evidence', 'media', media_file)
            media_view = FlaggedMediaView(self.view.frame, file_name=media_file)
            # Comments
            media_comments = DatabaseManager().fetch_evidence_desc_by_file_name(media_file)[0]
            if media_comments is not None:
                media_view.add_comments(media_comments)
            # EXIF / Metadata
            exif = FileManager().extract_exif(file_path)
            meta = FileManager().extract_metadata(file_path)
            if exif == 'no exif found':
                exif = ''
            if meta == 'no metadata found':
                meta = ''
            else:
                # Only add a newline if exif is not 'no exif found'
                if exif != '':
                    exif += '\n'
            media_view.add_meta(exif + meta)

    def generate_report(self):
        """
        Logic for generating PDF summary of case
        :return:
        """
        self.view.highlight_button('report')
        PDFManager().create_pdf()
        # Log activity
        (ActivityLogModel().
         insert("Generated report"))

    def load(self):
        """
        Logic for resetting the flag summaries when loaded
        :return:
        """
        # Clear out the frame
        for frame in self.view.frame.winfo_children():
            frame.destroy()
