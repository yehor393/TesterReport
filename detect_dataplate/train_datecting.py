from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("models/last.pt")

    # Train the model
    train_results = model.train(
        data="config.yaml",  # path to dataset YAML
        epochs=125,  # number of training epochs
        imgsz=640,  # training image size
        device=0  # device to run on, i.e. device=0 or device=0,1,2,3 or device=cpu
    )

# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
