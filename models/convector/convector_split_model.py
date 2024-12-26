from PyQt5.QtWidgets import QCheckBox
import csv
from models.shared.label_updater import update_manual_label

def convector_split_model(parent, model):
    """Calculate Voltage and Watts values from the model."""
    voltage, watts = 0, 0
    thermostat = False
    model_split = model.split("-")

    # Update manual
    update_manual_label(parent, model)

    # Initialize and initially hide checkboxes
    checkboxes = initialize_checkboxes(parent)

    if model.startswith(("CX", "CF")):
        voltage, watts = parse_cx_cf_model(model_split, checkboxes)
    elif model.startswith("XC"):
        voltage, watts = parse_xc_model(model_split, checkboxes)

    return voltage, watts


def initialize_checkboxes(parent):
    """Find and initialize all required checkboxes."""
    checkboxes = {
        "checkBox_h2": parent.findChild(QCheckBox, "checkBox_h2"),
        "checkBox_enclosure": parent.findChild(QCheckBox, "checkBox_enclosure"),
        "checkBox_sticker": parent.findChild(QCheckBox, "checkBox_sticker"),
        "checkBox_maxAmps": parent.findChild(QCheckBox, "checkBox_maxAmps"),
        "checkBox_tube": parent.findChild(QCheckBox, "checkBox_tube"),
        "checkBox_CFgroundlug": parent.findChild(QCheckBox, "checkBox_CFgroundlug"),
        "checkBox_CFgroundhole": parent.findChild(QCheckBox, "checkBox_CFgroundhole"),
    }
    for checkbox in checkboxes.values():
        checkbox.setVisible(False)

    checkboxes["checkBox_sticker"].setVisible(True)
    checkboxes["checkBox_enclosure"].setVisible(True)
    
    return checkboxes

def update_thermostat_checkboxes(thermo, checkboxes):
    """Update thermostat-related checkboxes based on thermo flag."""
    if thermo:
        checkboxes["checkBox_h2"].setVisible(False)
        checkboxes["checkBox_maxAmps"].setVisible(True)
        checkboxes["checkBox_tube"].setVisible(True)
    else:
        checkboxes["checkBox_h2"].setVisible(True)
        checkboxes["checkBox_maxAmps"].setVisible(False)
        checkboxes["checkBox_tube"].setVisible(False)


def parse_cx_cf_model(model_split, checkboxes):
    """Parse CX/CF model data."""
    voltage = int(model_split[1][:3])
    watts = int(model_split[2][:3]) * 100
    thermo = model_split[-1] == 'T'

    # CF-specific checkboxes
    if "CF" in model_split[0]:
        checkboxes["checkBox_CFgroundlug"].setVisible(True)
        checkboxes["checkBox_CFgroundhole"].setVisible(True)

    # Update thermostat-related checkboxes
    update_thermostat_checkboxes(thermo, checkboxes)

    # Update enclosure label
    enclosure = "IIC" if "IIC" in model_split else "IIB" if "IIB" in model_split else None
    update_enclosure_label(checkboxes["checkBox_enclosure"], enclosure, checkboxes["checkBox_sticker"])

    return voltage, watts


def parse_xc_model(model_split, checkboxes):
    """Parse XC model data."""
    kilowatts_map = {"A": 1200, "B": 1800, "C": 3600, "D": 4800, "E": 7600}
    voltage_map = {"1": 120, "2": 208, "3": 240, "4": 480, "5": 600, "6": 277}
    thermo_map = {"B": True, "N": False}

    voltage = voltage_map.get(model_split[1][1], 0)
    watts = kilowatts_map.get(model_split[1][0], 0)
    thermo = thermo_map.get(model_split[2][0], False)

    # Update thermostat-related checkboxes
    update_thermostat_checkboxes(thermo, checkboxes)

    # Update label texts
    checkboxes["checkBox_sticker"].setText(
        "For Private Label Convectors: Confirm Wording 'RUFFNECK Heaters' is not present on heater."
    )
    checkboxes["checkBox_enclosure"].setText(
        "The IIB model uses Defender® housing and shows no visible damage."
    )

    return voltage, watts

def update_enclosure_label(enclosure_checkbox, enclosure, sticker_checkbox):
    """Update the enclosure label with the correct text."""
    sticker_checkbox.setText(
        "Confirm only Ruffneck unit has a 24 hour sticker."
    )
    if enclosure_checkbox:
        if enclosure == 'IIC':
            enclosure_checkbox.setText("The IIC model uses x-Max® housing and shows no visible damage.")
        elif enclosure == 'IIB':
            enclosure_checkbox.setText("The IIB model uses Defender® housing and shows no visible damage.")
        else:
            enclosure_checkbox.setText("")
