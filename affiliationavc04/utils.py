#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
import os
import re

import cv2

# import keras_ocr
import numpy as np
from django.forms import fields
from matplotlib import image
from pdf2image import convert_from_path
from PIL import Image
# from unidecode import unidecode

# pipeline = keras_ocr.pipeline.Pipeline()


ZONES = {
    "last_name": [4, 140, 251, 192],
    "maternal_name": [254, 140, 499, 192],
    "first_name": [500, 140, 748, 192],
    "insured_number": [751, 140, 990, 197],
    "birthdate": [4, 248, 252, 297],
    "genre": [255, 222, 373, 295],
    "area": [375, 241, 538, 297],
    "address": [540, 238, 737, 304],
    "door_number": [742, 249, 832, 294],
    "location": [836, 248, 991, 296],
    "salary": [4, 328, 249, 382],
    "joining_police": [603, 352, 993, 389],
    "employer_number": [664, 413, 946, 449],
}


def pdf_to_images(pdf_path, dpi=300):
    ext = os.path.splitext(pdf_path)[1].lower()
    if ext == ".pdf":
        return convert_from_path(pdf_path, dpi=dpi)
    else:
        return [Image.open(pdf_path).convert("RGB")]


def remove_signature(img):
    th = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10
    )

    # morfología para unir trazos finos
    kernel = np.ones((2, 2), np.uint8)

    erosion = cv2.erode(th, kernel, iterations=1)
    # La dilatación revierte el daño de la erosión en las áreas gruesas, recuperando un poco el sello/firma.
    limpieza = cv2.dilate(erosion, kernel, iterations=1)

    # Después de este paso, 'limpieza' debería contener solo las firmas y sellos como manchas blancas.

    # 4. Invertir la máscara y Aplicar (Eliminar)
    # Invertimos 'limpieza' para crear una MÁSCARA donde las firmas/sellos sean NEGRO (0) y todo lo demás sea BLANCO (255).
    mask = cv2.bitwise_not(limpieza)

    return mask


