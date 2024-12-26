def validate_resistance(resistance_input, min_resistance, max_resistance):
    """Validate the Resistance value."""
    try:
        resistance = float(resistance_input.text())
        if min_resistance <= resistance <= max_resistance:
            resistance_input.setStyleSheet("background-color: lightgreen;")
        else:
            resistance_input.setStyleSheet("background-color: lightcoral;")
    except ValueError:
        if resistance_input.text().strip() == "":
            resistance_input.setStyleSheet("")
        else:
            resistance_input.setStyleSheet("background-color: lightcoral;")

def clear_resistance_fields(voltage_input, watts_input, resistance_input):
    """Clear resistance input and reset styles."""
    voltage_input.setStyleSheet("")
    watts_input.setStyleSheet("")
    resistance_input.clear()
    resistance_input.setStyleSheet("background-color: orange;")
    return None
