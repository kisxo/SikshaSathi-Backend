import cv2
import face_recognition
import matplotlib.pyplot as plt
from app.db.schemas.face_id import FaceID
import numpy
from fastapi import HTTPException

from app.db.models import student_model

def generate_face_id(image_group: str, image_id: str) -> FaceID:
    """
    image_group = ``students`` or ``staffs``
    Specify whose image to load image file from correct file route
    """
    try:
        known_image = face_recognition.load_image_file(f"media/images/{image_group}/{image_id}")
        optimized_known_image = cv2.resize(known_image, (0, 0), fx=0.25, fy=0.25)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found !")

    try:
        known_faces = face_recognition.face_encodings(face_image=optimized_known_image, num_jitters=5, model='cnn')[0]
    except Exception as e:
        raise HTTPException(status_code=404, detail="Face not detected!")

    return FaceID(face_signature=known_faces)


def verify_face_id(image, face_signature) -> bool:
    try:
        input_image = face_recognition.load_image_file(image.file)
        optimized_input_image = cv2.resize(input_image, (0, 0), fx=0.25, fy=0.25)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid image !")

    try:
        input_faces = face_recognition.face_encodings(face_image=optimized_input_image, num_jitters=5, model='cnn')[0]
    except Exception as e:
        raise HTTPException(status_code=404, detail="Face not detected!")

    known_face_id = numpy.array(face_signature)

    result = face_recognition.compare_faces([known_face_id], input_faces)

    return bool(result[0])