import csv

def read_csv(file_path, voltage, watts):
    """Read data from CSV based on Voltage and Watts."""
    try:
        with open(file_path, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["Voltage"]) == voltage and int(row["Watts"]) == watts:
                    return {
                        "Voltage": int(row["Voltage"]),
                        "Watts": int(row["Watts"]),
                        "ResistanceMin": float(row["ResistanceMin"]),
                        "ResistanceMax": float(row["ResistanceMax"]),
                    }
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Error reading CSV: {e}")
    return None
