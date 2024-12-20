from PyQt5.QtWidgets import QMainWindow, QLineEdit, QCheckBox, QTabWidget, QPushButton, QGroupBox, QButtonGroup
from PyQt5.uic import loadUi
from pdf_generator import generate_pdf_report
import csv
from PyQt5.QtCore import QTimer, Qt
import re

class HeaterTestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI
        loadUi("frontend.ui", self)

        # Get UI elements
        self.tab_widget: QTabWidget = self.findChild(QTabWidget, "tabWidget")
        self.serial_input: QLineEdit = self.findChild(QLineEdit, "serial_input")
        self.model_input: QLineEdit = self.findChild(QLineEdit, "line_model")
        self.post_button: QPushButton = self.findChild(QPushButton, "post_button")

        # Connect signals
        self.post_button.clicked.connect(self.generate_pdf)
        self.model_input.returnPressed.connect(self.on_model_entered)

        # Save tabs as separate widgets
        self.outside_steam = self.tab_widget.widget(0)
        self.outside_convector = self.tab_widget.widget(1)
        self.value = self.tab_widget.widget(2)
        self.final = self.tab_widget.widget(3)

        # Remove all tabs at start
        self.clear_tabs()

        # Flag to prevent redundant calls
        
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
        elif model.startswith("CX1"):
            self.tab_widget.addTab(self.outside_convector, "Outside Convector")
            self.tab_widget.addTab(self.value, "Value")
            self.convector_value_tab(model)
        
        self.tab_widget.addTab(self.final, "Final")

        self.initialize_boxes_and_bottons()


    def initialize_boxes_and_buttons(self):
        """Initialize all active boxes, buttons, and QButtonGroups after entering the model."""
        self.checkbox_lists = {}
        self.button_groups = {}

        for index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(index)

            # Initialize checkboxes
            self.checkbox_lists[index] = tab.findChildren(QCheckBox)

            # Initialize all buttons
            buttons = tab.findChildren(QPushButton)

            # Automatically create QButtonGroup for each QGroupBox
            group_boxes = tab.findChildren(QGroupBox)
            for group_box in group_boxes:
                # Create QButtonGroup for buttons in this QGroupBox
                button_group = QButtonGroup(self)
                button_group.setExclusive(False)

                # Add all QPushButtons to QButtonGroup
                buttons_in_group = group_box.findChildren(QPushButton)
                for button in buttons_in_group:
                    button.setCheckable(True)
                    button_group.addButton(button)
                    button.clicked.connect(lambda _, b=button, g=button_group: self.toggle_button(b, g))

                # Store the group in a dictionary for access
                group_name = group_box.objectName()
                self.button_groups[group_name] = button_group

            # Clear signals and reassign button actions
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


    def toggle_button(self, button, group):
        """Toggle button selection in QButtonGroup."""
        if not isinstance(button, QPushButton):
            print(f"Error: {button} is not a QPushButton. Type: {type(button)}")
            return

        if not isinstance(group, QButtonGroup):
            print(f"Error: {group} is not a QButtonGroup. Type: {type(group)}")
            return

        if not button.isCheckable():
            print(f"Error: Button '{button.text()}' is not checkable.")
            return

        if button.isChecked():
            print(f"Unchecking button: {button.text()}")
            button.setChecked(False)
        else:
            print(f"Checking button: {button.text()}")
            button.setChecked(True)


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
        enclosure = ""

        model_split = model.split("-")
        voltage = int(model_split[1][:3])
        watts = int(model_split[2][:3]) * 100
        thermo = str(model_split[-1])

        if thermo == 'T':
            thermostat = True

        if 'IIC' in model_split:
            enclosure = 'IIC'
        elif 'IIB' in model_split:
            enclosure = 'IIB'
        
        self.update_enclosure_groupbox(enclosure)

        print(f"Voltage: {voltage}, Watts: {watts}, Thermostat: {thermostat}, Enclosure: {enclosure}")
        return voltage, watts

    def update_enclosure_groupbox(self, enclosure):
        """Update the QGroupBox title with the enclosure value."""
        enclosure_groupbox = self.findChild(QGroupBox, "enclosure_groupbox")
        if enclosure_groupbox:
            if enclosure == 'IIC':
                enclosure_groupbox.setTitle(f"Is the IIC Model using xmax housing?")
            elif enclosure == 'IIB':
                enclosure_groupbox.setTitle("Is the IIB Model using right housing?")

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
        print("clear_after_post called")
