import cv2
import easyocr
from ultralytics import YOLO

# Load YOLO model
model = YOLO("models/last.pt")

# Prediction on the image
results = model.predict(source=r"C:\Users\yehor\Documents\GitHub\TesterReport\data\images\test_image.jpg", conf=0.25, imgsz=640)

# Load the image
image = cv2.imread(r"C:\Users\yehor\Documents\GitHub\TesterReport\data\images\test_image.jpg")

# Initialize EasyOCR
reader = easyocr.Reader(['en'])  # Other languages can be added if needed

# Iterate through the detected fields
for result in results:
    for box in result.boxes.data.tolist():
        x_min, y_min, x_max, y_max = map(int, box[:4])

        # Crop the field area
        cropped_img = image[y_min:y_max, x_min:x_max]

        # Convert to grayscale and binarize
        gray_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        _, binary_img = cv2.threshold(gray_img, 184, 255, cv2.THRESH_BINARY_INV)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2))
        binary_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)

        # Use EasyOCR to read text from the cleaned image
        ocr_result = reader.readtext(binary_img)

        # Output OCR results
        text_combined = ""
        for detection in ocr_result:
            _, text, confidence = detection
            text_combined += text.strip() + " "
            print(f"Detected field: {text.strip()} (confidence: {confidence:.2f})")

        # View the binarized image
        cv2.imshow("Binary Image", binary_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
