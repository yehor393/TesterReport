def split_model(model):
    """Calculate Voltage and Watts values from the model."""
    model_split = model.split("-")
    voltage = int(model_split[1][:3])
    watts = int(model_split[2][:3]) * 100
    print(f"Voltage: {voltage}, Watts: {watts}")
    return voltage, watts