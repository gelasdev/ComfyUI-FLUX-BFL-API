import io
import base64
import numpy as np
from PIL import Image


class ImageToBase64:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "BFL/Utils"

    def convert(self, image):
        img_array = (image[0].numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array)

        pil_image = pil_image.convert("RGB")

        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG")

        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return (b64,)


NODE_CLASS_MAPPINGS = {
    "ImageToBase64_BFL": ImageToBase64
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToBase64_BFL": "Image to Base64 (BFL)"
}
