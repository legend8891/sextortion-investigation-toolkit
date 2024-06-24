import logging
import os
from asyncio import Event
from tkinter import filedialog
from tkinter import messagebox
from src.controllers.analysis_controller import AnalysisController
from src.controllers.collection_controller import CollectionController
from src.controllers.examination_controller import ExaminationController
from src.controllers.identification_controller import IdentificationController
from src.controllers.preservation_controller import PreservationController
from src.models.activitylog import ActivityLogModel
from src.models.case import CaseModel
from src.models.investigator import InvestigatorModel
from src.utility.utility import FileManager, DatabaseManager
from src.views.analysis_view import AnalysisView
from src.views.collection_view import CollectionView
from src.views.examination_view import ExaminationView
from src.views.identification_view import IdentificationView
from src.views.main_view import MainView
from src.views.preservation_view import PreservationView
from src.views.ui_components.popups import CasePopup, InvestigatorPopup
logging.basicConfig(level=logging.INFO)


class MainController:
    """
    Controller for the Main application view
    """
    def __init__(self, view: MainView) -> None:
        # Holds currently open case directory
        self.case_directory = None

        # MainView
        self.view = view

        # Other case manager bindings
        self.view.button_open.configure(command=self.open_case)
        self.view.button_new.configure(command=self.new_case)
        self.view.investigator_selector.configure(command=self.select_investigator)
        self.view.add_investigator_button.configure(command=self.create_investigator_popup)

        # Create identification tab view and controller
        self.identification_view = IdentificationView(master=self.view.tabs_view.tab("Identification"))
        self.identification_controller = IdentificationController(self.identification_view)

        # Create collection tab view and controller
        self.collection_view = CollectionView(master=self.view.tabs_view.tab("Collection"))
        self.collection_controller = CollectionController(self.collection_view)

        # Create preservation tab view and controller
        self.preservation_view = PreservationView(master=self.view.tabs_view.tab("Preservation"))
        self.preservation_controller = PreservationController(self.preservation_view)

        # Create examination tab view and controller
        self.examination_view = ExaminationView(master=self.view.tabs_view.tab("Examination"))
        self.examination_controller = ExaminationController(self.examination_view)

        # Create analysis tab view and controller
        self.analysis_view = AnalysisView(master=self.view.tabs_view.tab("Analysis"))
        self.analysis_controller = AnalysisController(self.analysis_view)

        # Don't show tabs until a case is loaded
        self.view.hide_tabs()

        # Temporary store of investigatrs
        self.investigators = None

    def handle_case_state(self):
        """
        Checks if case is open and shows/hides tabs accordingly
        :return:
        """
        if self.case_directory:
            # If there is a current directory then show the tabs
            logging.info("Case directory {} found, showing tabs".format(self.case_directory))
            self.view.show_tabs()
        else:
            # If there is no current directory then don't show the tabs
            logging.info("No case directory found, hiding tabs")
            self.view.hide_tabs()

    def create_folders_database(self, case_name, base_directory) -> None:
        """
        Creates basic directory structure and local database file
        :return:
        """
        # The full directory path for the case
        logging.info('Creating case directory structure')
        self.case_directory = os.path.join(base_directory, case_name)

        # Creates directory structure
        FileManager().setup_directories(self.case_directory)

        # Creates local database file
        logging.info('Creating database file and tables')
        DatabaseManager().create_tables(str(self.case_directory))

    def new_case(self, event: Event = None) -> None:
        """
        Logic for creating and binding new case popup
        :param event:
        :return:
        """
        # Create instance of popup
        case_popup = CasePopup(self.view)

        # Bind popup submit to case creation
        case_popup.bind_submit(lambda event_1: self.create_case(case_popup, event_1))

    def create_case(self, case_popup, event: Event = None) -> None:
        """
        Logic for creating a new case
        :param case_popup: case popup instance used to configure current case
        :param event:
        :return:
        """
        logging.info("Starting case creation process")

        # Get all fields filled by user
        case_number = case_popup.case_number_field.get()
        case_name = case_popup.case_name_entry.get()
        referral_source = case_popup.case_referral_entry.get()
        investigators = case_popup.investigators
        current_investigator = case_popup.current_investigator
        base_directory = case_popup.base_directory

        # Check all fields filled in and valid
        if case_number == "" or not case_number.isnumeric():
            # Invalid case number
            logging.error("Invalid case number")
            messagebox.showerror("ERROR", "INVALID CASE NUMBER")
            return
        if case_name == "":
            # Invalid case name
            logging.error("Invalid case name")
            messagebox.showerror("ERROR", "INVALID CASE NAME")
            return
        if referral_source == "":
            # Invalid referral source
            logging.error("Invalid referral source")
            messagebox.showerror("ERROR", "INVALID REFERRAL SOURCE")
            return
        if investigators == [[]]:
            # Investigators array empty for some reason
            logging.error("No investigators")
            messagebox.showerror("ERROR", "NO INVESTIGATORS FOUND")
            return
        if current_investigator == "":
            # No current investigator
            logging.error("No current investigator")
            messagebox.showerror("ERROR", "NO CURRENT INVESTIGATOR SELECTED: Click on an investigator from"
                                          " the list to set as current investigator. This can be changed later.")
            return
        if base_directory is None:
            # No directory selected
            logging.error("No directory selected")
            messagebox.showerror("ERROR", "NO DIRECTORY SELECTED")
            return


        # Make directories and db
        self.create_folders_database(case_name=case_name, base_directory=base_directory)

        # Make all entered investigators
        for investigator in investigators:
            logging.info('New investigator instance: {} {}'.format(investigator[0], investigator[1]))
            InvestigatorModel(
                first_name=investigator[0],
                last_name=investigator[1],
                phone=investigator[2],
                email=investigator[3]
            ).save()

        # Make the case
        logging.info('Getting current investigator: {}'.format(current_investigator))
        firstname, surname = current_investigator.split()
        investigator_id = DatabaseManager().fetch_investigator_by_name(first_name=firstname, last_name=surname)[0]
        logging.info('Creating case and saving to database')
        CaseModel().set_fields(
            case_number=case_number,
            case_name=case_name,
            referral_source=referral_source,
            investigator_id=investigator_id
        )
        CaseModel().save()

        # Destroy case popup
        case_popup.destroy()

        # Show tabs
        self.handle_case_state()

        # Update investigators dropdown
        self.update_investigators_dropdown()

        # Load all tabs
        self.load()

        # Log activity
        (ActivityLogModel().
         insert(f"Case {CaseModel().case_number} {CaseModel().case_name} created by {DatabaseManager().
                fetch_current_investigator_name()}"))

    def open_case(self, event: Event = None) -> None:
        """
        Logic for opening existing case
        :param event:
        :return:
        """
        logging.info("Choosing case directory to open")

        # Start navigation at the tool directory
        initial_directory = os.getcwd()

        # Allow the user to select a directory to open
        selected_directory = filedialog.askdirectory(initialdir=initial_directory)

        # Check a directory has been chosen
        if (selected_directory is None) or (selected_directory == ""):
            logging.info("User closed or canceled directory selection window")
            return

        logging.info('Chosen directory to open: {}'.format(selected_directory))

        # Check for evidence folder in directory
        evidence_folder = os.path.join(selected_directory, 'evidence')
        if os.path.exists(evidence_folder) and os.path.isdir(evidence_folder):
            logging.info('Evidence folder found: {}'.format(evidence_folder))
        else:
            logging.error('Evidence folder not found: {}'.format(evidence_folder))
            messagebox.showerror('ERROR', 'MISSING EVIDENCE FOLDER')
            return

        # Check for reports folder in directory
        reports_folder = os.path.join(selected_directory, 'reports')
        if os.path.exists(reports_folder) and os.path.isdir(reports_folder):
            logging.info('Reports folder found: {}'.format(reports_folder))
        else:
            logging.error('Reports folder not found: {}'.format(reports_folder))
            messagebox.showerror('ERROR', 'MISSING REPORTS FOLDER')
            return

        # Check for database file in directory
        db_file = os.path.join(selected_directory, 'cst.db')
        if os.path.exists(db_file) and os.path.isfile(db_file):
            logging.info('Database file found: {}'.format(db_file))
        else:
            logging.error('Database file not found: {}'.format(db_file))
            messagebox.showerror('ERROR', "MISSING DATABASE FILE 'cst.db'")
            return

        # Log activity
        (ActivityLogModel().
         insert(f"Case {CaseModel().case_number} {CaseModel().case_name} closed"))

        # Open case if all required files and folders are found
        logging.info('Case Valid')
        # Track current case directory
        self.case_directory = selected_directory
        # Creates tables if they don't exist, else updates database file location in database manager
        DatabaseManager().create_tables(self.case_directory)
        FileManager().case_directory = self.case_directory

        # Load state for each tab
        self.load()

        # Log activity
        (ActivityLogModel().
         insert(f"Case {CaseModel().case_number} {CaseModel().case_name} opened by "
                f"{DatabaseManager().fetch_current_investigator_name()}"))

    def create_investigator_popup(self, event: Event = None) -> None:
        """
        Logic for showing investigator popup
        :param event:
        :return:
        """
        logging.info('Showing investigator popup')
        popup = InvestigatorPopup(self.view)
        popup.bind_submit(lambda event_1: self.add_investigator(popup, event_1))

    def add_investigator(self, popup: InvestigatorPopup, event: Event = None) -> None:
        """
        Logic for creating a new investigator
        :param popup:
        :param event:
        :return:
        """
        logging.info('Adding new investigator')
        name_1 = popup.name_field_1.get()
        name_2 = popup.name_field_2.get()
        phone = popup.phone_field.get()
        email = popup.email_field.get()
        logging.info('New investigator instance: {} {}'.format(name_1, name_2))

        # Make investigator model instance
        InvestigatorModel(
            first_name=name_1,
            last_name=name_2,
            phone=phone,
            email=email
        ).save()

        self.update_investigators_dropdown()
        popup.destroy()

    def update_investigators_dropdown(self):
        """
        Logic for updating investigators dropdown box with up-to-date names
        :return:
        """
        logging.info('Updating investigators dropdown')

        # Get all investigator entries
        self.investigators = DatabaseManager().fetch_all_investigators()

        # Extract just the names
        names = []
        for investigator in self.investigators:
            first_name = investigator[1]  # First name at index 1
            surname = investigator[2]  # Surname at index 2
            full_name = f"{first_name} {surname}"
            names.append(full_name)

        # Update dropdown box with names
        self.view.investigator_selector.configure(values=names)

        # Select current investigator
        current_investigator = DatabaseManager().fetch_investigator_by_id(CaseModel().investigator_id)
        self.view.investigator_selector.set(f"{current_investigator[1]} {current_investigator[2]}")

    def select_investigator(self, event: Event = None) -> None:
        """
        Logic for handling selection of current investigator
        :param event:
        :return:
        """
        # Get the name chosen by the user
        chosen_name = self.view.investigator_selector.get()
        if chosen_name is None:
            return

        logging.info('Selected investigator: {}'.format(chosen_name))

        # Get all the details for the investigator
        for investigator in self.investigators:
            first_name, last_name = investigator[1], investigator[2]
            if f"{first_name} {last_name}" == chosen_name:
                logging.info('Selected investigator valid')
                chosen_investigator = investigator
                investigator_id = chosen_investigator[0]
                CaseModel().investigator_id = investigator_id
                CaseModel().save()

                # Log activity
                (ActivityLogModel().
                 insert(f"Current investigator changed to {DatabaseManager().fetch_current_investigator_name()}"))

    def run(self) -> None:
        """
        Run app
        :return:
        """
        self.view.mainloop()

    def load(self):
        """
        Logic for loading all tabs
        :return:
        """
        CaseModel().update()
        self.identification_controller.load()
        self.collection_controller.load()
        self.preservation_controller.load()
        self.examination_controller.load()
        self.analysis_controller.load()

        # Show tabs for current case
        self.handle_case_state()

        # Update investigators dropdown
        self.update_investigators_dropdown()
