import csv

def read_csv(voltage, watts, filename="tables/values.csv"):
    """Read data from CSV based on Voltage and Watts."""
    try:
        with open(filename, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["Voltage"]) == voltage and int(row["Watts"]) == watts:
                    print(f"Data for {voltage} Volts and {watts} Watts found.")
                    return {
                        "Voltage": int(row["Voltage"]),
                        "Watts": int(row["Watts"]),
                        "ResistanceMin": float(row["ResistanceMin"]),
                        "ResistanceMax": float(row["ResistanceMax"]),
                    }
    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Error reading file {filename}: {e}")
    
    print(f"Data for {voltage} Volts and {watts} Watts not found.")
    return None