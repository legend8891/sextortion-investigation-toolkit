import os
from fpdf import FPDF
from src.models.case import CaseModel
from src.models.flags import FlagManager
from src.models.incident import IncidentModel
from src.models.victim_suspect import VictimModel, SuspectModel
from src.utility.utility import FileManager, DatabaseManager


class PDFManager:
    """
    Utility class for creating PDF reports
    """

    __instance = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(PDFManager, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

    @staticmethod
    def create_pdf() -> None:
        """
        Creates PDF report
        :return:
        """
        # Create instance of FPDF class
        pdf = FPDF('P', 'mm', 'Legal', 'case_number')

        # Add a page
        pdf.add_page()

        # Title
        title = CaseModel().case_name + " Report"
        pdf.set_font('helvetica', 'B', 20)
        title_width = pdf.get_string_width(title) + 6
        doc_width = pdf.w
        pdf.set_x((doc_width - title_width) / 2)
        pdf.set_line_width(1)
        pdf.cell(title_width, 10, title, border=1, align='C')
        pdf.ln(10)

        # Case Information Heading
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, "Case Information", ln=True, align='L')
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 10, text=f"Case Name: {CaseModel().case_name}", ln=True)
        pdf.cell(0, 10, text=f"Referral Source: {CaseModel().referral_source}", ln=True)
        pdf.cell(0, 10, text=f"Case Directory: {FileManager().case_directory}", ln=True)
        pdf.ln(10)

        # Investigators Heading
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, "Investigators", ln=True, align='L')
        investigators = DatabaseManager().fetch_all_investigators()
        pdf.set_font('helvetica', '', 10)
        for investigator in investigators:
            pdf.cell(0, 10, text=f"Name: {investigator[1] + ' ' + investigator[2]}", ln=True)
            pdf.cell(0, 10, text=f"Phone: {investigator[3]}", ln=True)
            pdf.cell(0, 10, text=f"Email: {investigator[4]}", ln=True)
            pdf.ln(10)

        # Victim Information Heading
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, "Victim Information", ln=True, align='L')
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 10, text=f"Name: {VictimModel().name}", ln=True)
        pdf.cell(0, 10, text=f"DoB: {VictimModel().dob}", ln=True)
        pdf.cell(0, 10, text=f"Nationality: {VictimModel().nationality}", ln=True)
        pdf.cell(0, 10, text=f"Special Considerations: {VictimModel().special_considerations}", ln=True)
        pdf.cell(0, 10, text=f"Address: {VictimModel().address}", ln=True)
        pdf.cell(0, 10, text=f"Email: {VictimModel().email}", ln=True)
        pdf.cell(0, 10, text=f"Phone: {VictimModel().phone}", ln=True)
        pdf.cell(0, 10, text=f"Profiles: {VictimModel().profiles}", ln=True)
        pdf.cell(0, 10, text=f"Screen Names: {VictimModel().screen_names}", ln=True)
        pdf.cell(0, 10, text=f"School: {VictimModel().school}", ln=True)
        pdf.cell(0, 10, text=f"Additional Info: {VictimModel().additional_info}", ln=True)
        pdf.ln(10)

        # Suspect Information Heading
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, "Suspect Information", ln=True, align='L')
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 10, text=f"Name: {SuspectModel().name}", ln=True)
        pdf.cell(0, 10, text=f"DoB: {SuspectModel().dob}", ln=True)
        pdf.cell(0, 10, text=f"Nationality: {SuspectModel().nationality}", ln=True)
        pdf.cell(0, 10, text=f"Special Considerations: {SuspectModel().special_considerations}", ln=True)
        pdf.cell(0, 10, text=f"Address: {SuspectModel().address}", ln=True)
        pdf.cell(0, 10, text=f"Email: {SuspectModel().email}", ln=True)
        pdf.cell(0, 10, text=f"Phone: {SuspectModel().phone}", ln=True)
        pdf.cell(0, 10, text=f"Profiles: {SuspectModel().profiles}", ln=True)
        pdf.cell(0, 10, text=f"Screen Names: {SuspectModel().screen_names}", ln=True)
        pdf.cell(0, 10, text=f"School: {SuspectModel().school}", ln=True)
        pdf.cell(0, 10, text=f"Occupation: {SuspectModel().occupation}", ln=True)
        pdf.cell(0, 10, text=f"Business Address: {SuspectModel().business_address}", ln=True)
        pdf.cell(0, 10, text=f"Additional Info: {SuspectModel().additional_info}", ln=True)
        pdf.ln(10)

        # Incident Information Heading
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, "Incident Information", ln=True, align='L')
        pdf.set_font('helvetica', '', 10)
        pdf.cell(0, 10, text=f"Sextortion Type: {IncidentModel().type_of_sextortion}", ln=True)
        pdf.cell(0, 10, text=f"Threats: {IncidentModel().threats_made}", ln=True)
        pdf.cell(0, 10, text=f"Demands: {IncidentModel().demands_made}", ln=True)
        pdf.cell(0, 10, text=f"Start: {IncidentModel().start_date_time}", ln=True)
        pdf.cell(0, 10, text=f"End: {IncidentModel().end_date_time}", ln=True)
        pdf.ln(10)

        # Flagged Chat Logs
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, "Flagged Chat Logs", ln=True, align='L')
        flagged_clogs = FlagManager().load_flagged_clogs()
        for flagged_clog in flagged_clogs:
            file_name = flagged_clog[0]
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(0, 10, text=file_name, ln=True)
            pdf.set_font('helvetica', '', 10)
            pdf.cell(0, 10, text="Flagged Text: ", ln=True)
            flagged_texts = FlagManager().load_flagged_text(file_name)
            for flagged_text in flagged_texts:
                pdf.cell(0, 10, text=flagged_text, ln=True)
            clog_comments = DatabaseManager().fetch_evidence_desc_by_file_name(file_name)[0]
            pdf.cell(0, 10, text=f"Comments: {clog_comments}", ln=True)
        pdf.ln(10)

        # Flagged media here
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, "Flagged Media Files", ln=True, align='L')
        flagged_media = FlagManager().load_flagged_media_files()
        for media_file in flagged_media:
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(0, 10, text=media_file, ln=True)
            file_path = os.path.join(FileManager().case_directory, 'evidence', 'media', media_file)
            file_extension = os.path.splitext(media_file)[1]
            if file_extension in [".mp4", ".mov", ".avi", ".mkv"]:
                # Is video
                image = FileManager().generate_thumbnail(file_path, width=300, height=200)
            else:
                # Is photo
                image = file_path
            pdf.image(image, w=50, h=50)  # Adjust the path and dimensions as needed
            pdf.set_font('helvetica', '', 10)
            media_comments = DatabaseManager().fetch_evidence_desc_by_file_name(media_file)[0]
            pdf.cell(0, 10, text=f"Comments: {media_comments}", ln=True)
            # EXIF
            exif = FileManager().extract_exif(file_path)
            if not exif == 'no exif found':
                pdf.cell(0, 10, text=f"EXIF:", ln=True)
                lines = exif.splitlines()
                for line in lines:
                    pdf.cell(0, 10, text=line, ln=True)
        # Save the PDF to a file
        pdf.output(os.path.join(FileManager().case_directory, 'reports', f"{CaseModel().case_name}-report.pdf"))
