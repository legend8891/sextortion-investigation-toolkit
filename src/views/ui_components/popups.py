import logging
import os
import tkinter as tk
from tkinter import filedialog
from typing import Callable
import customtkinter
from CTkListbox import *
from customtkinter import CTkToplevel
from src.models.victim_suspect import VictimModel, SuspectModel

logging.basicConfig(level=logging.INFO)


class CasePopup(CTkToplevel):
    """
    Popup for creating and editing cases
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Window config
        self.title("Case Configuration")
        self.geometry("300x800")

        # Temp store of investigators and the current investigator
        self.investigators = []  # Array of investigator field arrays (2D)
        self.current_investigator = None  # Current investigator name

        self.base_directory = None

        # --------------------- Add components to popup ---------------------

        # Inside the scroll frame, add a frame to hold all components
        self.content_frame = customtkinter.CTkScrollableFrame(self)
        self.content_frame.pack(expand=True, fill="both")

        # Title
        self.label = customtkinter.CTkLabel(self.content_frame, text="Create New Case",
                                            font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label.pack(padx=20, pady=20)

        # ---- Case management box ----
        self.case_container = customtkinter.CTkFrame(self.content_frame, border_width=1)
        self.case_container.pack(padx=20, pady=(5, 20), expand=True, fill=tk.X)

        # Case number field
        self.case_label_1 = customtkinter.CTkLabel(self.case_container, text="Case Number",
                                                   font=customtkinter.CTkFont(size=15))
        self.case_label_1.pack(padx=20, pady=5)
        self.case_number_field = customtkinter.CTkEntry(self.case_container, placeholder_text="Enter Case Number")
        self.case_number_field.pack(padx=20, pady=5)

        # Case name field
        self.case_label_2 = customtkinter.CTkLabel(self.case_container, text="Case Name",
                                                   font=customtkinter.CTkFont(size=15))
        self.case_label_2.pack(padx=20, pady=5)
        self.case_name_entry = customtkinter.CTkEntry(self.case_container, placeholder_text="Enter Case Name")
        self.case_name_entry.pack(padx=20, pady=5)

        # Referral source field
        self.case_label_3 = customtkinter.CTkLabel(self.case_container, text="Referral Source",
                                                   font=customtkinter.CTkFont(size=15))
        self.case_label_3.pack(padx=20, pady=5)
        self.case_referral_entry = customtkinter.CTkEntry(self.case_container,
                                                          placeholder_text="Enter Referral Source (e.g., NCA)")
        self.case_referral_entry.pack(padx=20, pady=(5, 20))

        # Directory selection
        self.select_directory_button = customtkinter.CTkButton(self.case_container, text="Choose Directory",
                                                               font=customtkinter.CTkFont(),
                                                               command=self.choose_case_directory)
        self.select_directory_button.pack(padx=20, pady=(0, 20))
        self.selected_directory_label = customtkinter.CTkLabel(self.case_container, text="No Directory Selected",
                                                               wraplength=100)
        self.selected_directory_label.pack(padx=20, pady=(0, 20))

        # ---- Investigators box  ----

        # Investigators container
        self.investigators_frame = customtkinter.CTkFrame(self.content_frame, border_width=1)
        self.investigators_frame.pack(padx=20, pady=(5, 20), expand=True, fill=tk.X)

        # Investigators selection and adding more investigators
        self.case_label_4 = customtkinter.CTkLabel(self.investigators_frame, text="Investigators",
                                                   font=customtkinter.CTkFont(size=15))
        self.case_label_4.pack(padx=20, pady=5)

        # Case investigators scrollable list
        self.investigators_listbox = CTkListbox(self.investigators_frame)
        self.investigators_listbox.pack(fill="both", expand=True, padx=10, pady=10)

        # First name field
        self.invest_label_1 = customtkinter.CTkLabel(self.investigators_frame, text="First Name",
                                                     font=customtkinter.CTkFont(size=15))
        self.invest_label_1.pack(padx=20, pady=5)
        self.name_field_1 = customtkinter.CTkEntry(self.investigators_frame, placeholder_text="Enter First Name")
        self.name_field_1.pack(padx=20, pady=5)

        # Surname field
        self.invest_label_2 = customtkinter.CTkLabel(self.investigators_frame, text="Surname",
                                                     font=customtkinter.CTkFont(size=15))
        self.invest_label_2.pack(padx=20, pady=5)
        self.name_field_2 = customtkinter.CTkEntry(self.investigators_frame, placeholder_text="Enter Surname")
        self.name_field_2.pack(padx=20, pady=5)

        # Phone field
        self.invest_label_3 = customtkinter.CTkLabel(self.investigators_frame, text="Phone Number",
                                                     font=customtkinter.CTkFont(size=15))
        self.invest_label_3.pack(padx=20, pady=5)
        self.phone_field = customtkinter.CTkEntry(self.investigators_frame, placeholder_text="Enter Phone Number")
        self.phone_field.pack(padx=20, pady=5)

        # Email field
        self.invest_label_4 = customtkinter.CTkLabel(self.investigators_frame, text="Email",
                                                     font=customtkinter.CTkFont(size=15))
        self.invest_label_4.pack(padx=20, pady=5)
        self.email_field = customtkinter.CTkEntry(self.investigators_frame, placeholder_text="Enter Email")
        self.email_field.pack(padx=20, pady=5)

        self.investigator_button = customtkinter.CTkButton(self.investigators_frame, text="Add Investigator",
                                                           font=customtkinter.CTkFont(), command=self.add_investigator)
        self.investigator_button.pack(padx=20, pady=20)

        # ---- Case create ----
        self.create_case_button = customtkinter.CTkButton(self.content_frame, text="Create Case",
                                                          font=customtkinter.CTkFont(),
                                                          command=self.set_current_investigator)
        self.create_case_button.pack(padx=20, pady=(5, 20))

        # ---- Window closing ----
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # ---- Focus ----
        self.case_number_field.focus_set()

    def on_window_close(self) -> None:
        """
        Handle window closing
        :return:
        """
        close = tk.messagebox.askyesno(title="Warning",
                                       message="Warning: Case hasn't been created, progress will be lost, are you "
                                               "sure you want to continue?")
        if close:
            self.destroy()
        else:
            return

    def bind_investigator_select(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binding for selecting investigator
        :param callback:
        :return:
        """
        self.investigators_listbox.bind("<<ListboxSelect>>", callback)

    def bind_create_case(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binding for case creation button
        :param callback:
        :return:
        """
        self.create_case_button.bind("<Button-1>", callback)

    def bind_submit(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binding for submitting
        :param callback:
        :return:
        """
        self.create_case_button.bind("<Button-1>", callback)

    def choose_case_directory(self):
        """
        Selection of case directory to store all case files
        :return:
        """
        logging.info("Choosing case directory")
        initial_directory = os.getcwd()
        self.base_directory = filedialog.askdirectory(initialdir=initial_directory)
        if self.base_directory is not None:
            logging.info('Chosen directory: {}'.format(self.base_directory))
            self.selected_directory_label.configure(text=self.base_directory)
        else:
            logging.error('Chosen directory invalid: {}'.format(self.base_directory))
            self.selected_directory_label.configure(text="No Directory Selected")

    def add_investigator(self) -> None:
        """
        Add investigator to temporary storage and put name in listbox
        :return:
        """
        logging.info("Adding investigator to temporary storage")

        # Add to temp storage
        investigator = self.get_investigator_fields()
        self.investigators.append(investigator)

        # Put investigator name in listbox
        index = self.investigators_listbox.size()
        self.investigators_listbox.insert(index, investigator[0] + " " + investigator[1])

    def set_current_investigator(self) -> None:
        """
        Get the selected current investigator
        :return:
        """
        logging.info("Setting current investigator")
        self.current_investigator = self.investigators_listbox.get()

    def get_investigator_fields(self):
        """
        Get entry fields from investigator
        :return:
        """
        fields = [
            self.name_field_1.get(),
            self.name_field_2.get(),
            self.phone_field.get(),
            self.email_field.get(),
        ]
        return fields


class SuspectPopup(CTkToplevel):
    """
    Popup for creating suspect popup to configure suspect details
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Window config
        self.title("Suspect Profile")
        self.geometry("300x800")
        self.resizable(False, False)

        # Inside the scroll frame, add a frame to hold all components
        self.content_frame = customtkinter.CTkScrollableFrame(self)
        self.content_frame.pack(expand=True, fill="both")

        # Title
        customtkinter.CTkLabel(self.content_frame, text="Suspect Profile",
                               font=customtkinter.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Name
        customtkinter.CTkLabel(self.content_frame, text="First Name", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.name_field_1 = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter First Name")
        self.name_field_1.pack(padx=20, pady=5, fill=tk.X)

        customtkinter.CTkLabel(self.content_frame, text="Surname", font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.name_field_2 = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Surname")
        self.name_field_2.pack(padx=20, pady=5, fill=tk.X)

        # DOB
        customtkinter.CTkLabel(self.content_frame, text="Date of Birth",
                               font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.dob_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="DD/MM/YYYY")
        self.dob_field.pack(padx=20, pady=5, fill=tk.X)

        # Nationality
        customtkinter.CTkLabel(self.content_frame, text="Nationality",
                               font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.nationality_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Nationality")
        self.nationality_field.pack(padx=20, pady=5, fill=tk.X)

        # Special considerations
        customtkinter.CTkLabel(self.content_frame, text="Special Considerations",
                               font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.considerations_field = customtkinter.CTkEntry(self.content_frame,
                                                           placeholder_text="Enter Special Considerations")
        self.considerations_field.pack(padx=20, pady=5, fill=tk.X)

        # Address
        customtkinter.CTkLabel(self.content_frame, text="Address", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.address_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Address")
        self.address_field.pack(padx=20, pady=5, fill=tk.X)

        # Email
        customtkinter.CTkLabel(self.content_frame, text="Email", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.email_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Email Address")
        self.email_field.pack(padx=20, pady=5, fill=tk.X)

        # Phone
        customtkinter.CTkLabel(self.content_frame, text="Phone", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.phone_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Phone Number")
        self.phone_field.pack(padx=20, pady=5, fill=tk.X)

        # Online profiles
        customtkinter.CTkLabel(self.content_frame, text="Online Profiles",
                               font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.profiles_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Profiles")
        self.profiles_field.pack(padx=20, pady=5, fill=tk.X)

        # Screen names
        customtkinter.CTkLabel(self.content_frame, text="Screen Names",
                               font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.screen_names_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Screen Names")
        self.screen_names_field.pack(padx=20, pady=5, fill=tk.X)

        # School
        customtkinter.CTkLabel(self.content_frame, text="School", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.school_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter School")
        self.school_field.pack(padx=20, pady=5, fill=tk.X)

        # Occupation
        customtkinter.CTkLabel(self.content_frame, text="Occupation",
                               font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.occupation_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Occupation")
        self.occupation_field.pack(padx=20, pady=5, fill=tk.X)

        # Business address
        customtkinter.CTkLabel(self.content_frame, text="Business Address",
                               font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.business_address_field = customtkinter.CTkEntry(self.content_frame,
                                                             placeholder_text="Enter Business Address")
        self.business_address_field.pack(padx=20, pady=5, fill=tk.X)

        # Relationship to victim
        customtkinter.CTkLabel(self.content_frame, text="Relationship to Victim",
                               font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.victim_relationship_field = customtkinter.CTkEntry(self.content_frame,
                                                                placeholder_text="Enter Relationship to Victim")
        self.victim_relationship_field.pack(padx=20, pady=5, fill=tk.X)

        # Additional info
        customtkinter.CTkLabel(self.content_frame, text="Additional Information",
                               font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.additional_info_field = customtkinter.CTkEntry(self.content_frame,
                                                            placeholder_text="Enter Additional Info")
        self.additional_info_field.pack(padx=20, pady=5, fill=tk.X)

        # Submit button
        self.submit_button = customtkinter.CTkButton(self.content_frame, text="Submit",
                                                     font=customtkinter.CTkFont(size=15))
        self.submit_button.pack(padx=20, pady=(20, 5), fill=tk.X)

    def bind_submit(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binds submitting suspect details
        :param callback:
        :return:
        """
        self.submit_button.bind("<Button-1>", callback)

    def update_fields(self):
        """
        Populate popup with stored information
        :return:
        """
        logging.info("Updating suspect popup fields")

        suspect_model = SuspectModel()

        # Check if each attribute is not None before inserting
        if suspect_model.name is not None:
            name_1, name_2 = suspect_model.name.split(" ")
            self.name_field_1.insert(0, name_1)
            self.name_field_2.insert(0, name_2)
        if suspect_model.dob is not None:
            self.dob_field.insert(0, suspect_model.dob)
        if suspect_model.nationality is not None:
            self.nationality_field.insert(0, suspect_model.nationality)
        if suspect_model.special_considerations is not None:
            self.considerations_field.insert(0, suspect_model.special_considerations)
        if suspect_model.address is not None:
            self.address_field.insert(0, suspect_model.address)
        if suspect_model.email is not None:
            self.email_field.insert(0, suspect_model.email)
        if suspect_model.phone is not None:
            self.phone_field.insert(0, suspect_model.phone)
        if suspect_model.profiles is not None:
            self.profiles_field.insert(0, suspect_model.profiles)
        if suspect_model.screen_names is not None:
            self.screen_names_field.insert(0, suspect_model.screen_names)
        if suspect_model.school is not None:
            self.school_field.insert(0, suspect_model.school)
        if suspect_model.occupation is not None:
            self.occupation_field.insert(0, suspect_model.occupation)
        if suspect_model.business_address is not None:
            self.business_address_field.insert(0, suspect_model.business_address)
        if suspect_model.relationship_to_victim is not None:
            self.victim_relationship_field.insert(0, suspect_model.relationship_to_victim)
        if suspect_model.additional_info is not None:
            self.additional_info_field.insert(0, suspect_model.additional_info)


class VictimPopup(CTkToplevel):
    """
    Popup for configuring victim profile
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Window config
        self.title("Victim Profile")
        self.geometry("300x800")
        self.resizable(False, False)

        # Inside the scroll frame, add a frame to hold all components
        self.content_frame = customtkinter.CTkScrollableFrame(self)
        self.content_frame.pack(expand=True, fill="both")

        # Title
        customtkinter.CTkLabel(self.content_frame, text="Victim Profile",
                               font=customtkinter.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Name
        customtkinter.CTkLabel(self.content_frame, text="First Name", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.name_field_1 = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter First Name")
        self.name_field_1.pack(padx=20, pady=5, fill=tk.X)

        customtkinter.CTkLabel(self.content_frame, text="Surname", font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.name_field_2 = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Surname")
        self.name_field_2.pack(padx=20, pady=5, fill=tk.X)

        # DOB
        customtkinter.CTkLabel(self.content_frame, text="Date of Birth",
                               font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.dob_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="DD/MM/YYYY")
        self.dob_field.pack(padx=20, pady=5, fill=tk.X)

        # Nationality
        customtkinter.CTkLabel(self.content_frame, text="Nationality",
                               font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.nationality_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Nationality")
        self.nationality_field.pack(padx=20, pady=5, fill=tk.X)

        # Special considerations
        customtkinter.CTkLabel(self.content_frame, text="Special Considerations",
                               font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.considerations_field = customtkinter.CTkEntry(self.content_frame,
                                                           placeholder_text="Enter Special Considerations")
        self.considerations_field.pack(padx=20, pady=5, fill=tk.X)

        # Address
        customtkinter.CTkLabel(self.content_frame, text="Address", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.address_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Address")
        self.address_field.pack(padx=20, pady=5, fill=tk.X)

        # Email
        customtkinter.CTkLabel(self.content_frame, text="Email", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.email_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Email Address")
        self.email_field.pack(padx=20, pady=5, fill=tk.X)

        # Phone
        customtkinter.CTkLabel(self.content_frame, text="Phone", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.phone_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Phone Number")
        self.phone_field.pack(padx=20, pady=5, fill=tk.X)

        # Online profiles
        customtkinter.CTkLabel(self.content_frame, text="Online Profiles",
                               font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.profiles_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Profiles")
        self.profiles_field.pack(padx=20, pady=5, fill=tk.X)

        # Screen names
        customtkinter.CTkLabel(self.content_frame, text="Screen Names",
                               font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.screen_names_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter Screen Names")
        self.screen_names_field.pack(padx=20, pady=5, fill=tk.X)

        # School
        customtkinter.CTkLabel(self.content_frame, text="School", font=customtkinter.CTkFont(size=15)).pack(
            pady=5)
        self.school_field = customtkinter.CTkEntry(self.content_frame, placeholder_text="Enter School")
        self.school_field.pack(padx=20, pady=5, fill=tk.X)

        # Additional info
        customtkinter.CTkLabel(self.content_frame, text="Additional Information",
                               font=customtkinter.CTkFont(size=15)).pack(pady=5)
        self.additional_info_field = customtkinter.CTkEntry(self.content_frame,
                                                            placeholder_text="Enter Additional Info")
        self.additional_info_field.pack(padx=20, pady=5, fill=tk.X)

        # Submit button
        self.submit_button = customtkinter.CTkButton(self.content_frame, text="Submit",
                                                     font=customtkinter.CTkFont(size=15))
        self.submit_button.pack(padx=20, pady=(20, 5), fill=tk.X)

    def bind_submit(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binds submitting victim information
        :param callback:
        :return:
        """
        self.submit_button.bind("<Button-1>", callback)

    def update_fields(self):
        """
        Updates popup with model
        :return:
        """
        logging.info("Updating victim popup fields")
        victim_model = VictimModel()

        # Check if each attribute is not None before inserting
        if victim_model.name is not None:
            name_1, name_2 = victim_model.name.split(" ")
            self.name_field_1.insert(0, name_1)
            self.name_field_2.insert(0, name_2)
        if victim_model.dob is not None:
            self.dob_field.insert(0, victim_model.dob)
        if victim_model.nationality is not None:
            self.nationality_field.insert(0, victim_model.nationality)
        if victim_model.special_considerations is not None:
            self.considerations_field.insert(0, victim_model.special_considerations)
        if victim_model.address is not None:
            self.address_field.insert(0, victim_model.address)
        if victim_model.email is not None:
            self.email_field.insert(0, victim_model.email)
        if victim_model.phone is not None:
            self.phone_field.insert(0, victim_model.phone)
        if victim_model.profiles is not None:
            self.profiles_field.insert(0, victim_model.profiles)
        if victim_model.screen_names is not None:
            self.screen_names_field.insert(0, victim_model.screen_names)
        if victim_model.school is not None:
            self.school_field.insert(0, victim_model.school)
        if victim_model.additional_info is not None:
            self.additional_info_field.insert(0, victim_model.additional_info)


class InvestigatorPopup(CTkToplevel):
    """
    Popup for configuring investigator profile
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Window config
        self.title("New Investigator")
        self.geometry("200x400")
        self.resizable(False, False)

        # Investigators selection and adding more investigators
        self.title = customtkinter.CTkLabel(self, text="New Investigator",
                                            font=customtkinter.CTkFont(size=20, weight='bold'))
        self.title.pack(padx=20, pady=5, fill=tk.X)

        # First name field
        self.name_label_1 = customtkinter.CTkLabel(self, text="First Name",
                                                   font=customtkinter.CTkFont(size=15))
        self.name_label_1.pack(padx=20, pady=5, fill=tk.X)
        self.name_field_1 = customtkinter.CTkEntry(self, placeholder_text="Enter First Name")
        self.name_field_1.pack(padx=20, pady=5, fill=tk.X)

        # Surname field
        self.name_label_2 = customtkinter.CTkLabel(self, text="Surname",
                                                   font=customtkinter.CTkFont(size=15))
        self.name_label_2.pack(padx=20, pady=5, fill=tk.X)
        self.name_field_2 = customtkinter.CTkEntry(self, placeholder_text="Enter Surname")
        self.name_field_2.pack(padx=20, pady=5, fill=tk.X)

        # Phone field
        self.phone_label = customtkinter.CTkLabel(self, text="Phone Number",
                                                  font=customtkinter.CTkFont(size=15))
        self.phone_label.pack(padx=20, pady=5, fill=tk.X)
        self.phone_field = customtkinter.CTkEntry(self, placeholder_text="Enter Phone Number")
        self.phone_field.pack(padx=20, pady=5, fill=tk.X)

        # Email field
        self.email_label = customtkinter.CTkLabel(self, text="Email",
                                                  font=customtkinter.CTkFont(size=15))
        self.email_label.pack(padx=20, pady=5, fill=tk.X)
        self.email_field = customtkinter.CTkEntry(self, placeholder_text="Enter Email")
        self.email_field.pack(padx=20, pady=5, fill=tk.X)

        self.submit_button = customtkinter.CTkButton(self, text="Submit",
                                                     font=customtkinter.CTkFont())
        self.submit_button.pack(padx=20, expand=True, fill=tk.X)

    def bind_submit(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binds submitting investigator
        :param callback:
        :return:
        """
        self.submit_button.bind("<Button-1>", callback)


class EXIFPopup(CTkToplevel):
    """
    Popup for displaying EXIF data
    """

    def __init__(self, file_name, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry('400x400')
        self.title(f"{file_name} EXIF Data")

        self.title = customtkinter.CTkLabel(self, text=f"{file_name} EXIF Data", font=customtkinter.CTkFont(size=20))
        self.title.pack(padx=20, pady=10, fill='x', expand=False)

        self.data_dump = customtkinter.CTkTextbox(self, font=customtkinter.CTkFont(size=15))
        self.data_dump.pack(padx=20, pady=10, fill='both', expand=True)


class MetaPopup(CTkToplevel):
    """
    Popup for displaying metadata
    """

    def __init__(self, file_name, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry('400x550')
        self.title(f"{file_name} Metadata")

        self.title = customtkinter.CTkLabel(self, text=f"{file_name} Metadata", font=customtkinter.CTkFont(size=20))
        self.title.pack(padx=20, pady=10, fill='x', expand=False)

        self.data_dump = customtkinter.CTkTextbox(self, font=customtkinter.CTkFont(size=15))
        self.data_dump.pack(padx=20, pady=10, fill='both', expand=True)


class HexPopup(CTkToplevel):
    """
    Popup for displaying hex beside plaintext
    """

    def __init__(self, file_name, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry('550x550')
        self.title(f"{file_name} Hex")

        self.title = customtkinter.CTkLabel(self, text=f"{file_name} Hex", font=customtkinter.CTkFont(size=20))
        self.title.pack(padx=20, pady=10, fill='x', expand=False)

        self.data_dump = customtkinter.CTkTextbox(self)
        self.data_dump.pack(padx=20, pady=10, fill='both', expand=True)


class ObjectsPopup(CTkToplevel):
    """
    Popup for displaying objects detected in media
    """

    def __init__(self, file_name, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry('300x300')
        self.title(f"{file_name} Detected Objects")

        self.title = customtkinter.CTkLabel(self, text=f"Detected Objects",
                                            font=customtkinter.CTkFont(size=20))
        self.title.pack(padx=20, pady=10, fill='x', expand=False)

        self.objects_box = customtkinter.CTkTextbox(self, font=customtkinter.CTkFont(size=15))
        self.objects_box.pack(padx=20, pady=10, fill='both', expand=True)


class URLsPopup(CTkToplevel):
    """
    Popup for displaying extracted URLs
    """

    def __init__(self, urls, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry('400x550')
        self.title(f"{len(urls)} URLs found")

        self.title = customtkinter.CTkLabel(self, text=f"{len(urls)} URLs found",
                                            font=customtkinter.CTkFont(size=20))
        self.title.pack(padx=20, pady=10, fill='x', expand=False)

        self.urls_box = customtkinter.CTkTextbox(self, font=customtkinter.CTkFont(size=15))
        self.urls_box.pack(padx=20, pady=10, fill='both', expand=True)


class UnflagTextPopup(CTkToplevel):
    """
    Popup for displaying flagged text to unflag
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry('400x550')
        self.title("Flagged Text")

        self.title = customtkinter.CTkLabel(self, text="Flagged Text",
                                            font=customtkinter.CTkFont(size=20))
        self.title.pack(padx=20, pady=10, fill='x', expand=False)

        self.flags_listbox = CTkListbox(self, multiple_selection=False)
        self.flags_listbox.pack(padx=20, pady=10, fill='both', expand=True)

        self.delete_button = customtkinter.CTkButton(self, text="DELETE FLAG")
        self.delete_button.pack(padx=20, pady=10, fill='x', expand=False)

    def add_flag(self, flagged_text):
        """
        Adds flagged text to unflag popup listbox
        :param flagged_text:
        :return:
        """
        index = self.flags_listbox.size()
        self.flags_listbox.insert(index, flagged_text)

    def bind_delete_flag(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binds click with deleting flag
        :param callback:
        :return:
        """
        self.delete_button.bind("<Button-1>", callback)

    def update_listbox(self, flagged_texts: [str]) -> None:
        """
        Refreshes listbox with to display flagged_texts
        :param flagged_texts:
        :return:
        """

        if len(flagged_texts) == 0:
            self.destroy()
        else:
            self.flags_listbox.delete(0, tk.END)
            for flagged_text in flagged_texts:
                self.add_flag(flagged_text)


class DetectedGroomingPopup(CTkToplevel):
    """
    Popup for displaying detected grooming
    """

    def __init__(self, results, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry('1000x550')
        self.title(f"Grooming Detected In {len(results)} Instances")

        self.title = customtkinter.CTkLabel(self, text=f"Detected {len(results)} Instances of Potential Grooming",
                                            font=customtkinter.CTkFont(size=20))
        self.title.pack(padx=20, pady=10, fill='x', expand=False)

        self.gd_box = customtkinter.CTkTextbox(self, font=customtkinter.CTkFont(size=15))
        self.gd_box.pack(padx=20, pady=10, fill='both', expand=True)

        self.highlight_button = customtkinter.CTkButton(self, text="HIGHLIGHT DETECTED INSTANCES IN CHAT LOG")
        self.highlight_button.pack(padx=20, pady=10, fill='x', expand=False)

        # Populate gd box with gd results
        self.add_detected_grooming(results)

        self.focus_set()

    def add_detected_grooming(self, results: [str]) -> None:
        """
        Adds detected grooming to box
        :param results:
        :return:
        """
        for result in results:
            self.gd_box.insert(tk.END, result + '\n\n')

    def bind_highlight(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binds click highlighting detected grooming in chat
        :param callback:
        :return:
        """
        self.highlight_button.bind("<Button-1>", callback)
