import re, os, cv2, numpy as np, pytesseract
from typing import Dict, Any, Optional

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # adjust if needed

def read_image(path_or_bytes):
    if isinstance(path_or_bytes, (bytes, bytearray)):
        arr = np.frombuffer(path_or_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(path_or_bytes)
    if img is None:
        raise ValueError(f"Unable to read image: {path_or_bytes}")
    return img

def preprocess_image(img, resize_max_dim=1200):
    h,w = img.shape[:2]
    max_dim = max(h,w)
    if max_dim > resize_max_dim:
        scale = resize_max_dim / max_dim
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,31,12)
    return gray

def ocr_image_text(img, lang='eng', psm=3, oem=3, config_add=None):
    config = f'--oem {oem} --psm {psm}'
    if config_add:
        config += ' ' + config_add
    return pytesseract.image_to_string(img, lang=lang, config=config)

def ocr_image_data(img, lang='eng'):
    return pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)

DOB_REGEXES = [r'(\d{2}[\/\-]\d{2}[\/\-]\d{4})', r'(\d{4}[\/\-]\d{2}[\/\-]\d{2})', r'(\d{2}\s+[A-Za-z]{3,}\s+\d{4})']
ID_NUMBER_REGEXES = [r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', r'\b(\d{12})\b', r'\b(\d{4}\s*\d{4}\s*\d{4})\b']

def find_first(patterns, text):
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None

def extract_fields(text: str) -> Dict[str, Optional[str]]:
    txt = re.sub(r'\s{2,}', ' ', text).strip()

    # DOB (keep as is if working)
    dob = find_first(DOB_REGEXES, txt)

    # PAN-like pattern: allow one trailing non-letter like ')' then clean
    pan_match = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z0-9])\b', txt)
    id_number = None
    if pan_match:
        candidate = pan_match.group(1)
        # If last char is not a letter, drop it (e.g. JYWPD8828))
        if not candidate[-1].isalpha():
            candidate = candidate[:-1]
        id_number = candidate

    # Name: look for "Name" label and take words after it
    name = None
    name_label = re.search(r'Name\s+([A-Za-z ]{3,40})', txt, flags=re.IGNORECASE)
    if name_label:
        name = name_label.group(1).strip()
    else:
        # fallback: heuristic (same as before, scanning top lines)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for ln in lines[:8]:
            if 2 <= len(ln.split()) <= 4 and re.match(r'^[A-Za-z .-]+$', ln):
                if not re.search(r'(government|national|identity|id|no\.|DOB|date|father|son|account)', ln, re.IGNORECASE):
                    name = ln
                    break

    # Address: last few non-trivial lines as before
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    address = None
    if len(lines) > 3:
        candidates = lines[-4:]
        address = ', '.join([c for c in candidates if len(c) > 8])[:200]

    return {
        "raw_text": txt,
        "name": name,
        "dob": dob,
        "id_number": id_number,
        "address_snippet": address
    }

def analyze_image_file(path_or_bytes) -> Dict[str, Any]:
    img = read_image(path_or_bytes)
    pre = preprocess_image(img)
    text = ocr_image_text(pre)
    data = ocr_image_data(pre)
    fields = extract_fields(text)
    confs = [int(x) for x in data.get('conf', []) if isinstance(x, str) and x.strip() and x != '-1']
    # handle ints in conf (avoid int.strip errors)
    confs += [int(x) for x in data.get('conf', []) if isinstance(x, (int,float)) and x > 0]
    avg_conf = float(sum(confs))/len(confs) if confs else None
    return {"fields": fields, "ocr_confidence_avg": avg_conf, "ocr_word_count": len([w for w in data.get('text',[]) if isinstance(w,str) and w.strip()]), "ocr_data": data}
