import cv2
import numpy as np
import easyocr
import certifi

_reader=None

def get reader():
    if _reader is None:
        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
        _reader = easyocr.Reader(['ko','en'], gpu=False)
        return _reader
    
def preprocess(img_bgr):
    gray=cv2. cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
     gray = cv2.GaussianBlur(gray, (3,3), 0)
    thr = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 5
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    thr = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel)
    return thr

def run_ocr(image_path: str):
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return ""

    proc = preprocess(img_bgr)
    try:
        reader = get_reader()
        texts = reader.readtext(proc, detail=0)
        return " ".join(texts).strip()
    
    except Exception as e:
        # 오류가 났을 때 원인을 화면에라도 남기기
        # (실서비스라면 로깅으로 처리)
        return f"[OCR 오류] {type(e).__name__}: {e}"
