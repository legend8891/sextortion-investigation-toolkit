import logging
import tkinter as tk
from tkinter import ttk
from typing import Callable
import customtkinter
from src.models.victim_suspect import VictimModel, SuspectModel


class EvidenceViewBox(ttk.Treeview):
    """
    Widget for displaying uploaded files
    """

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs, columns=('file_name', 'hash_value'), show='headings')

        self.heading('file_name', text='File Name')
        self.heading('hash_value', text='MD5 Hash')


class IntegrityViewBox(ttk.Treeview):
    """
    Widget for displaying file integrity check
    """

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs, columns=('file_name', 'original_hash_value', 'recomputed_hash_value'),
                         show='headings')

        self.heading('file_name', text='File Name')
        self.heading('original_hash_value', text='Original MD5 Hash')
        self.heading('recomputed_hash_value', text='Recomputed MD5 Hash')

        self.tag_configure('failed', background='darkred')
        self.tag_configure('passed', background='darkgreen')

    def clear(self) -> None:
        """
        Clears all entries
        :return:
        """
        self.delete(*self.get_children())


class SuspectWidget(customtkinter.CTkScrollableFrame):
    """
    Widget for displaying suspect information
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Add a thin border
        self.configure(border_width=1)

        # For centering
        self.columnconfigure(0, weight=1)

        # Title
        self.title = customtkinter.CTkLabel(self, text="Suspect Profile",
                                            font=customtkinter.CTkFont(size=30, weight="bold"))
        self.title.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

        customtkinter.CTkLabel(self, text="Name", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=1,
                                                                                                           column=0,
                                                                                                           sticky='nsew',
                                                                                                           padx=20,
                                                                                                           pady=5)

        self.name = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.name.grid(row=2, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="DOB", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=3,
                                                                                                          column=0,
                                                                                                          sticky='nsew',
                                                                                                          padx=20,
                                                                                                          pady=5)

        self.dob = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.dob.grid(row=4, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Nationality", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=5,
                                                                                                                  column=0,
                                                                                                                  sticky='nsew',
                                                                                                                  padx=20,
                                                                                                                  pady=5)

        self.nationality = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.nationality.grid(row=6, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Special Considerations",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=7, column=0, sticky='nsew',
                                                                                        padx=20, pady=5)

        self.special_considerations = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.special_considerations.grid(row=8, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Address", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=9,
                                                                                                              column=0,
                                                                                                              sticky='nsew',
                                                                                                              padx=20,
                                                                                                              pady=5)

        self.address = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.address.grid(row=10, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Email", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=11,
                                                                                                            column=0,
                                                                                                            sticky='nsew',
                                                                                                            padx=20,
                                                                                                            pady=5)

        self.email = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.email.grid(row=12, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Phone", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=13,
                                                                                                            column=0,
                                                                                                            sticky='nsew',
                                                                                                            padx=20,
                                                                                                            pady=5)

        self.phone = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.phone.grid(row=14, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Profiles", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=15,
                                                                                                               column=0,
                                                                                                               sticky='nsew',
                                                                                                               padx=20,
                                                                                                               pady=5)

        self.profiles = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.profiles.grid(row=16, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Screen Names", font=customtkinter.CTkFont(size=20, weight="bold")).grid(
            row=17, column=0, sticky='nsew', padx=20, pady=5)

        self.screen_names = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.screen_names.grid(row=18, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="School", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=19,
                                                                                                             column=0,
                                                                                                             sticky='nsew',
                                                                                                             padx=20,
                                                                                                             pady=5)

        self.school = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.school.grid(row=20, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Occupation", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=21,
                                                                                                                 column=0,
                                                                                                                 sticky='nsew',
                                                                                                                 padx=20,
                                                                                                                 pady=5)

        self.occupation = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.occupation.grid(row=22, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Business Address", font=customtkinter.CTkFont(size=20, weight="bold")).grid(
            row=23, column=0, sticky='nsew', padx=20, pady=5)

        self.business_address = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.business_address.grid(row=24, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Relationship to victim",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=25, column=0, sticky='nsew',
                                                                                        padx=20, pady=5)

        self.victim_relationship = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.victim_relationship.grid(row=26, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Additional Information",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=27,
                                                                                        column=0,
                                                                                        sticky='nsew',
                                                                                        padx=20,
                                                                                        pady=5)

        self.additional_info = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.additional_info.grid(row=28, column=0, sticky='n', padx=20, pady=5)

        self.edit_button = customtkinter.CTkButton(self, text="EDIT")
        self.edit_button.grid(row=29, column=0, sticky='n', padx=20, pady=5)

    def bind_edit(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binds editing suspect button at bottom of widget
        :param callback:
        :return:
        """
        self.edit_button.bind("<Button-1>", callback)

    def set_fields(self) -> None:
        """
        Updates all fields in the profile widget
        :return:
        """
        logging.info("Setting suspect widget fields")
        suspect_model = SuspectModel()

        self.name.configure(text=suspect_model.name)
        self.dob.configure(text=suspect_model.dob)
        self.nationality.configure(text=suspect_model.nationality)
        self.special_considerations.configure(text=suspect_model.special_considerations)
        self.special_considerations.configure(text=suspect_model.special_considerations)
        self.address.configure(text=suspect_model.address)
        self.email.configure(text=suspect_model.email)
        self.phone.configure(text=suspect_model.phone)
        self.profiles.configure(text=suspect_model.profiles)
        self.screen_names.configure(text=suspect_model.screen_names)
        self.school.configure(text=suspect_model.school)
        self.occupation.configure(text=suspect_model.occupation)
        self.business_address.configure(text=suspect_model.business_address)
        self.victim_relationship.configure(text=suspect_model.relationship_to_victim)
        self.additional_info.configure(text=suspect_model.additional_info)


