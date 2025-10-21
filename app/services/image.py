from uuid import uuid4
from fastapi import HTTPException
import base64
import time

def save_images(image_str: str, image_group: str, center_id: int) -> str:
    """
    image_group = ``students`` or ``staffs``
    Specify whose image to save and determine correct file route
    """
    if not image_str:
        raise HTTPException(status_code=400, detail="Image is empty !")
    try:
        # Format: center_id + '-' + uuid
        unique_image_id = f"{center_id}-{uuid4()}"
        with open(f"media/images/{image_group}/{unique_image_id}", "bw") as image_file:
            contents = base64.b64decode(image_str)
            image_file.write(contents)
        return unique_image_id
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file !")

async def save_image(input_file, image_group: str) :
    """
    image_group = ``students`` or ``staffs``
    Specify whose image to save and determine correct file route
    """
    current_time = str(time.time()).replace('.', '-')
    unique_image_id = f"{uuid4()}-{current_time}.jpg"

    try:
        with open(f"media/images/{image_group}/{unique_image_id}", "bw") as image_file:
            contents = await input_file.read()
            image_file.write(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file !")

    return unique_image_id