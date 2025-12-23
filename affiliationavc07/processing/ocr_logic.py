#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
import re

import cv2
import numpy as np
from hospital.models import Hospital
from paddleocr import PaddleOCR
from datetime import datetime, timedelta
from threading import Lock


ocr_lock = Lock()
# ocr = PaddleOCR(lang="es", use_angle_cls=True)
ocr = PaddleOCR(lang="es", use_angle_cls=True, show_log=False)


def get_safe_ocr_result(pil_img):
    with ocr_lock:
        return ocr.ocr(pil_img, cls=True)


def parse_date_safe(date_str: str):
    """Intenta convertir fechas incompletas o con formato incorrecto."""
    if not date_str:
        return None

    date_str = date_str.strip().replace("/", "-")

    # Casos típicos correctos
    for fmt in ("%d-%m-%Y", "%d-%m-%y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # Caso: fecha deformada tipo "310-25" → "31-10-2025"
    if re.match(r"^\d{3,6}$", date_str):
        parts = re.findall(r"\d", date_str)
        if len(parts) >= 5:
            d = "".join(parts[:2])
            m = "".join(parts[2:4])
            y = "".join(parts[4:])
            try:
                return datetime.strptime(f"{d}-{m}-{y}", "%d-%m-%y")
            except Exception:
                try:
                    return datetime.strptime(f"{d}-{m}-{y}", "%d-%m-%Y")
                except Exception:
                    return None
    return None


def extract_days_from_text(text: str):
    """Extrae el número de días incluso si está incrustado en texto (TRES3DIAS)."""
    if not text:
        return None

    m = re.search(r"(\d+)", text)
    if m:
        return int(m.group(1))

    num_map = {
        "UNO": 1,
        "DOS": 2,
        "TRES": 3,
        "CUATRO": 4,
        "CINCO": 5,
        "SEIS": 6,
        "SIETE": 7,
        "OCHO": 8,
        "NUEVE": 9,
        "DIEZ": 10,
    }
    for palabra, val in num_map.items():
        if palabra in text.upper():
            return val
    return None


def normalize_incapacity_fields(data: dict):
    """Corrige from_date, to_date y days_incapacity en el diccionario OCR."""
    from_raw = data.get("from_date")
    to_raw = data.get("to_date")
    days_raw = data.get("days_incapacity")

    from_date = parse_date_safe(from_raw)
    to_date = parse_date_safe(to_raw)
    days_incapacity = extract_days_from_text(days_raw)

    # Si to_date es inválida pero hay días válidos → calcularla
    if from_date and not to_date and days_incapacity:
        to_date = from_date + timedelta(days=days_incapacity - 1)

    # Si no hay días pero sí fechas → calcular diferencia
    if from_date and to_date and not days_incapacity:
        days_incapacity = (to_date - from_date).days + 1  # inclusivo

    # Si hay días pero falta to_date → estimar
    if from_date and days_incapacity and not to_date:
        to_date = from_date + timedelta(days=days_incapacity - 1)

    # Guardar en el mismo formato original
    data["from_date"] = from_date.strftime("%d-%m-%Y") if from_date else from_raw
    data["to_date"] = to_date.strftime("%d-%m-%Y") if to_date else to_raw
    data["days_incapacity"] = str(days_incapacity) if days_incapacity else days_raw

    return data


def preprocess(pil_img):
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (1, 1), 0)
    return blur


def extract_value_from_line(text, keyword):
    match = re.search(rf"{keyword}[:\s\-\.]*([A-Z0-9ÁÉÍÓÚÑ\-\s\.]+)", text)
    if match:
        return match.group(1).strip()
    return None


