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
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("base64_image",)
    FUNCTION = "convert"
    CATEGORY = "BFL/Utils"

    def convert(self, image, output_format="jpeg"):
        img_array = (image[0].numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array)

        buffer = io.BytesIO()
        pil_image.save(buffer, format=output_format.upper())
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        mime = "image/jpeg" if output_format == "jpeg" else "image/png"
        return (f"data:{mime};base64,{b64}",)


NODE_CLASS_MAPPINGS = {
    "ImageToBase64_BFL": ImageToBase64
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToBase64_BFL": "Image to Base64 (BFL)"
}
