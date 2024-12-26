from PyQt5.QtWidgets import QCheckBox
import csv

def update_manual_label(parent, model):
    """Update the manual label based on the model."""
    checkBox_manual = parent.findChild(QCheckBox, "checkBox_manual")
    model_split = model.split("-")
    model_value = model_split[0][:2]

    try:
        with open("tables/manuals.csv", mode="r") as file:
            for row in csv.DictReader(file):
                if str(row["Model"]) == model_value:
                    manual = row["Manual"]
                    checkBox_manual.setText(f"Check against Shop Order to {manual}. Kit is installed.")
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Error updating manual label: {e}")