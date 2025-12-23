#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
import numpy as np
from PIL.Image import Image
from qreader import QReader

qreader_detector = QReader()


def read_qr_from_image(pil_image: Image):
    try:
        payload = {
            "code": None,
            "last_name": None,
            "maternal_name": None,
            "first_name": None,
            "middle_name": None,
            "insured_number": None,
            "employer_number": None,
            "company_name": None,
            "from_date": None,
            "to_date": None,
            "type_risk": None,
            "matricula": None,
            "isue_date": None,
            "days_incapacity": None,
            "hospital": None,
        }
        # 1. Asegurar formato correcto
        if isinstance(pil_image, np.ndarray):
            # Ya es un array OpenCV o NumPy
            cv_image = pil_image
        else:
            # Es PIL → convertir a OpenCV BGR
            cv_image = np.array(pil_image.convert("RGB"))[:, :, ::-1].copy()

        # 2. Detectar y decodificar el QR
        decoded_texts = qreader_detector.detect_and_decode(image=cv_image)

        if not decoded_texts or decoded_texts[0] is None:
            print("INFO: No se detectó ningún QR en la imagen.")
            return payload

        qr_string = decoded_texts[0]
        print(f"INFO: QR Detectado. Datos: {qr_string}")

        # 3. Parsear los datos
        # "09209|12323ABC|273623|Juan Perez|Razón Social S.R.L.|Dr. Apellido|2025-01-01"
        campos = qr_string.split("|")
        campo = campos[2].strip().split(" ")
        campoMat = campos[5].strip().split(" ")
        first_name = None
        middle_name = None
        last_name = None
        maternal_name = None
        if len(campo) <= 2:
            first_name = campo[0]
            last_name = campo[1]
        elif len(campo) == 3:
            first_name = campo[0]
            last_name = campo[1]
            maternal_name = campo[2]
        else:
            first_name = campo[0]
            middle_name = campo[1]
            last_name = campo[2]
            maternal_name = campo[3]

        matricula = campoMat[0]
        # Rellenar con None si faltan campos para evitar IndexError
        campos.extend([None] * (7 - len(campos)))

        payload = {
            "code": campos[0].strip() if campos[0] else None,
            "last_name": last_name,
            "maternal_name": maternal_name,
            "first_name": first_name,
            "middle_name": middle_name,
            "insured_number": campos[1].strip() if campos[1] else None,
            "employer_number": (campos[3].strip() if campos[3] else None),
            "company_name": campos[4].strip() if campos[4] else None,
            "from_date": None,
            "to_date": None,
            "type_risk": None,
            "matricula": matricula,
            "isue_date": (campos[6].strip() if campos[6] else None),
            "days_incapacity": None,
            "hospital": None,
        }

        # print(f"INFO: Datos QR parseados: {payload}")
        return payload

    except Exception as e:
        print(f"ERROR: Error procesando QR: {e}")
        return None
