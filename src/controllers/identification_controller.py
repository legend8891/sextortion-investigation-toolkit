import logging
import re
from asyncio import Event
from datetime import datetime
from tkinter import messagebox
import customtkinter
from src.models.activitylog import ActivityLogModel
from src.models.case import CaseModel
from src.models.incident import IncidentModel
from src.models.victim_suspect import SuspectModel, VictimModel
from src.views.identification_view import IdentificationView
from src.views.ui_components.popups import SuspectPopup, VictimPopup
logging.basicConfig(level=logging.INFO)


class IdentificationController:
    """
    Controller for the Identification tab
    """

    def __init__(self, view: IdentificationView) -> None:
        # Identification view
        self.view = view

        # Identification tab bindings
        self.view.victim_add.configure(command=self.add_victim)
        self.view.suspect_add.configure(command=self.add_suspect)
        self.view.victim_profile_widget.edit_button.configure(command=self.victim_edit)
        self.view.suspect_profile_widget.edit_button.configure(command=self.suspect_edit)
        self.view.sextortion_type.configure(command=self.select_type)
        self.view.threats_entry.configure(command=self.select_threats)
        self.view.demands_entry.configure(command=self.select_demands)
        self.view.start_button.configure(command=self.submit_start_date_time)
        self.view.end_button.configure(command=self.submit_end_date_time)

    def add_victim(self, event: Event = None) -> None:
        """
        Logic for editing victim profile
        :param event:
        :return:
        """
        logging.info('Editing victim profile')

        victim_popup = VictimPopup(self.view)
        victim_popup.bind_submit(lambda e: self.create_victim(victim_popup, True, e))

    def add_suspect(self, event: Event = None) -> None:
        """
        Logic for editing suspect profile
        :param event:
        :return:
        """
        logging.info('Editing suspect profile')

        suspect_popup = SuspectPopup(self.view)
        suspect_popup.bind_submit(lambda e: self.create_suspect(suspect_popup, True, e))

    def create_suspect(self, popup, new: bool, event: Event = None) -> None:
        """
        Logic for creating suspect from fields
        :param new: Flag to determine if activity log says new or edits made
        :param popup:
        :param event:
        :return:
        """
        logging.info('Suspect profile submitted, gathering fields')

        # Gather fields from popup
        name = popup.name_field_1.get() + " " + popup.name_field_2.get()
        dob = popup.dob_field.get()
        nationality = popup.nationality_field.get()
        special_considerations = popup.considerations_field.get()
        address = popup.address_field.get()
        email = popup.email_field.get()
        phone = popup.phone_field.get()
        profiles = popup.profiles_field.get()
        screen_names = popup.screen_names_field.get()
        school = popup.school_field.get()
        occupation = popup.occupation_field.get()
        business_address = popup.business_address_field.get()
        relationship_to_victim = popup.victim_relationship_field.get()
        additional_info = popup.additional_info_field.get()

        # Check for required fields
        if name == "" or name is None:
            # Doesn't have required field
            messagebox.showerror('Error', 'Please enter required fields')
            return
        else:
            logging.info('Storing suspect fields in suspect object')

            # Update suspect model
            SuspectModel().set_fields(name,
                                      dob,
                                      nationality,
                                      special_considerations,
                                      address,
                                      email,
                                      phone,
                                      profiles,
                                      screen_names,
                                      school,
                                      occupation,
                                      business_address,
                                      relationship_to_victim,
                                      additional_info)

            # Save model to database
            SuspectModel().save()

            # Display suspect profile
            self.view.suspect_profile_widget.set_fields()
            self.view.suspect_button_to_widget()

            # Destroy popup
            popup.destroy()

            # Log activity
            if new:
                (ActivityLogModel().insert(f"New suspect added '{SuspectModel().name}'"))
            else:
                (ActivityLogModel().insert(f"Edits made to suspect '{SuspectModel().name}'"))

    def create_victim(self, popup, new: bool, event: Event = None) -> None:
        """
        Logic for creating victim from fields
        :param popup: victim popup
        :param event:
        :param new: Flag to determine if activity log says new or edits made
        :return:
        """
        logging.info('Victim profile submitted, gathering fields')

        # Gather fields from popup
        name = popup.name_field_1.get() + " " + popup.name_field_2.get()
        dob = popup.dob_field.get()
        nationality = popup.nationality_field.get()
        special_considerations = popup.considerations_field.get()
        address = popup.address_field.get()
        email = popup.email_field.get()
        phone = popup.phone_field.get()
        profiles = popup.profiles_field.get()
        screen_names = popup.screen_names_field.get()
        school = popup.school_field.get()
        additional_info = popup.additional_info_field.get()

        # Check for required fields
        if name == "" or name is None:
            # Doesn't have required field
            messagebox.showerror('Error', 'Please enter required fields')
            return
        else:
            # Has required field
            logging.info('Storing victim fields in victim object')

            # Update victim model with collected fields
            VictimModel().set_fields(name,
                                     dob,
                                     nationality,
                                     special_considerations,
                                     address,
                                     email,
                                     phone,
                                     profiles,
                                     screen_names,
                                     school,
                                     additional_info)

            # Save model to database
            VictimModel().save()

            # Display suspect profile
            self.view.victim_profile_widget.set_fields()
            self.view.victim_button_to_widget()

            # Destroy popup
            popup.destroy()

            # Log activity
            if new:
                (ActivityLogModel().insert(f"New victim added '{VictimModel().name}'"))
            else:
                (ActivityLogModel().insert(f"Edits made to victim '{VictimModel().name}'"))

    def victim_edit(self, event: Event = None) -> None:
        logging.info("Editing victim profile")

        # Create a victim popup for editing victim information
        victim_popup = VictimPopup(self.view)
        victim_popup.bind_submit(lambda e: self.create_victim(victim_popup, False, e))

        # Populate popup with existing victim fields
        victim_popup.update_fields()

    def suspect_edit(self, event: Event = None) -> None:
        logging.info("Editing suspect profile")

        # Create a suspect popup for editing suspect information
        suspect_popup = SuspectPopup(self.view)
        suspect_popup.bind_submit(lambda e: self.create_suspect(suspect_popup, False, e))

        # Populate popup with existing suspect fields
        suspect_popup.update_fields()

    def save_suspect(self):
        """
        Saves suspect model to DB
        :return:
        """
        SuspectModel().save()

    def save_victim(self) -> None:
        """
        Saves victim model to DB
        :return:
        """
        VictimModel().save()

    def save_incident(self) -> None:
        """
        Saves incident model to DB
        :return:
        """
        IncidentModel().save(CaseModel().case_number)

    def load(self) -> None:
        """
        Logic for loading identification tab for the current case
        :return:
        """
        logging.info("Loading Identification...")

        # Clear fields
        self.view.clear_fields()

        # Load victim and suspect
        VictimModel().update()
        SuspectModel().update()

        # Load incident details
        IncidentModel().update()

        # Update view
        self.view.victim_profile_widget.set_fields()
        self.view.suspect_profile_widget.set_fields()

        # Update if fields in model aren't None
        if not IncidentModel().type_of_sextortion is None:
            self.view.sextortion_type.set(IncidentModel().type_of_sextortion)
        if not IncidentModel().threats_made is None:
            self.view.threats_entry.set(IncidentModel().threats_made)
        if not IncidentModel().demands_made is None:
            self.view.demands_entry.set(IncidentModel().demands_made)

        if not IncidentModel().start_date_time is None:
            date_time = IncidentModel().start_date_time
            datetime_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
            converted_date = datetime_obj.strftime("%d/%m/%Y")
            self.view.start_date_field.insert(0, converted_date)
            converted_time = datetime_obj.strftime("%H:%M")
            self.view.start_time_field.insert(0, converted_time)

        if not IncidentModel().end_date_time is None:
            date_time = IncidentModel().end_date_time
            datetime_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
            converted_date = datetime_obj.strftime("%d/%m/%Y")
            self.view.end_date_field.insert(0, converted_date)
            converted_time = datetime_obj.strftime("%H:%M")
            self.view.end_time_field.insert(0, converted_time)

        if not SuspectModel().is_empty(): self.view.suspect_button_to_widget()
        if not VictimModel().is_empty(): self.view.victim_button_to_widget()

        # Need to add Loading start and end date times

    def select_type(self, event: Event = None) -> None:
        """
        Logic for handling selection of sextortion type
        :param event:
        :return:
        """

        # Get currently entered type and prev type
        prev_sextortion_type = IncidentModel().type_of_sextortion
        sextortion_type = self.view.sextortion_type.get()
        logging.info(f"Sextortion type selected: {sextortion_type} \n Previous type: {prev_sextortion_type}")

        # Has type been changed or still the same?
        unchanged = prev_sextortion_type == sextortion_type

        # If nothing is selected or same option selected again then ignore it, otherwise accept it
        if sextortion_type == "" or sextortion_type is None or sextortion_type == "--Select Sextortion Type--" or unchanged:
            logging.info("Invalid sextortion type selected or same as previous value - this will not be saved")
        else:
            if sextortion_type == "Other":
                logging.info("Other selected, providing input dialog box")
                dialog = customtkinter.CTkInputDialog(text="Enter Sextortion Type", title="Sextortion Type")
                other_type = dialog.get_input()
                IncidentModel().type_of_sextortion = other_type
                self.view.sextortion_type.set(other_type)
            else:
                IncidentModel().type_of_sextortion = sextortion_type

            # Save model state
            IncidentModel().save(CaseModel().case_number)

            # Log activity
            (ActivityLogModel().
             insert(f"Sextortion type '{IncidentModel().type_of_sextortion}' selected"))

    def select_threats(self, event: Event = None) -> None:
        """
        Logic for handling selection of threats
        :param event:
        :return:
        """

        # Get currently entered threats and prev threats
        prev_threats = IncidentModel().threats_made
        threats = self.view.threats_entry.get()
        logging.info(f"Threats selected: {threats} \n Previous type: {prev_threats}")

        # Has the threats changed or still the same?
        unchanged = prev_threats == threats

        # Same checks as with type
        if threats == "" or threats is None or threats == "--Select Threats--" or unchanged:
            logging.info("Invalid threats selected or same as previous value - this will not be saved")
        else:
            if threats == "Other":
                logging.info("Other selected, providing input dialog box")
                dialog = customtkinter.CTkInputDialog(text="Enter Threats", title="Threats")
                other_type = dialog.get_input()
                IncidentModel().threats_made = other_type
                self.view.threats_entry.set(other_type)
            else:
                IncidentModel().threats_made = threats

            # Save model state
            IncidentModel().save(CaseModel().case_number)

            # Log activity
            (ActivityLogModel().
             insert(f"Threat '{IncidentModel().threats_made}' selected"))

    def select_demands(self, event: Event = None) -> None:
        """
        Logic for handling selection of demands
        :param event:
        :return:
        """

        # Get currently entered demands and prev demands
        prev_demands = IncidentModel().demands_made
        demands = self.view.demands_entry.get()
        logging.info(f"Threats selected: {demands} \n Previous type: {prev_demands} \n")

        # Has the demands changed or still the same?
        unchanged = prev_demands == demands

        # Same checks as with type
        if demands == "" or demands is None or demands == "--Select Demands--" or unchanged:
            logging.info("Invalid demands selected or same as previous value - this will not be saved")
        else:
            if demands == "Other":
                logging.info("Other selected, providing input dialog box")
                dialog = customtkinter.CTkInputDialog(text="Enter Demands", title="Demands")
                other_type = dialog.get_input()
                IncidentModel().demands_made = other_type
                self.view.demands_entry.set(other_type)
            else:
                IncidentModel().demands_made = demands

            # Save model state
            IncidentModel().save(CaseModel().case_number)

            # Log activity
            (ActivityLogModel().
             insert(f"Demand '{IncidentModel().demands_made}' selected"))

    def submit_start_date_time(self, event: Event = None) -> None:
        """
        Logic for handling start date time submission
        :param event:
        :return:
        """
        # Previous value
        prev_date_time = IncidentModel().start_date_time

        # Raw date in format DD/MM/YYYY
        raw_date = self.view.start_date_field.get()
        # Raw time in format HH:MM
        raw_time = self.view.start_time_field.get()

        # Validate inputs
        if not self.validate_date(raw_date):
            messagebox.showinfo(title="Error", message="Invalid date format. Ensure date format is DD/MM/YYYY")
            return
        if not self.validate_time(raw_time):
            messagebox.showinfo(title="Error", message="Invalid time format. Ensure date format is HH:MM")
            return

        # Convert raw date into required ISO8601 format - YYYY-MM-DD HH:MM:SS.SSS
        date_obj = datetime.strptime(raw_date, "%d/%m/%Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        formatted_date_time = f"{formatted_date} {raw_time}"

        # Check date time isn't the same
        if prev_date_time == formatted_date_time:
            logging.info("Date time hasn't changed - this will not be saved again ")
            return

        # Store new date time
        IncidentModel().start_date_time = formatted_date_time
        IncidentModel().save(CaseModel().case_number)

        # Log activity
        (ActivityLogModel().
         insert(f"Incident start date time updated '{IncidentModel().start_date_time}'"))

    def submit_end_date_time(self, event: Event = None) -> None:
        """
        Logic for handling end date time submission
        :param event:
        :return:
        """
        """
           Logic for handling start date time submission
           :param event:
           :return:
           """
        # Previous value
        prev_date_time = IncidentModel().end_date_time

        # Raw date in format DD/MM/YYYY
        raw_date = self.view.end_date_field.get()
        # Raw time in format HH:MM
        raw_time = self.view.end_time_field.get()

        # Validate inputs
        if not self.validate_date(raw_date):
            messagebox.showinfo(title="Error", message="Invalid date format. Ensure date format is DD/MM/YYYY")
            return
        if not self.validate_time(raw_time):
            messagebox.showinfo(title="Error", message="Invalid time format. Ensure date format is HH:MM")
            return

        # Convert raw date into required ISO8601 format - YYYY-MM-DD HH:MM:SS.SSS
        date_obj = datetime.strptime(raw_date, "%d/%m/%Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        formatted_date_time = f"{formatted_date} {raw_time}"

        # Check date time isn't the same
        if prev_date_time == formatted_date_time:
            logging.info("Date time hasn't changed - this will not be saved again ")
            return

        # Store new date time
        IncidentModel().end_date_time = formatted_date_time
        IncidentModel().save(CaseModel().case_number)

        # Log activity
        (ActivityLogModel().
         insert(f"Incident end date time updated '{IncidentModel().end_date_time}'"))

    def validate_date(self, raw_date):
        """
        Helper function to validate date input
        :return:
        """
        # Define a regular expression pattern for the date format DD/MM/YYYY
        date_pattern = r'\d{2}/\d{2}/\d{4}'
        # Check if the raw date matches the pattern
        if re.match(date_pattern, raw_date):
            return True
        else:
            return False

    def validate_time(self, raw_time):
        """
        Helper function to validate time input
        :return:
        """
        # Define a regular expression pattern for the time format HH:MM
        time_pattern = r'\d{2}:\d{2}'
        # Check if the raw time matches the pattern
        if re.match(time_pattern, raw_time):
            return True
        else:
            return False
