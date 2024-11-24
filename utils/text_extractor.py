import pytesseract
import cv2

def extract_text_from_field(image, bounding_box):
    """
    Виділяє текст з певної області зображення.
    :param image: Зображення у форматі OpenCV
    :param bounding_box: Координати області (x1, y1, x2, y2)
    :return: Розпізнаний текст
    """
    x1, y1, x2, y2 = bounding_box
    field_image = image[y1:y2, x1:x2]
    gray_image = cv2.cvtColor(field_image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray_image, config='--psm 6')  # Використовуємо PSM для розпізнавання тексту
    return text