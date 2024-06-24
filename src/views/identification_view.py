import logging
import tkinter as tk
import customtkinter
from src.views.ui_components.widgets import SuspectWidget, VictimWidget


class IdentificationView(customtkinter.CTkFrame):
    """
    View for the Identification tab
    """

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)

        logging.info("Creating Identification Tab")

        # Create profile widgets
        self.suspect_profile_widget = SuspectWidget(self)
        self.victim_profile_widget = VictimWidget(self)

        # Add suspect button visibility flag
        self.suspect_button_visible = True
        self.victim_button_visible = True

        # 2 Equal size columns
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Configure main rows
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)

        # Suspect/Victim add buttons
        self.suspect_add = customtkinter.CTkButton(self, text="ADD SUSPECT",
                                                   font=customtkinter.CTkFont(size=15, weight="bold"))
        self.suspect_add.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.victim_add = customtkinter.CTkButton(self, text="ADD VICTIM",
                                                  font=customtkinter.CTkFont(size=15, weight="bold"))
        self.victim_add.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Configure incident frame
        self.incident_frame = customtkinter.CTkFrame(self, border_width=1)
        self.incident_frame.grid(row=1, column=0, columnspan=4, padx=20, pady=20, sticky="nsew")
        self.incident_frame.columnconfigure(0, weight=1)
        self.incident_frame.rowconfigure(0, weight=1)
        self.incident_frame.rowconfigure(1, weight=0)
        self.incident_frame.rowconfigure(2, weight=1)
        self.incident_frame.rowconfigure(3, weight=0)
        self.incident_frame.rowconfigure(4, weight=1)
        self.incident_frame.rowconfigure(5, weight=0)

        # Incident type
        self.type_label = customtkinter.CTkLabel(self.incident_frame, text="SEXTORTION TYPE",
                                                 font=customtkinter.CTkFont(size=15, weight="bold"))
        self.type_label.grid(row=0, padx=10, pady=5, sticky="nsew")
        self.sextortion_type = customtkinter.CTkOptionMenu(self.incident_frame, values=['--Select Sextortion Type--',
                                                                                        'Minor-focused', 'Cybercrime',
                                                                                        'Romantic/Relationship',
                                                                                        'Organised Crime',
                                                                                        'Other'])
        self.sextortion_type.grid(row=1, padx=10, pady=5, sticky="nsew")

        # Threats
        self.threats_label = customtkinter.CTkLabel(self.incident_frame, text="THREATS",
                                                    font=customtkinter.CTkFont(size=15, weight="bold"))
        self.threats_label.grid(row=2, padx=10, pady=5, sticky="nsew")
        self.threats_entry = customtkinter.CTkOptionMenu(self.incident_frame,
                                                         values=['--Select Threats--', 'Share victim CSAM',
                                                                 'Harassment', 'Stalking (online)',
                                                                 'Stalking (offline)',
                                                                 'Get in trouble with '
                                                                 'work/school/family/law',
                                                                 'Physical harm (victim)', 'Physical '
                                                                                           'harm('
                                                                                           'others)',
                                                                 'Other'])
        self.threats_entry.grid(row=3, padx=10, pady=5, sticky="nsew")

        # Demands
        self.demands_label = customtkinter.CTkLabel(self.incident_frame, text="DEMANDS",
                                                    font=customtkinter.CTkFont(size=15, weight="bold"))
        self.demands_label.grid(row=4, padx=10, pady=5, sticky="nsew")
        self.demands_entry = customtkinter.CTkOptionMenu(self.incident_frame,
                                                         values=['--Select Demands--', 'Additional '
                                                                                       'CSAM',
                                                                 'Meet online for sexual '
                                                                 'activity', 'Meet offline for '
                                                                             'sexual activity',
                                                                 'Send CSAM of someone else',
                                                                 'Remain in relationship',
                                                                 'Monetary', 'Self-Harm',
                                                                 'Other'])
        self.demands_entry.grid(row=5, padx=10, pady=(5, 20), sticky="nsew")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Frames to hold start and end date times
        self.start_frame = customtkinter.CTkFrame(self, border_width=1)
        self.start_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.end_frame = customtkinter.CTkFrame(self, border_width=1)
        self.end_frame.grid(row=2, column=1, padx=20, pady=20, sticky="nsew")
        self.start_frame.columnconfigure((0, 1), weight=1)
        self.end_frame.columnconfigure((0, 1), weight=1)

        # Titles for start/end date time frames
        self.start_frame_label = customtkinter.CTkLabel(self.start_frame, text="START DATE TIME",
                                                        font=customtkinter.CTkFont(size=15, weight="bold"))
        self.start_frame_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.end_frame_label = customtkinter.CTkLabel(self.end_frame, text="END DATE TIME",
                                                      font=customtkinter.CTkFont(size=15, weight="bold"))
        self.end_frame_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Start date time
        self.start_date_field = (
            customtkinter.CTkEntry(self.start_frame, placeholder_text="DD/MM/YYYY", border_width=1))
        self.start_date_field.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        self.start_date_label = customtkinter.CTkLabel(self.start_frame, text="DATE",
                                                       font=customtkinter.CTkFont(size=15)).grid(row=1, column=0,
                                                                                                 padx=10,
                                                                                                 pady=10, sticky='e')

        self.start_time_field = (customtkinter.CTkEntry(self.start_frame, placeholder_text="HH:MM", border_width=1))
        self.start_time_field.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        self.start_time_label = customtkinter.CTkLabel(self.start_frame, text="TIME",
                                                       font=customtkinter.CTkFont(size=15)).grid(row=2, column=0,
                                                                                                 padx=10,
                                                                                                 pady=10, sticky='e')
        self.start_button = customtkinter.CTkButton(self.start_frame, text="SUBMIT",
                                                    font=customtkinter.CTkFont(size=15))
        self.start_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # End date time
        self.end_date_field = customtkinter.CTkEntry(self.end_frame, placeholder_text="DD/MM/YYYY", border_width=1)
        self.end_date_field.grid(row=1, column=1, padx=10, pady=10, sticky='w')

        self.end_date_label = customtkinter.CTkLabel(self.end_frame, text="DATE",
                                                     font=customtkinter.CTkFont(size=15)).grid(row=1, column=0, padx=10,
                                                                                               pady=10, sticky='e')

        self.end_time_field = (customtkinter.CTkEntry(self.end_frame, placeholder_text="HH:MM", border_width=1))
        self.end_time_field.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        self.end_time_label = customtkinter.CTkLabel(self.end_frame, text="TIME",
                                                     font=customtkinter.CTkFont(size=15)).grid(row=2, column=0, padx=10,
                                                                                               pady=10, sticky='e')
        self.end_button = (customtkinter.CTkButton(self.end_frame, text="SUBMIT",
                                                   font=customtkinter.CTkFont(size=15)))
        self.end_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Add all content to the frame
        self.pack(fill=tk.BOTH, expand=True)
        self.pack_propagate(False)

    def suspect_button_to_widget(self) -> None:
        """
        Hides suspect add button and shows profile widget
        :return:
        """
        logging.info("Hiding suspect add button, showing suspect widget")

        # Hide button
        self.suspect_add.grid_forget()
        # Toggle flag
        self.suspect_button_visible = False
        # Show profile widget
        self.suspect_profile_widget.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def victim_button_to_widget(self) -> None:
        """
        Hides victim add button and shows profile widget
        """
        logging.info("Hiding victim add button, showing victim widget")

        # Hide button
        self.victim_add.grid_forget()
        # Toggle flag
        self.victim_button_visible = False
        # Show profile widget
        self.victim_profile_widget.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def suspect_widget_to_button(self) -> None:
        """
        Hides suspect profile widget and shows add button
        :return:
        """
        logging.info("Hiding suspect widget, showing suspect add button")

        # Hide widget
        self.suspect_profile_widget.grid_forget()
        # Toggle flag
        self.suspect_button_visible = True
        # Show button
        self.suspect_add.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def victim_widget_to_button(self) -> None:
        """
        Hides victim profile widget and shows add button
        :return:
        """
        logging.info("Hiding victim widget, showing victim add button")

        # Hide widget
        self.victim_profile_widget.grid_forget()
        # Toggle flag
        self.victim_button_visible = True
        # Show button
        self.victim_add.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def clear_fields(self) -> None:
        """
        Resets all fields to default
        :return:
        """
        logging.info("Clearing identification view fields")
        self.suspect_widget_to_button()
        self.victim_widget_to_button()
        self.sextortion_type.set("--Select Sextortion Type--")
        self.threats_entry.set("--Select Threats--")
        self.demands_entry.set("--Select Demands--")
        self.start_date_field.delete(0, tk.END)
        self.start_date_field.configure(placeholder_text='DD/MM/YYYY')
        self.start_time_field.delete(0, tk.END)
        self.start_time_field.configure(placeholder_text='HH:MM')
        self.end_date_field.delete(0, tk.END)
        self.end_date_field.configure(placeholder_text='DD/MM/YYYY')
        self.end_time_field.delete(0, tk.END)
        self.end_time_field.configure(placeholder_text='HH:MM')
