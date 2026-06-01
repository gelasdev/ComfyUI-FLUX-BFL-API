from .base import BaseFlux


class FluxErase(BaseFlux):
    CATEGORY = "BFL"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    "STRING",
                    {"default": "", "tooltip": "Input image (base64-encoded string)."},
                ),
                "mask": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": (
                            "Black/white mask (base64-encoded string). White (255) = remove, black (0) = keep. "
                            "Must match the input image dimensions."
                        ),
                    },
                ),
                "dilate_pixels": (
                    "INT",
                    {
                        "default": 10,
                        "min": 0,
                        "max": 25,
                        "tooltip": (
                            "Pixels to dilate the mask before removal. Range 0-25, default 10. "
                            "Helps the model fully cover object edges."
                        ),
                    },
                ),
                "safety_tolerance": (
                    "INT",
                    {
                        "default": 2,
                        "min": 0,
                        "max": 5,
                        "tooltip": (
                            "Tolerance level for input and output moderation. "
                            "Between 0 and 5, 0 being most strict, 5 being least strict."
                        ),
                    },
                ),
                "output_format": (
                    ["png", "jpeg"],
                    {"default": "png", "tooltip": "png (default) or jpeg."},
                ),
            },
            "optional": {
                "seed": (
                    "INT",
                    {"default": -1, "tooltip": "Optional seed for reproducibility. -1 = random."},
                ),
                "webhook_url": (
                    "STRING",
                    {"default": "", "tooltip": "URL to receive webhook notifications."},
                ),
                "webhook_secret": (
                    "STRING",
                    {"default": "", "tooltip": "Optional secret for webhook signature verification."},
                ),
                "config": (
                    "BFL_CONFIG",
                    {"tooltip": "Optional Flux Config (BFL) override for x-key, base URL, and region."},
                ),
            },
        }

    def generate_image(
        self,
        image,
        mask,
        dilate_pixels,
        safety_tolerance,
        output_format,
        seed=-1,
        webhook_url="",
        webhook_secret="",
        config=None,
    ):
        arguments = {
            "image": image,
            "mask": mask,
            "dilate_pixels": dilate_pixels,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
        }
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        return super().generate_image("flux-tools/erase-v1", arguments, config)


class FluxOutpaint(BaseFlux):
    CATEGORY = "BFL"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_image": (
                    "STRING",
                    {"default": "", "tooltip": "Reference image to expand (base64-encoded string)."},
                ),
                "width": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 64,
                        "max": 4096,
                        "step": 32,
                        "tooltip": "Target canvas width in pixels (>=64).",
                    },
                ),
                "height": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 64,
                        "max": 4096,
                        "step": 32,
                        "tooltip": "Target canvas height in pixels (>=64).",
                    },
                ),
                "output_format": (
                    ["png", "jpeg"],
                    {"default": "png", "tooltip": "png (default) or jpeg."},
                ),
            },
            "optional": {
                "prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": (
                            "Experimental: optional text guidance for the outpainted region. "
                            "The model may not strictly follow this prompt; the visual content of the input image "
                            "is the primary signal. Leave unset for default behavior."
                        ),
                    },
                ),
                "center_reference": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": (
                            "When True (default), the server centers the reference image on the canvas "
                            "(reference_offset_x/y are omitted from the request). "
                            "When False, the reference_offset_x/y values below are sent explicitly."
                        ),
                    },
                ),
                "reference_offset_x": (
                    "INT",
                    {
                        "default": 0,
                        "min": -8192,
                        "max": 8192,
                        "tooltip": (
                            "Left offset (px) of the reference image's top-left corner on the canvas. "
                            "Negative values allowed. None = center horizontally."
                        ),
                    },
                ),
                "reference_offset_y": (
                    "INT",
                    {
                        "default": 0,
                        "min": -8192,
                        "max": 8192,
                        "tooltip": (
                            "Top offset (px) of the reference image's top-left corner on the canvas. "
                            "Negative values allowed. None = center vertically."
                        ),
                    },
                ),
                "auto_crop": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": (
                            "If true, crop the reference image to the canvas bounds when it extends beyond the edges. "
                            "Defaults to false (out-of-bounds placements return 422)."
                        ),
                    },
                ),
                "config": (
                    "BFL_CONFIG",
                    {"tooltip": "Optional Flux Config (BFL) override for x-key, base URL, and region."},
                ),
            },
        }

    def generate_image(
        self,
        input_image,
        width,
        height,
        output_format,
        prompt="",
        center_reference=True,
        reference_offset_x=0,
        reference_offset_y=0,
        auto_crop=False,
        config=None,
    ):
        arguments = {
            "input_image": input_image,
            "width": width,
            "height": height,
            "output_format": output_format,
        }
        if not center_reference:
            arguments["reference_offset_x"] = reference_offset_x
            arguments["reference_offset_y"] = reference_offset_y
        if prompt and prompt.strip():
            arguments["prompt"] = prompt
        if auto_crop:
            arguments["auto_crop"] = auto_crop
        return super().generate_image("flux-tools/outpainting-v1", arguments, config)


class FluxVirtualTryOn(BaseFlux):
    CATEGORY = "BFL"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "person": (
                    "STRING",
                    {"default": "", "tooltip": "Person image (base64-encoded string). The subject to dress."},
                ),
                "garment": (
                    "STRING",
                    {"default": "", "tooltip": "Garment image (base64-encoded string). The clothing to apply."},
                ),
                "prompt": (
                    "STRING",
                    {
                        "default": "TRY-ON: The person of image 1 wearing garments of image 2.",
                        "multiline": True,
                        "tooltip": (
                            "Text guidance for the try-on. Describe the garment and how it is worn while "
                            "preserving the person's face and pose."
                        ),
                    },
                ),
                "safety_tolerance": (
                    "INT",
                    {
                        "default": 2,
                        "min": 0,
                        "max": 5,
                        "tooltip": (
                            "Tolerance level for input and output moderation. "
                            "Between 0 and 5, 0 being most strict, 5 being least strict."
                        ),
                    },
                ),
                "output_format": (
                    ["jpeg", "png"],
                    {"default": "jpeg", "tooltip": "jpeg (default) or png."},
                ),
            },
            "optional": {
                "seed": (
                    "INT",
                    {"default": -1, "tooltip": "Optional seed for reproducibility. -1 = random."},
                ),
                "webhook_url": (
                    "STRING",
                    {"default": "", "tooltip": "URL to receive webhook notifications."},
                ),
                "webhook_secret": (
                    "STRING",
                    {"default": "", "tooltip": "Optional secret for webhook signature verification."},
                ),
                "config": (
                    "BFL_CONFIG",
                    {"tooltip": "Optional Flux Config (BFL) override for x-key, base URL, and region."},
                ),
            },
        }

    def generate_image(
        self,
        person,
        garment,
        prompt,
        safety_tolerance,
        output_format,
        seed=-1,
        webhook_url="",
        webhook_secret="",
        config=None,
    ):
        arguments = {
            "prompt": prompt,
            "person": person,
            "garment": garment,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
        }
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        return super().generate_image("flux-tools/vto-v1", arguments, config)


NODE_CLASS_MAPPINGS = {
    "FluxErase_BFL": FluxErase,
    "FluxOutpaint_BFL": FluxOutpaint,
    "FluxVirtualTryOn_BFL": FluxVirtualTryOn,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxErase_BFL": "Flux Erase (BFL)",
    "FluxOutpaint_BFL": "Flux Outpaint (BFL)",
    "FluxVirtualTryOn_BFL": "Flux Virtual Try-On (BFL)",
}
