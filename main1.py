from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("models/last.pt")

#    # Train the model
#    train_results = model.train(
#        data="config.yaml",  # path to dataset YAML
#        epochs=125,  # number of training epochs
#        imgsz=640,  # training image size
#        device=0  # device to run on, i.e. device=0 or device=0,1,2,3 or device=cpu
#    )

    # Використання моделі для передбачення
    results = model.predict(
        source=r"C:\Users\yehor\Documents\GitHub\TesterReport\data\images\test_image.jpg",  # шлях до зображення або папки зображень
        conf=0.25,  # встановлення порогу confidence threshold (за замовчуванням 0.25)
        imgsz=640,  # розмір зображення для передбачення
        save=True,  # збереження передбачених результатів
        save_txt=True  # збереження результатів у текстовому форматі
    )

# Виведення результатів
    for result in results:
        print(result.boxes)  
        result.show()

# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118