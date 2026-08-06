import base64
import io
import os
import tempfile

import numpy as np
from PIL import Image


class ImageToBase64:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "image_format": (["jpeg", "png"], {"default": "jpeg"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "BFL/Utils"

    def convert(self, image, image_format="jpeg"):
        img_array = (image[0].numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(img_array)

        pil_image = pil_image.convert("RGB")

        buffer = io.BytesIO()
        pil_image.save(buffer, format=image_format.upper())

        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return (b64,)


class VideoToBase64:
    """Convert a ComfyUI VIDEO (LoadVideo output or a Flux 3 Video result) to a base64 MP4 string.

    Reads the video's stream source directly when it is already an MP4 in
    memory or on disk; anything else is remuxed to MP4 via VideoInput.save_to.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("VIDEO",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "convert"
    CATEGORY = "BFL/Utils"

    def convert(self, video):
        source = video.get_stream_source() if hasattr(video, "get_stream_source") else None
        if isinstance(source, io.BytesIO):
            data = source.getvalue()
        elif isinstance(source, str) and source.lower().endswith(".mp4"):
            with open(source, "rb") as f:
                data = f.read()
        else:
            fd, temp_path = tempfile.mkstemp(suffix=".mp4")
            os.close(fd)
            try:
                video.save_to(temp_path)
                with open(temp_path, "rb") as f:
                    data = f.read()
            finally:
                os.remove(temp_path)
        print(f"[BFL] Video encoded to base64 ({len(data) / (1024 * 1024):.1f} MB)")
        return (base64.b64encode(data).decode("utf-8"),)


NODE_CLASS_MAPPINGS = {"ImageToBase64_BFL": ImageToBase64, "VideoToBase64_BFL": VideoToBase64}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageToBase64_BFL": "Image to Base64 (BFL)",
    "VideoToBase64_BFL": "Video to Base64 (BFL)",
}