class VictimWidget(customtkinter.CTkScrollableFrame):
    """
    Widget for displaying victim information
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Add a thin border
        self.configure(border_width=1)

        # For centering
        self.columnconfigure(0, weight=1)

        # Title
        self.title = customtkinter.CTkLabel(self, text="Victim Profile",
                                            font=customtkinter.CTkFont(size=30, weight="bold"))
        self.title.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

        customtkinter.CTkLabel(self, text="Name", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=1,
                                                                                                           column=0,
                                                                                                           sticky='nsew',
                                                                                                           padx=20,
                                                                                                           pady=5)

        self.name = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.name.grid(row=2, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="DOB", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=3,
                                                                                                          column=0,
                                                                                                          sticky='nsew',
                                                                                                          padx=20,
                                                                                                          pady=5)

        self.dob = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.dob.grid(row=4, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Nationality", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=5,
                                                                                                                  column=0,
                                                                                                                  sticky='nsew',
                                                                                                                  padx=20,
                                                                                                                  pady=5)

        self.nationality = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.nationality.grid(row=6, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Special Considerations",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=7, column=0, sticky='nsew',
                                                                                        padx=20, pady=5)

        self.special_considerations = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.special_considerations.grid(row=8, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Address", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=9,
                                                                                                              column=0,
                                                                                                              sticky='nsew',
                                                                                                              padx=20,
                                                                                                              pady=5)

        self.address = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.address.grid(row=10, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Email", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=11,
                                                                                                            column=0,
                                                                                                            sticky='nsew',
                                                                                                            padx=20,
                                                                                                            pady=5)

        self.email = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.email.grid(row=12, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Phone", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=13,
                                                                                                            column=0,
                                                                                                            sticky='nsew',
                                                                                                            padx=20,
                                                                                                            pady=5)

        self.phone = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.phone.grid(row=14, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Profiles", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=15,
                                                                                                               column=0,
                                                                                                               sticky='nsew',
                                                                                                               padx=20,
                                                                                                               pady=5)

        self.profiles = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.profiles.grid(row=16, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Screen Names", font=customtkinter.CTkFont(size=20, weight="bold")).grid(
            row=17, column=0, sticky='nsew', padx=20, pady=5)

        self.screen_names = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.screen_names.grid(row=18, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="School", font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=19,
                                                                                                             column=0,
                                                                                                             sticky='nsew',
                                                                                                             padx=20,
                                                                                                             pady=5)

        self.school = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.school.grid(row=20, column=0, sticky='n', padx=20, pady=5)

        customtkinter.CTkLabel(self, text="Additional Information",
                               font=customtkinter.CTkFont(size=20, weight="bold")).grid(row=19,
                                                                                        column=0,
                                                                                        sticky='nsew',
                                                                                        padx=20,
                                                                                        pady=5)

        self.additional_info = customtkinter.CTkLabel(self, font=customtkinter.CTkFont(size=20))
        self.additional_info.grid(row=21, column=0, sticky='n', padx=20, pady=5)

        self.edit_button = customtkinter.CTkButton(self, text="EDIT")
        self.edit_button.grid(row=22, column=0, sticky='n', padx=20, pady=5)

    def bind_edit(self, callback: Callable[[tk.Event], None]) -> None:
        """
        Binds edit button
        :param callback:
        :return:
        """
        self.edit_button.bind("<Button-1>", callback)

    def set_fields(self) -> None:
        """
        Updates all fields in the profile widget
        :return:
        """
        logging.info("Setting victim widget fields")
        victim_model = VictimModel()

        self.name.configure(text=victim_model.name)
        self.dob.configure(text=victim_model.dob)
        self.nationality.configure(text=victim_model.nationality)
        self.special_considerations.configure(text=victim_model.special_considerations)
        self.special_considerations.configure(text=victim_model.special_considerations)
        self.address.configure(text=victim_model.address)
        self.email.configure(text=victim_model.email)
        self.phone.configure(text=victim_model.phone)
        self.profiles.configure(text=victim_model.profiles)
        self.screen_names.configure(text=victim_model.screen_names)
        self.school.configure(text=victim_model.school)
        self.additional_info.configure(text=victim_model.additional_info)