FIELD_KEYWORDS = {
    "last_name": [r"AP\.?\s?PATERNO", r"PATERNO"],
    "maternal_name": [r"AP\.?\s?MATERNO", r"MATERNO"],
    "first_name": [r"\(?\d*\)?NOMBRES", r"NOMBRES?", "NOMBRES"],
    "middle_name": [r"NOMBRES?"],
    "insured_number": ["N°ASEGURADO", "NASEGURADO"],
    "employer_number": ["N°EMPLEADOR", "NEMPLEADOR"],
    "company_name": [
        r"NOMBRE\s?O\s?RAZON\s?SOCIAL\s?DEL\s?EMPLEADOR",
        "NOMBREORAZONSOCIALDELEMPLEADOR",
    ],
    "from_date": ["DESDE", "DESDE:", "DESDE."],
    "to_date": ["HASTA", "HASTA:", "HASTA."],
    "type_risk": ["TIPODERIESGO"],
    "matricula": ["MATRICULA", "MATRICULA:", "MATRICULA."],
    "isue_date": ["LUGARYFECHADEEMISION"],
    "days_incapacity": ["DIASDEINCAPACIDAD", "DEINCAPACIDAD"],
    "hospital": [
        "UNIDAD MED.:",
        "UNIDAD MED.",
        "UNIDAD MED:",
        "UNIDAD MEDICA",
        "UNIDADMED.:",
        "UNIDADMED.",
        "UNIDADMED:",
        "UNIDADMED",
        "HOSPITAL",
    ],
}


def normalize_for_match(text: str) -> str:
    if not text:
        return ""

    return re.sub(r"[\s\.\-]", "", text.upper())


def extract_fields_by_position(pil_img, qr_data):

    img = preprocess(pil_img)

    result = get_safe_ocr_result(img)

    lines = []
    for block in result:
        for line in block:
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = line[0]
            text = line[1][0].strip().upper()
            y_avg = (y1 + y2 + y3 + y4) / 4
            x_avg = (x1 + x2 + x3 + x4) / 4
            lines.append({"text": text, "x": x_avg, "y": y_avg})

    # Ordenar por posición vertical
    lines.sort(key=lambda l: (l["y"], l["x"]))

    # --- Buscar el valor debajo usando X e Y ---
    def find_nearby_text(label_line, mode="below", x_tolerance=50, y_tolerance=50):
        candidates = []
        for other in lines:
            if other is label_line:
                continue

            dx = other["x"] - label_line["x"]
            dy = other["y"] - label_line["y"]

            if mode == "below":
                if dy > 5 and dy < y_tolerance and abs(dx) < x_tolerance:
                    candidates.append((dy, other))
            elif mode == "right":
                if 0 < dx < 250 and abs(dy) < (y_tolerance / 2):
                    candidates.append((dx, other))

        if candidates:
            candidates.sort(key=lambda c: c[0])
            return candidates[0][1]["text"]
        return None

    data = {}

    # --- Buscar cada campo ---
    for line in lines:
        text = line["text"]

        # normalize_text = text.replace(" ", "")
        normalize_text = normalize_for_match(text)

        for field, keywords in FIELD_KEYWORDS.items():
            # if any(k in normalize_text for k in keywords):
            if any(normalize_for_match(k) in normalize_text for k in keywords):
                # 1️⃣ Verificar si el valor está en la misma línea (DESDE:25-08-2025)
                same_line_val = extract_value_from_line(text, keywords[0])
                existing = qr_data.get(field)
                if same_line_val:
                    if not existing:
                        data[field] = same_line_val
                    continue
                    # else:
                    #     data[field] = existing

                x_tol = (
                    50
                    if field
                    in [
                        "last_name",
                        "maternal_name",
                        "first_name",
                        "insured_number",
                        "isue_date",
                        "company_name",
                    ]
                    else 40
                )
                y_tol = 60 if field in ["employer_number"] else 30

                val = find_nearby_text(
                    line, mode="below", x_tolerance=x_tol, y_tolerance=y_tol
                )

                if val:
                    if not existing:
                        if field == "first_name":
                            data["first_name"] = val
                            data["middle_name"] = None
                        elif field == "company_name":
                            data["company_name"] = "POLICIA BOLIVIANA"
                        elif field == "employer_number":
                            data["employer_number"] = val
                        elif field == "insured_number":
                            data["insured_number"] = val
                        elif field == "isue_date":
                            data["isue_date"] = val
                        elif field == "type_risk" and "ENFERMEDAD" in text:
                            pass
                        elif field == "disease":
                            data["disease_value"] = val
                        elif field == "incapacity":
                            pass
                        else:
                            data[field] = val
                    else:
                        data[field] = existing

                # print(f"data {data}")
            if field == "type_risk" and field not in data:
                pass

    for k, v in data.items():
        if v:
            v2 = re.sub(r"[^A-Z0-9ÁÉÍÓÚÑ\s\-\.:]", "", v).strip()
            data[k] = v2

    data = normalize_incapacity_fields(data)
    return data
