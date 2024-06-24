import logging
import tkinter as tk
from tkinter import ttk
import customtkinter
from src.models.activitylog import ActivityLogModel
logging.basicConfig(level=logging.INFO)


class MainView(customtkinter.CTk):
    """
    Main application view
    Contains all tabs and case manager sidebar
    """
    def __init__(self) -> None:
        super().__init__()

        # Configure window
        self.title("Child Sextortion Toolkit")
        width, height = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry('%dx%d+0+0' % (width, height))

        # Set application theme
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("dark-blue")

        # Sidebar column
        self.grid_columnconfigure(0, weight=0)

        # Main display column
        self.grid_columnconfigure(1, weight=1)

        # Config row weight
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Create sidebar and position it to the left side
        self.sidebar_frame = customtkinter.CTkFrame(self, border_width=4, width=400)
        self.sidebar_frame.grid(row=0, column=0, padx=20, pady=20, rowspan=10, sticky="nsw")

        # Add components to the sidebar
        self.corner_title = customtkinter.CTkLabel(self.sidebar_frame, text="CST \n CHILD SEXTORTION TOOLKIT",
                                                   font=customtkinter.CTkFont(family="Helvetica", size=20,
                                                                              weight="bold"))
        self.corner_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

        # Container for case management buttons
        self.buttons_frame = customtkinter.CTkFrame(self.sidebar_frame, border_width=4)
        self.buttons_frame.grid(row=1, column=0, padx=50, pady=20, rowspan=4, sticky="nsew")
        self.buttons_frame.columnconfigure(0, weight=1)
        self.case_management_label = customtkinter.CTkLabel(self.buttons_frame, text="CASE MANAGEMENT",
                                                            font=customtkinter.CTkFont(size=20, weight="bold"))
        self.case_management_label.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # New case button
        self.button_new = customtkinter.CTkButton(self.buttons_frame, text="NEW", font=customtkinter.CTkFont())
        self.button_new.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Open case button
        self.button_open = customtkinter.CTkButton(self.buttons_frame, text="OPEN", font=customtkinter.CTkFont())
        self.button_open.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Container for investigator changing
        self.investigator_frame = customtkinter.CTkFrame(self.sidebar_frame, border_width=4)

        # Investigator change dropdown
        self.investigator_selector_label = customtkinter.CTkLabel(self.investigator_frame,
                                                                  text="CURRENT \n INVESTIGATOR",
                                                                  font=customtkinter.CTkFont(size=20, weight="bold"))
        self.investigator_selector_label.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        self.investigator_selector = customtkinter.CTkOptionMenu(self.investigator_frame)
        self.investigator_selector.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        self.add_investigator_button = customtkinter.CTkButton(self.investigator_frame, text="ADD",
                                                               font=customtkinter.CTkFont())
        self.add_investigator_button.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # Create tabs frame and bar
        self.tabs_view = customtkinter.CTkTabview(self, border_width=4, corner_radius=10, anchor="w")
        self.tabs_view.add("Identification")
        self.tabs_view.add("Preservation")
        self.tabs_view.add("Collection")
        self.tabs_view.add("Examination")
        self.tabs_view.add("Analysis")
        # self.tabs_view.grid(row=0, column=1, rowspan=5, padx=20, pady=20, sticky="nsew")
        self.tabs_view.set("Identification")

        # For when no case is open
        self.no_tabs_view = customtkinter.CTkFrame(self, border_width=4, corner_radius=10)
        self.no_tabs_label = customtkinter.CTkLabel(self.no_tabs_view,
                                                    text="NO CURRENT CASE \n CREATE A NEW CASE OR OPEN AN EXISTING CASE")
        self.no_tabs_label.pack(expand=True, fill=tk.BOTH)

        # Destroy view when window closed
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Set styling for treeviews
        style = ttk.Style()
        style.configure("Treeview",
                        background="#252525",
                        foreground="white",
                        rowheight=50,
                        fieldbackground="#252525")

        style.configure("Treeview.Heading",
                        font=(None, 15))

    def on_window_close(self) -> None:
        """
        Handle window closing
        :return:
        """
        # Log closing
        (ActivityLogModel().insert(f"Toolkit closed"))

        # Close
        self.destroy()

    def hide_tabs(self) -> None:
        """
        Hides tabs and presents prompts to open or create a case
        :return:
        """
        logging.info("Hiding tabs and investigator selection")

        # Hide tabs
        self.tabs_view.grid_forget()

        # Show no case message
        self.no_tabs_view.grid(row=0, column=1, rowspan=5, padx=20, pady=20, sticky="nsew")

        # Hide investigators frame
        self.investigator_frame.grid_forget()

    def show_tabs(self) -> None:
        """
        Shows tabs since case is open
        :return:
        """
        logging.info("Showing tabs and investigator selection")

        # Hide no case message
        self.no_tabs_view.grid_forget()

        # Show tabs
        self.tabs_view.grid(row=0, column=1, rowspan=5, padx=20, pady=20, sticky="nsew")

        # Show investigators frame
        self.investigator_frame.grid(row=5, column=0, padx=50, pady=20, rowspan=4, sticky="nsew")
