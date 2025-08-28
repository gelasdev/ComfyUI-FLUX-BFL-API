from .base import BaseFlux


class FluxPro11(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "width": ("INT", {"default": 1440, "min": 256, "max": 1440}),
                "height": ("INT", {"default": 1440, "min": 256, "max": 1440}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, width, height, prompt_upsampling, safety_tolerance, output_format, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-pro-1.1", arguments, config)


class FluxDev(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "width": ("INT", {"default": 1024, "min": 256, "max": 1440}),
                "height": ("INT", {"default": 768, "min": 256, "max": 1440}),
                "steps": ("INT", {"default": 28, "min": 1, "max": 50}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "guidance": ("FLOAT", {"default": 3, "min": 1.5, "max": 5}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, width, height, steps, prompt_upsampling, safety_tolerance, guidance, output_format, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "guidance": guidance,
            "output_format": output_format,
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-dev", arguments, config)
        
class FluxDevRedux(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "image_prompt": ("STRING", {"default": "", "multiline": True}),
                "width": ("INT", {"default": 1024, "min": 256, "max": 1440}),
                "height": ("INT", {"default": 768, "min": 256, "max": 1440}),
                "steps": ("INT", {"default": 28, "min": 1, "max": 50}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "guidance": ("FLOAT", {"default": 3, "min": 1.5, "max": 5}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, image_prompt, width, height, steps, prompt_upsampling, safety_tolerance, guidance, output_format, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "image_prompt": image_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "guidance": guidance,
            "output_format": output_format,
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-dev", arguments, config)

class FluxPro(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "width": ("INT", {"default": 1024, "min": 256, "max": 1440}),
                "height": ("INT", {"default": 768, "min": 256, "max": 1440}),
                "steps": ("INT", {"default": 40, "min": 1, "max": 50}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "guidance": ("FLOAT", {"default": 2.5, "min": 1.5, "max": 5}),
                "interval": ("INT", {"default": 2, "min": 1, "max": 4}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, width, height, steps, prompt_upsampling, safety_tolerance, guidance, interval, output_format, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "guidance": guidance,
            "interval": interval,
            "output_format": output_format,
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-pro", arguments, config)


class FluxPro11Ultra(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "aspect_ratio": (["16:9", "4:3", "1:1", "3:2", "21:9","9:16", "3:4", "2:3", "9:21"], {"default": "16:9"}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "raw": ("BOOLEAN", {"default": False})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, aspect_ratio, safety_tolerance, output_format, raw, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
            "raw": raw
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-pro-1.1-ultra", arguments, config)

class FluxProFill(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("STRING", {"default": None}),
                "mask": ("STRING", {"default": None}),
                "prompt": ("STRING", {"default": None, "multiline": True}),
                "steps": ("INT", {"default": 28, "min": 15, "max": 50}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "guidance": ("FLOAT", {"default": 60.0, "min": 1.5, "max": 100.0}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, image, mask=None, prompt=None, steps=50, prompt_upsampling=False, guidance=60.0,
                      safety_tolerance=2, output_format="jpeg", seed=-1, config=None):
        arguments = {
            "image": image,
            "steps": steps,
            "prompt_upsampling": prompt_upsampling,
            "guidance": guidance,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }

        if seed != -1:
            arguments["seed"] = seed

        if mask is not None:
            if mask:
                arguments["mask"] = mask
            else:
                print("Warning: Mask image could not be encoded. Proceeding without mask.")

        if prompt is not None:
            arguments["prompt"] = prompt

        return super().generate_image("flux-pro-1.0-fill", arguments, config)

class FluxProCanny(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "control_image": ("STRING", {"default": None}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "steps": ("INT", {"default": 28, "min": 15, "max": 50}),
                "guidance": ("FLOAT", {"default": 60.0, "min": 1.5, "max": 100.0}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, control_image, prompt_upsampling, steps, guidance, safety_tolerance, output_format, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "control_image": control_image,
            "prompt_upsampling": prompt_upsampling,
            "steps": steps,
            "guidance": guidance,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-pro-1.0-canny", arguments, config)


class FluxProDepth(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "control_image": ("STRING", {"default": None}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "steps": ("INT", {"default": 28, "min": 15, "max": 50}),
                "guidance": ("FLOAT", {"default": 60.0, "min": 1.5, "max": 100.0}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, control_image, prompt_upsampling, steps, guidance, safety_tolerance, output_format, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "control_image": control_image,
            "prompt_upsampling": prompt_upsampling,
            "steps": steps,
            "guidance": guidance,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-pro-1.0-depth", arguments, config)

class FluxPro11Redux(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "image_prompt": ("STRING", {"default": None}),
                "width": ("INT", {"default": 1440, "min": 256, "max": 1440}),
                "height": ("INT", {"default": 1440, "min": 256, "max": 1440}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, image_prompt, width, height, prompt_upsampling, safety_tolerance, output_format, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "image_prompt": image_prompt,
            "width": width,
            "height": height,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-pro-1.1", arguments, config)
        
class FluxPro11UltraRedux(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "image_prompt": ("STRING", {"default": "", "multiline": True}),
                "image_prompt_strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0}),
                "aspect_ratio": (["16:9", "4:3", "1:1", "3:2", "21:9", "9:16", "3:4", "2:3", "9:21"], {"default": "16:9"}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "raw": ("BOOLEAN", {"default": False})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, image_prompt, image_prompt_strength, aspect_ratio, safety_tolerance, output_format, raw, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "image_prompt": image_prompt,
            "image_prompt_strength": image_prompt_strength,
            "aspect_ratio": aspect_ratio,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
            "raw": raw
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-pro-1.1-ultra", arguments, config)

class FluxKontextPro(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "input_image": ("STRING", {"default": None}),
                "aspect_ratio": (["16:9", "4:3", "1:1", "3:2", "21:9", "9:16", "3:4", "2:3", "9:21"], {"default": "16:9"}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, input_image, aspect_ratio, prompt_upsampling, safety_tolerance, output_format, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "input_image": input_image,
            "aspect_ratio": aspect_ratio,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-kontext-pro", arguments, config)

class FluxKontextMax(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "input_image": ("STRING", {"default": None}),
                "aspect_ratio": (["16:9", "4:3", "1:1", "3:2", "21:9", "9:16", "3:4", "2:3", "9:21"], {"default": "16:9"}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, input_image, aspect_ratio, prompt_upsampling, safety_tolerance, output_format, seed=-1, config=None):
        arguments = {
            "prompt": prompt,
            "input_image": input_image,
            "aspect_ratio": aspect_ratio,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-kontext-max", arguments, config)

NODE_CLASS_MAPPINGS = {
    "FluxPro_BFL": FluxPro,
    "FluxPro11_BFL": FluxPro11,
    "FluxDev_BFL": FluxDev,
    "FluxPro11Ultra_BFL": FluxPro11Ultra,
    "FluxDevRedux_BFL": FluxDevRedux,
    "FluxPro11Redux_BFL": FluxPro11Redux,
    "FluxPro11UltraRedux_BFL": FluxPro11UltraRedux,
    "FluxProFill_BFL": FluxProFill,
    "FluxProCanny_BFL": FluxProCanny,
    "FluxProDepth_BFL": FluxProDepth,
    "FluxKontextPro_BFL": FluxKontextPro,
    "FluxKontextMax_BFL": FluxKontextMax
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxPro_BFL": "Flux Pro (BFL)",
    "FluxPro11_BFL": "Flux Pro 1.1 (BFL)",
    "FluxDev_BFL": "Flux Dev (BFL)",
    "FluxPro11Ultra_BFL": "Flux Pro 1.1 Ultra (BFL)",
    "FluxDevRedux_BFL": "Flux Dev Redux (BFL)",
    "FluxPro11Redux_BFL": "Flux Pro 1.1 Redux (BFL)",
    "FluxPro11UltraRedux_BFL": "Flux Pro 1.1 Ultra Redux (BFL)",
    "FluxProFill_BFL": "Flux Pro Fill (BFL)",
    "FluxProCanny_BFL": "Flux Pro Canny (BFL)",
    "FluxProDepth_BFL": "Flux Pro Depth (BFL)",
    "FluxKontextPro_BFL": "Flux Kontext Pro (BFL)",
    "FluxKontextMax_BFL": "Flux Kontext Max (BFL)"
}
