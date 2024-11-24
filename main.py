import cv2
import easyocr
from ultralytics import YOLO

# Завантаження моделі YOLO
model = YOLO("models/last.pt")

# Передбачення на зображенні
results = model.predict(source=r"C:\Users\yehor\Documents\GitHub\TesterReport\data\images\test_image.jpg", conf=0.25, imgsz=640)

# Завантаження зображення
image = cv2.imread(r"C:\Users\yehor\Documents\GitHub\TesterReport\data\images\test_image.jpg")

# Ініціалізація EasyOCR
reader = easyocr.Reader(['en'])  # Можна додати інші мови за потреби

# Ітерування по знайдених полях
for result in results:
    for box in result.boxes.data.tolist():
        x_min, y_min, x_max, y_max = map(int, box[:4])

        # Обрізання області поля
        cropped_img = image[y_min:y_max, x_min:x_max]

        # Перетворення в градації сірого та бінаризація
        gray_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        _, binary_img = cv2.threshold(gray_img, 184, 255, cv2.THRESH_BINARY_INV)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2))
        binary_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)

        # Використання EasyOCR для зчитування тексту з очищеного зображення
        ocr_result = reader.readtext(binary_img)

        # Виведення результатів OCR
        text_combined = ""
        for detection in ocr_result:
            _, text, confidence = detection
            text_combined += text.strip() + " "
            print(f"Знайдене поле: {text.strip()} (довіра: {confidence:.2f})")

        
        # Перегляд бінаризованого зображення
        cv2.imshow("Binary Image", binary_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
