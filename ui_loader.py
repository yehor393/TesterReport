from PyQt5.QtWidgets import QMainWindow, QLineEdit, QCheckBox, QTabWidget, QPushButton, QLabel
from PyQt5.uic import loadUi
from pdf_generator import generate_pdf_report
import csv
from PyQt5.QtCore import QTimer, Qt, QDateTime
import re

class HeaterTestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI
        loadUi("frontend.ui", self)

        # Get UI elements
        # Tabs
        self.tab_widget: QTabWidget = self.findChild(QTabWidget, "tabWidget")
        
        # Inputs
        self.serial_input: QLineEdit = self.findChild(QLineEdit, "serial_input")
        self.model_input: QLineEdit = self.findChild(QLineEdit, "line_model")
        self.post_button: QPushButton = self.findChild(QPushButton, "post_button")
        self.build_by: QLineEdit = self.findChild(QLineEdit, "build_by")
        self.pass_by: QLineEdit = self.findChild(QLineEdit, "pass_by")
        self.datetime_widget: QLabel = self.findChild(QLabel, "datetime_widget")

        # Buttons
        self.post_button: QPushButton = self.findChild(QPushButton, "post_button")
        
        # Checkboxes
        self.checkBox_h2: QCheckBox = self.findChild(QCheckBox, "checkBox_h2")
        self.checkBox_h2.setVisible(False)

        # Connect signals
        self.post_button.clicked.connect(self.generate_pdf)
        self.model_input.returnPressed.connect(self.on_model_entered)

        # Ensure inputs are always uppercase
        self.serial_input.setText(self.serial_input.text().upper())
        self.serial_input.textChanged.connect(lambda: self.serial_input.setText(self.serial_input.text().upper()))

        self.model_input.setText(self.model_input.text().upper())
        self.model_input.textChanged.connect(lambda: self.model_input.setText(self.model_input.text().upper()))

        self.build_by.setText(self.build_by.text().upper())
        self.build_by.textChanged.connect(lambda: self.build_by.setText(self.build_by.text().upper()))

        self.pass_by.setText(self.pass_by.text().upper())
        self.pass_by.textChanged.connect(lambda: self.pass_by.setText(self.pass_by.text().upper()))
        
        # Save tabs as separate widgets
        self.outside_steam = self.tab_widget.widget(0)
        self.outside_convector = self.tab_widget.widget(1)
        self.value = self.tab_widget.widget(2)
        self.final = self.tab_widget.widget(3)

        # Remove all tabs at start
        self.clear_tabs()

        # Set up real-time date and time updating
        self.update_datetime()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Update every second
        
    def on_model_entered(self):
        """Handle event after entering the model."""
        model = self.model_input.text().strip()
        
        if model:
            self.clear_all_fields()
            self.set_tabs_for_model(model)
        else:
            self.clear_tabs()


    def set_tabs_for_model(self, model):
        """Add the required tabs based on the model."""
        self.clear_tabs()
        if model.startswith("HP"):
            self.tab_widget.addTab(self.outside_steam, "Outside Steam")
        elif model.startswith("CX1") or model.startswith("CF1") or model.startswith("XC"):
            self.tab_widget.addTab(self.outside_convector, "Outside Convector")
            self.tab_widget.addTab(self.value, "Value")
            self.convector_value_tab(model)
        
        self.tab_widget.addTab(self.final, "Final")

        self.initialize_boxes_and_buttons()


    def initialize_boxes_and_buttons(self):
        """Initialize all active boxes, buttons, and QButtonGroups after entering the model."""
        self.checkbox_lists = {}

        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)

            # Initialize checkboxes
            self.checkbox_lists[index] = tab.findChildren(QCheckBox)

            # Initialize all buttons
            buttons = tab.findChildren(QPushButton)

            for button in buttons:
                try:
                    button.clicked.disconnect()
                except TypeError:
                    pass

                # Bind actions for specific buttons
                if "clear_button" in button.objectName():
                    button.clicked.connect(lambda _, b=button: self.clear_fields(b))
                elif "fill_button" in button.objectName():
                    button.clicked.connect(lambda _, b=button: self.fill_fields(b))

        print(f"initialize_boxes_and_buttons called with {self.tab_widget.count()} tabs")


    def convector_value_tab(self, model):
        """Initialize the Value tab after creation."""
        voltage, watts = self.convector_split_model(model)

        # Find elements in the Value tab
        self.voltage_input: QLineEdit = self.value.findChild(QLineEdit, "voltage_input")
        self.watts_input: QLineEdit = self.value.findChild(QLineEdit, "watts_input")
        self.resistance_input: QLineEdit = self.value.findChild(QLineEdit, "resistance_input")

        # Update Voltage and Watts fields
        self.voltage_input.setText(str(voltage))
        self.watts_input.setText(str(watts))

        # Clear resistance input field
        self.resistance_input.clear()

        # Read resistance range from CSV only if voltage and watts exist on the same row
        resistance_data = self.convector_read_csv(voltage, watts)

        # Disconnect resistance validation before updating logic
        try:
            self.resistance_input.textChanged.disconnect()
        except TypeError:
            pass

        if resistance_data:
            min_resistance = resistance_data["ResistanceMin"]
            max_resistance = resistance_data["ResistanceMax"]
            self.resistance_range = (min_resistance, max_resistance)

            # Highlight fields if data is available
            self.voltage_input.setStyleSheet("background-color: lightgreen;")
            self.watts_input.setStyleSheet("background-color: lightgreen;")

            # Connect resistance validation
            self.resistance_input.textChanged.connect(
                lambda: self.validate_resistance(min_resistance, max_resistance)
            )
        else:
            self.clear_resistance_fields()

        print(f"initialize_value_tab called for model: {model}")


    def convector_split_model(self, model):
        """Calculate Voltage and Watts values from the model."""
        voltage = 0
        watts = 0
        thermostat = False
        thermo = None

        model_split = model.split("-")

        self.update_manual_label(model)

        checkBox_h2 = self.findChild(QCheckBox, "checkBox_h2")
        checkBox_h2.setVisible(False)

        checkBox_enclosure = self.findChild(QCheckBox, "checkBox_enclosure")
        checkBox_sticker = self.findChild(QCheckBox, "checkBox_sticker")
        
        checkBox_maxAmps = self.findChild(QCheckBox, "checkBox_maxAmps")
        checkBox_maxAmps.setVisible(False)

        checkBox_tube = self.findChild(QCheckBox, "checkBox_tube")
        checkBox_tube.setVisible(False)

        checkBox_CFgroundlug = self.findChild(QCheckBox, "checkBox_CFgroundlug")
        checkBox_CFgroundlug.setVisible(False)

        checkBox_CFgroundhole = self.findChild(QCheckBox, "checkBox_CFgroundhole")
        checkBox_CFgroundhole.setVisible(False)
        
        try:
            if model.startswith(("CX", "CF")):
                voltage = int(model_split[1][:3])
                watts = int(model_split[2][:3]) * 100
                thermo = str(model_split[-1])

                if model.startswith("CF"):
                    checkBox_CFgroundlug.setVisible(True)
                    checkBox_CFgroundhole.setVisible(True)

                if thermo == 'T':
                    thermostat = True
                    checkBox_h2.setVisible(False)
                    checkBox_maxAmps.setVisible(True)
                else:
                    checkBox_h2.setVisible(True)

                if 'IIC' in model_split:
                    enclosure = 'IIC'
                elif 'IIB' in model_split:
                    enclosure = 'IIB'
                else:
                    enclosure = None
                
                self.update_enclosure_label(enclosure)
                checkBox_sticker.setText("Confirm only Ruffneck unit has a 24 hour sticker.")

            
            elif model.startswith("XC"):
                voltage = str(model_split[1][1])
                watts = str(model_split[1][0])
                thermo = str(model_split[2][0])
                print(model_split)

                # Maps for values
                kilowatts_map = {
                    "A": 1200,
                    "B": 1800,
                    "C": 3600,
                    "D": 4800,
                    "E": 7600
                }
                voltage_map = {
                    "1": 120,
                    "2": 208,
                    "3": 240,
                    "4": 480,
                    "5": 600,
                    "6": 277
                }
            
                # Get values from maps
                watts = kilowatts_map.get(watts, None)
                voltage = voltage_map.get(voltage, None)
            
                checkBox_sticker.setText("For Private Label Convectors: Confirm Wording 'RUFFNECK Heaters' is not present on heater.")            
                checkBox_enclosure.setText("The IIB model uses Defender® housing and shows no visible damage.")
            
        except (FileNotFoundError, ValueError, KeyError, TypeError) as e:
            print(f"Error reading model: {e}")


        if thermo == 'T' or thermo == 'B':
            thermostat = True
            checkBox_maxAmps.setVisible(True)
            checkBox_tube.setVisible(True)
        else:
            checkBox_h2.setVisible(True)


            print(f"Voltage: {voltage}, Watts: {watts}, Thermostat: {thermostat}")
        return voltage, watts


    def update_enclosure_label(self, enclosure):
        """Update the QGroupBox title with the enclosure value."""
        enclosure_label = self.findChild(QCheckBox, "enclosure_label")
        if enclosure_label:
            if enclosure == 'IIC':
                enclosure_label.setText("The IIC model uses x-Max® housing and shows no visible damage.")
            elif enclosure == 'IIB':
                enclosure_label.setText("The IIB model uses Defender® housing and shows no visible damage.")
            else:
                enclosure_label.setText("")
        else:
            print("enclosure_label not found")


    def update_manual_label(self, model):
        """Update the manual label based on the model."""

        checkBox_manual = self.findChild(QCheckBox, "checkBox_manual")

        model_split = model.split("-")
        model_value = model_split[0][:2]

        try:
            with open("tables/manuals.csv", mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if str(row["Model"]) == model_value:
                        manual = row["Manual"]
                        return checkBox_manual.setText(f"Check against Shop Order to {manual}. Kit is installed.")

        except (FileNotFoundError, ValueError, KeyError) as e:
            print(f"model not found: {e}")


    def convector_read_csv(self, voltage, watts):
        """Read data from CSV based on Voltage and Watts."""
        try:
            with open("tables/values.csv", mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if int(row["Voltage"]) == voltage and int(row["Watts"]) == watts:
                        print(f"Дані для {voltage} Вольт і {watts} Ватт знайдено в таблиці.")
                        return {
                            "Voltage": int(row["Voltage"]),
                            "Watts": int(row["Watts"]),
                            "ResistanceMin": float(row["ResistanceMin"]),
                            "ResistanceMax": float(row["ResistanceMax"]),
                        }
        except (FileNotFoundError, ValueError, KeyError) as e:
            print(f"Помилка при зчитуванні файлу values.csv: {e}")
        
        print(f"Дані для {voltage} Вольт і {watts} Ватт не знайдено в таблиці.")
        return None


    def clear_resistance_fields(self):
        """Clear resistance input and reset styles."""
        self.voltage_input.setStyleSheet("")
        self.watts_input.setStyleSheet("")
        self.resistance_input.clear()
        self.resistance_input.setStyleSheet("background-color: orange;")
        self.resistance_range = None


    def validate_resistance(self, min_resistance, max_resistance):
        """Validate the Resistance value."""
        try:
            resistance = float(self.resistance_input.text())
            if min_resistance <= resistance <= max_resistance:
                self.resistance_input.setStyleSheet("background-color: lightgreen;")
            else:
                self.resistance_input.setStyleSheet("background-color: lightcoral;")
        except ValueError:
            if self.resistance_input.text().strip() == "":
                self.resistance_input.setStyleSheet("")
            else:
                self.resistance_input.setStyleSheet("background-color: lightcoral;")


    def clear_fields(self, button):
        """Clear fields related to the button."""
        tab = self.get_parent_tab(button)
        if tab:
            checkboxes = tab.findChildren(QCheckBox)
            for checkbox in checkboxes:
                checkbox.setChecked(False)
        print(f"clear_fields called for button: {button.objectName()}")


    def fill_fields(self, button):
        """Fill fields related to the button."""
        tab = self.get_parent_tab(button)
        if tab:
            checkboxes = tab.findChildren(QCheckBox)
            for checkbox in checkboxes:
                checkbox.setChecked(True)
        button.setFocus()
        print(f"fill_fields called for button: {button.objectName()}")


    def clear_tabs(self):
        """Remove all tabs."""
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)
        print("clear_tabs called")


    def clear_all_fields(self):
        """Clear all checkboxes and text fields (QLineEdit) on all tabs."""
        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)
            checkboxes = tab.findChildren(QCheckBox)
            for checkbox in checkboxes:
                checkbox.setChecked(False)
            line_edits = tab.findChildren(QLineEdit)
            for line_edit in line_edits:
                line_edit.clear()
        print("clear_all_fields called")


    def get_parent_tab(self, widget):
        """Get the tab to which the widget belongs."""
        while widget and widget not in [self.tab_widget.widget(i) for i in range(self.tab_widget.count())]:
            widget = widget.parent()
        return widget
    

    def generate_pdf(self):
        """Call the function to create a PDF report."""
        model = self.model_input.text().strip()
        serial = self.serial_input.text().strip()

        try:
            generate_pdf_report(model, serial, self.tab_widget)
            self.clear_after_post()
        except Exception as e:
            print(f"Помилка при створенні PDF: {e}")


    def clear_after_post(self):
        """Clear all tabs, checkboxes, and text fields after POST."""
        self.clear_all_fields()
        self.clear_tabs()
        self.serial_input.clear()
        self.model_input.clear()
        print("clear_after_post called")

    def update_datetime(self):
        """Update the date and time in the datetime widget."""
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("HH:mm\nMMMM dd/yyyy")
        self.datetime_widget.setText(formatted_datetime)