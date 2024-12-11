#import depecdencies
from paddleocr import PaddleOCR, draw_ocr
from matplotlib import pyplot as plt
import cv2
import os

#instantiate model and detect
ocr_model = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
img_path = os.path.join('.', 'test.jpg')

def generate_string(data):
    result = []
    for res in data:
        result.append(res[1][0])
    return " ".join(result)

result=ocr_model.ocr(img_path, cls=True)
print(generate_string(result[0]))








        
