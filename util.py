from ultralytics import YOLO

# Load a model
model = YOLO("yolo11n.pt")

# Train the model
train_results = model.train(
    data="config.yaml",  # path to dataset YAML
    epochs=100,  # number of training epochs
    imgsz=640,  # training image size
    device="cpu",  # device to run on, i.e. device=0 or device=0,1,2,3 or device=cpu
)

# Використання моделі для передбачення
results = model.predict(
    source=r"C:\Users\yehor\Pictures\Dataplates\val\images",  # шлях до зображення або папки зображень
    conf=0.25,  # встановлення порогу confidence threshold (за замовчуванням 0.25)
    imgsz=640  # розмір зображення для передбачення
)