def correct_img(pil_img, points, image_size, display_size):
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # =================================================================
    # 1. Eliminar firmas y sellos
    mask = remove_signature(gray)

    # 2. Aplicar Desenfoque Gaussiano (elimina ruido, suaviza)
    blur = cv2.GaussianBlur(mask, (5, 5), 0)

    edged = cv2.Canny(blur, 10, 150)
    kernel = np.ones((3, 3))
    dilatation = cv2.dilate(edged, kernel, iterations=1)
    cnts, _ = cv2.findContours(dilatation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    screenCnt = None
    max_area = 0
    # Recorrer los contornos encontrados
    for c in cnts:
        area = cv2.contourArea(c)
        # Filtramos por un área mínima para evitar el ruido pequeño
        if area > 1000:
            # Aproximación de polígono:
            # Encuentra una forma poligonal con menos vértices que aún se asemeje al contorno original.
            # 0.02 * cv2.arcLength(c, True) es el factor de tolerancia.
            perimetro = cv2.arcLength(c, True)
            aprox = cv2.approxPolyDP(c, 0.02 * perimetro, True)

            # Si la aproximación tiene 4 puntos, asumimos que es el documento
            if area > max_area and len(aprox) == 4:
                max_area = area
                screenCnt = aprox

    if screenCnt is None:
        print("Error: No se pudo encontrar un contorno de 4 puntos (documento).")
        exit()

    scale_x = image_size["width"] / display_size["width"]
    scale_y = image_size["height"] / display_size["height"]

    # 🔹 Escalar puntos
    if isinstance(points[0], dict):
        points = np.array(
            [[p["x"] * scale_x, p["y"] * scale_y] for p in points], dtype="float32"
        )
    else:
        points = np.array(
            [[p[0] * scale_x, p[1] * scale_y] for p in points], dtype="float32"
        )

    # if isinstance(points[0], dict):
    #     points = np.array([[p["x"], p["y"]] for p in points], dtype="float32")
    # else:
    #     points = np.array(points, dtype="float32")
    # pts = np.array(points, dtype="float32")
    print(
        f"esto es el screenCnt: { screenCnt }, pero estos son los puntos procesados: {points}, los tipos son {type(screenCnt)} y {type(points)}"
    )
    cv2.drawContours(img, [points.astype(int)], -1, (0, 255, 0), 2)
    cv2.circle(img, tuple(screenCnt[0][0]), 7, (0, 0, 255), 2)
    cv2.circle(img, tuple(screenCnt[1][0]), 7, (0, 0, 255), 2)
    cv2.circle(img, tuple(screenCnt[2][0]), 7, (0, 0, 255), 2)
    cv2.circle(img, tuple(screenCnt[3][0]), 7, (0, 0, 255), 2)
    cv2.imshow("Imagen", img)
    # cv2.setMouseCallback("Imagen", click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    pts = np.array(points, dtype="float32")
    # Ordenar puntos si vienen desordenados
    if pts.shape != (4, 2):
        raise ValueError("Los puntos deben tener forma (4,2)")
    pts = order_points(pts)

    # 7. Calcular las dimensiones de la imagen de destino (anchura y altura máximas)
    # Calcular la anchura máxima (distancia entre superior derecha y superior izquierda, y entre inferior derecha e inferior izquierda)
    widthA = np.sqrt(((pts[2][0] - pts[3][0]) ** 2) + ((pts[2][1] - pts[3][1]) ** 2))
    widthB = np.sqrt(((pts[1][0] - pts[0][0]) ** 2) + ((pts[1][1] - pts[0][1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # Calcular la altura máxima (distancia entre superior derecha e inferior derecha, y entre superior izquierda e inferior izquierda)
    heightA = np.sqrt(((pts[1][0] - pts[2][0]) ** 2) + ((pts[1][1] - pts[2][1]) ** 2))
    heightB = np.sqrt(((pts[0][0] - pts[3][0]) ** 2) + ((pts[0][1] - pts[3][1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # Definir los puntos de destino (la imagen 'vista desde arriba' y recortada)
    dst = np.array(
        [
            [0, 0],  # Superior Izquierda
            [maxWidth - 1, 0],  # Superior Derecha
            [maxWidth - 1, maxHeight - 1],  # Inferior Derecha
            [0, maxHeight - 1],
        ],  # Inferior Izquierda
        dtype="float32",
    )

    # 8. Obtener la matriz de transformación de perspectiva
    M = cv2.getPerspectiveTransform(pts, dst)

    # 9. Aplicar la transformación de perspectiva
    warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))

    # Opcional: convertir a escala de grises y aplicar umbral para un look de "escaneo"
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    warped = resize_image(warped, 1000, 600)
    if warped is None:
        return None

    cv2.imshow("corregido", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return warped


def preprocess_image(pil_img):
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur: np.ndarray = cv2.GaussianBlur(gray, (3, 3), 0)

    contrast = np.std(blur)
    mean_intensity = np.mean(blur)
    if contrast < 20:
        # Imagen plana o lavada → refuerzo fuerte
        alpha, beta = 1.6, -25
        kernel = np.array([[0, -1, 0], [-1, 6, -1], [0, -1, 0]])
        erode_iter = 1
    # elif contrast > 35:
    #     # Imagen ya contrastada → refuerzo mínimo
    #     alpha, beta = 2.3, -45
    #     kernel = np.array([[0, -2, 0], [-2, 9, -2], [0, -2, 0]])
    #     erode_iter = 0
    elif contrast > 37:
        # Imagen ya contrastada → refuerzo mínimo
        alpha, beta = 1.9, -40
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        erode_iter = 2
    else:
        # Intermedio
        alpha, beta = 1.7, 0
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        erode_iter = 0

    # 4️⃣ Umbral adaptativo para resaltar texto sobre fondo no uniforme
    enhanced = cv2.convertScaleAbs(blur, alpha=alpha, beta=beta)
    # th = cv2.adaptiveThreshold(
    #     gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10
    # )

    # --- 3️⃣ Umbral adaptativo u Otsu (elige el mejor automáticamente) ---
    _, otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    adapt = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 8
    )
    # Combinar ambos suavemente
    th = cv2.bitwise_and(otsu, adapt)
    # 5️⃣ Invertir si el texto queda blanco sobre negro (keras-ocr espera texto oscuro)
    white_ratio = np.mean(th > 127)
    if white_ratio > 0.5:  # si la mayoría es blanca → invertir
        th = cv2.bitwise_not(th)

    # 6️⃣ Mejorar nitidez
    # kernel = np.array([[0, -1, 0], [-1, 6, -1], [0, -1, 0]])
    sharp = cv2.filter2D(th, -1, kernel)

    if erode_iter > 0 & erode_iter < 2:
        sharp = cv2.erode(sharp, np.ones((1, 1), np.uint8), iterations=1)
    if erode_iter >= 2:
        sharp = cv2.erode(sharp, np.ones((2, 2), np.uint8), iterations=1)

    # 7️⃣ Redimensionar para mejorar reconocimiento
    h, w = sharp.shape
    scale = 2.0 if h < 60 else 1.0
    resized = cv2.resize(sharp, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 8️⃣ Padding blanco alrededor
    bordered = cv2.copyMakeBorder(resized, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=255)

    th = cv2.cvtColor(bordered, cv2.COLOR_GRAY2RGB)
    cv2.imshow("prepreses", th)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return th


def resize_image(image_path, target_width, target_height):
    img = image_path
    if img is None:
        print(f"Error: No se pudo cargar la imagen en {image_path}")
        return None

    # Redimensionar la imagen
    # cv2.INTER_AREA es bueno para reducir, cv2.INTER_LINEAR para ampliar
    resized_img = cv2.resize(
        img, (target_width, target_height), interpolation=cv2.INTER_LINEAR
    )

    return resized_img


def order_points(pts):
    # Inicializar el arreglo de 4 puntos ordenados: TL, TR, BR, BL
    rect = np.zeros((4, 2), dtype="float32")

    # Suma de coordenadas (min para TL, max para BR)
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # Superior Izquierda
    rect[2] = pts[np.argmax(s)]  # Inferior Derecha

    # Diferencia de coordenadas (min para TR, max para BL)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # Superior Derecha
    rect[3] = pts[np.argmax(diff)]  # Inferior Izquierda

    return rect


points = []


def click_event(event, x, y, flags, param):
    # if event == cv2.EVENT_LBUTTONDOWN:  # click izquierdo
    #     print(f"Coordenada: x={x}, y={y}")

    global points, img_display

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            # Almacena el punto
            points.append((x, y))
            print(f"Punto {len(points)} seleccionado: ({x}, {y})")

            # Dibuja un círculo en el punto seleccionado para visualización
            cv2.circle(img_display, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Seleccione 4 Puntos", img_display)


def crop_zone(img, zone):
    h, w = img.shape[:2]
    x1, y1, x2, y2 = [int(c * w) if c <= 1 else int(c) for c in zone]
    return img[y1:y2, x1:x2]


def extract_fields_from_image(img):
    resultados = {}
    for etiqueta, zone in ZONES.items():
        cropped = crop_zone(img, zone)
        proc = preprocess_image(Image.fromarray(cropped))
        prediction = pipeline.recognize([proc])[0]
        text = " ".join([t for t, _ in prediction])
        # limpiar texto
        # text = re.sub(r"[^A-Z0-9ÁÉÍÓÚÑÜ\.\,\-\s/]", "", text.strip().upper())
        text = clean_text(text, etiqueta)

        resultados[etiqueta] = text or None
    return resultados


def ocr_common_corrections(text: str, expected_type: str = "auto"):
    text = text.upper()
    # Limpieza básica
    text = text.strip()

    # Detección automática
    if expected_type == "auto":
        if re.fullmatch(r"[0-9\-\s]+", text):
            expected_type = "numeric"
        elif re.fullmatch(r"[A-Za-z\s]+", text):
            expected_type = "alpha"
        else:
            # Si tiene mezcla, no cambia nada
            return text

    if expected_type == "numeric":
        # Cambiar letras que parecen números
        replacements = {
            "O": "0",
            "o": "0",
            "D": "0",
            "I": "1",
            "T": "1",
            "l": "1",
            "Z": "2",
            "A": "4",
            "S": "5",
            "B": "8",
        }

    elif expected_type == "alpha":
        # Cambiar números que parecen letras
        replacements = {
            "0": "O",
            "0": "D",
            "2": "Z",
            "1": "I",
            "4": "A",
            "5": "S",
            "8": "B",
        }

    # Aplicar reemplazos
    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def clean_text(text, field):
    text = text.strip().upper()
    text = ocr_common_corrections(text)
    # print(f"tercero: {text}")
    if field == "insured_number":
        text = re.sub(r"[^A-Z0-9-]", "", text)
        text = re.sub(r"[-\s_]+", "-", text)
        text = ocr_common_corrections(text)
        # text = ocr_common_corrections(text)
        match = re.search(r"\b\d{2}-\d{4}-[A-Z]{3}\b", text)
        if match:
            return match.group(0)
        else:
            raw = re.sub(r"[^A-Z0-9]", "", text)
            print(f"type: {type(raw)}")
            if len(raw) >= 9:
                # print(f"segundo: {raw[2:6]}")
                raw_aux = ocr_common_corrections(raw[:6], expected_type="numeric")
                raw = raw_aux + ocr_common_corrections(raw[6:9], expected_type="alpha")
                print(f"primero: {raw_aux}")
                print(f"tercero: {raw}")
                text = f"{raw[0:2]}-{raw[2:6]}-{raw[6:9]}"
            else:
                text = raw  # dejarlo tal cual si incompleto
        # return re.sub(r"[^0-9A-Z\-]", "", text)

    elif field in ["first_name", "last_name", "maternal_name"]:
        text = re.sub(r"[^A-ZÁÉÍÓÚÑÜ\s-]", "", text)
        text = ocr_common_corrections(text, expected_type="alpha")
    elif field == "birthdate":
        text = re.sub(r"[^0-9/.-]", "", text)
    elif field in ["insured_number", "employer_number"]:
        text = re.sub(r"[^0-9]", "", text)
    return text


def run_keras_ocr_on_images(cv2_images):
    imgs = [cv2.cvtColor(i, cv2.COLOR_BGR2RGB) for i in cv2_images]
    # results = pipeline.recognize(imgs)
    # results = None
    normalized = []
    # for res in results:
    #     normalized.append(
    #         [(t.strip(), np.array(box).astype(int).tolist()) for t, box in res]
    #     )
    return normalized


def process_file_and_extract(path):
    img = Image.open(path).convert("RGB")
    # img = correct_img(img)
    # fields = remove_signature(img)
    fields = extract_fields_from_image(img)

    # fields = preprocess_image(img)

    print(fields)
    # images = pdf_to_images(path)
    # fields = [preprocess_image(img) for img in images]

    return fields
