from PyQt5.QtWidgets import QLineEdit
from models.shared.resistance_utils import validate_resistance, clear_resistance_fields
from models.shared.csv_utils import read_csv


def convector_value_tab(parent, model, convector_split_model):
    """Initialize the Value tab after creation."""
    voltage, watts = convector_split_model(parent, model)

    # Find elements in the Value tab
    voltage_input: QLineEdit = parent.value.findChild(QLineEdit, "voltage_input")
    watts_input: QLineEdit = parent.value.findChild(QLineEdit, "watts_input")
    resistance_input: QLineEdit = parent.value.findChild(QLineEdit, "resistance_input")

    # Update Voltage and Watts fields
    voltage_input.setText(str(voltage))
    watts_input.setText(str(watts))
    resistance_input.clear()

    # Read resistance range from CSV
    resistance_data = read_csv("tables/values.csv", voltage, watts)

    # Disconnect resistance validation before updating logic
    try:
        resistance_input.textChanged.disconnect()
    except TypeError:
        pass

    if resistance_data:
        min_resistance = resistance_data["ResistanceMin"]
        max_resistance = resistance_data["ResistanceMax"]
        resistance_input.textChanged.connect(
            lambda: validate_resistance(resistance_input, min_resistance, max_resistance)
        )
    else:
        clear_resistance_fields(voltage_input, watts_input, resistance_input)

    print(f"initialize_value_tab called for model: {model}")
