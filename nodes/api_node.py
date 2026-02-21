import requests
import json
from .base import BaseFlux
from .config_node import get_config_loader


class FluxPro11(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "width": ("INT", {"default": 1440, "min": 256, "max": 1440}),
                "height": ("INT", {"default": 1440, "min": 256, "max": 1440}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "image_prompt": ("STRING", {"default": ""}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, width, height, prompt_upsampling, safety_tolerance, output_format,
                       seed=-1, image_prompt="", webhook_url="", webhook_secret="", config=None):
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
        if image_prompt:
            arguments["image_prompt"] = image_prompt
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
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
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "guidance": ("FLOAT", {"default": 3, "min": 1.5, "max": 5}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "image_prompt": ("STRING", {"default": ""}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, width, height, steps, prompt_upsampling, safety_tolerance, guidance,
                       output_format, seed=-1, image_prompt="", webhook_url="", webhook_secret="", config=None):
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
        if image_prompt:
            arguments["image_prompt"] = image_prompt
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        return super().generate_image("flux-dev", arguments, config)


class FluxPro11Ultra(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "aspect_ratio": (["16:9", "4:3", "1:1", "3:2", "21:9", "9:16", "3:4", "2:3", "9:21"], {"default": "16:9"}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "raw": ("BOOLEAN", {"default": False})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "image_prompt": ("STRING", {"default": ""}),
                "image_prompt_strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, aspect_ratio, prompt_upsampling, safety_tolerance, output_format, raw,
                       seed=-1, image_prompt="", image_prompt_strength=0.1, webhook_url="", webhook_secret="", config=None):
        arguments = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
            "raw": raw
        }
        if seed != -1:
            arguments["seed"] = seed
        if image_prompt:
            arguments["image_prompt"] = image_prompt
            arguments["image_prompt_strength"] = image_prompt_strength
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        return super().generate_image("flux-pro-1.1-ultra", arguments, config)


class FluxProFill(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("STRING", {"default": None}),
                "mask": ("STRING", {"default": None}),
                "prompt": ("STRING", {"default": None, "multiline": True}),
                "steps": ("INT", {"default": 50, "min": 15, "max": 50}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "guidance": ("FLOAT", {"default": 60.0, "min": 1.5, "max": 100.0}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, image, mask=None, prompt=None, steps=50, prompt_upsampling=False, guidance=60.0,
                       safety_tolerance=2, output_format="jpeg", seed=-1, webhook_url="", webhook_secret="", config=None):
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
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        return super().generate_image("flux-pro-1.0-fill", arguments, config)


class FluxKontextPro(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "input_image": ("STRING", {"default": None}),
                "aspect_ratio": (["none", "21:9", "16:9", "3:2", "4:3", "1:1", "3:4", "2:3", "9:16", "9:21"], {"default": "none"}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "png"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "input_image_2": ("STRING", {"default": ""}),
                "input_image_3": ("STRING", {"default": ""}),
                "input_image_4": ("STRING", {"default": ""}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, input_image, aspect_ratio, prompt_upsampling, safety_tolerance, output_format,
                       seed=-1, input_image_2="", input_image_3="", input_image_4="",
                       webhook_url="", webhook_secret="", config=None):
        arguments = {
            "prompt": prompt,
            "input_image": input_image,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        if aspect_ratio != "none":
            arguments["aspect_ratio"] = aspect_ratio
        if seed != -1:
            arguments["seed"] = seed
        if input_image_2:
            arguments["input_image_2"] = input_image_2
        if input_image_3:
            arguments["input_image_3"] = input_image_3
        if input_image_4:
            arguments["input_image_4"] = input_image_4
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        return super().generate_image("flux-kontext-pro", arguments, config)


class FluxKontextMax(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "input_image": ("STRING", {"default": None}),
                "aspect_ratio": (["none", "21:9", "16:9", "3:2", "4:3", "1:1", "3:4", "2:3", "9:16", "9:21"], {"default": "none"}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "png"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "input_image_2": ("STRING", {"default": ""}),
                "input_image_3": ("STRING", {"default": ""}),
                "input_image_4": ("STRING", {"default": ""}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, input_image, aspect_ratio, prompt_upsampling, safety_tolerance, output_format,
                       seed=-1, input_image_2="", input_image_3="", input_image_4="",
                       webhook_url="", webhook_secret="", config=None):
        arguments = {
            "prompt": prompt,
            "input_image": input_image,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        if aspect_ratio != "none":
            arguments["aspect_ratio"] = aspect_ratio
        if seed != -1:
            arguments["seed"] = seed
        if input_image_2:
            arguments["input_image_2"] = input_image_2
        if input_image_3:
            arguments["input_image_3"] = input_image_3
        if input_image_4:
            arguments["input_image_4"] = input_image_4
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        return super().generate_image("flux-kontext-max", arguments, config)


class FluxProExpand(BaseFlux):
    CATEGORY = "BFL"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("STRING", {"default": ""}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "top": ("INT", {"default": 0, "min": 0, "max": 2048}),
                "bottom": ("INT", {"default": 0, "min": 0, "max": 2048}),
                "left": ("INT", {"default": 0, "min": 0, "max": 2048}),
                "right": ("INT", {"default": 0, "min": 0, "max": 2048}),
                "steps": ("INT", {"default": 50, "min": 15, "max": 50}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "guidance": ("FLOAT", {"default": 60.0, "min": 1.5, "max": 100.0}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, image, prompt, top, bottom, left, right, steps, prompt_upsampling, guidance,
                       safety_tolerance, output_format, seed=-1, webhook_url="", webhook_secret="", config=None):
        arguments = {
            "image": image,
            "prompt": prompt,
            "top": top,
            "bottom": bottom,
            "left": left,
            "right": right,
            "steps": steps,
            "prompt_upsampling": prompt_upsampling,
            "guidance": guidance,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        return super().generate_image("flux-pro-1.0-expand", arguments, config)


class Flux2Max(BaseFlux):
    CATEGORY = "BFL/Flux2"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 5}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "input_image": ("STRING", {"default": ""}),
                "input_image_2": ("STRING", {"default": ""}),
                "input_image_3": ("STRING", {"default": ""}),
                "input_image_4": ("STRING", {"default": ""}),
                "input_image_5": ("STRING", {"default": ""}),
                "input_image_6": ("STRING", {"default": ""}),
                "input_image_7": ("STRING", {"default": ""}),
                "input_image_8": ("STRING", {"default": ""}),
                "width": ("INT", {"default": 0, "min": 64}),
                "height": ("INT", {"default": 0, "min": 64}),
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, safety_tolerance, output_format,
                       input_image="", input_image_2="", input_image_3="", input_image_4="",
                       input_image_5="", input_image_6="", input_image_7="", input_image_8="",
                       width=0, height=0, seed=-1, webhook_url="", webhook_secret="", config=None):
        arguments = {
            "prompt": prompt,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        for key, val in [
            ("input_image", input_image), ("input_image_2", input_image_2),
            ("input_image_3", input_image_3), ("input_image_4", input_image_4),
            ("input_image_5", input_image_5), ("input_image_6", input_image_6),
            ("input_image_7", input_image_7), ("input_image_8", input_image_8)
        ]:
            if val:
                arguments[key] = val
        if width > 0:
            arguments["width"] = width
        if height > 0:
            arguments["height"] = height
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        try:
            task_id = self.post_request("flux-2-max", arguments, config)
            if task_id:
                print(f"Task ID '{task_id}'")
                return self.get_result(task_id, output_format=output_format, config_override=config)
            return self.create_blank_image()
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return self.create_blank_image()


class Flux2Pro(BaseFlux):
    CATEGORY = "BFL/Flux2"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 5}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "input_image": ("STRING", {"default": ""}),
                "input_image_2": ("STRING", {"default": ""}),
                "input_image_3": ("STRING", {"default": ""}),
                "input_image_4": ("STRING", {"default": ""}),
                "input_image_5": ("STRING", {"default": ""}),
                "input_image_6": ("STRING", {"default": ""}),
                "input_image_7": ("STRING", {"default": ""}),
                "input_image_8": ("STRING", {"default": ""}),
                "width": ("INT", {"default": 0, "min": 64}),
                "height": ("INT", {"default": 0, "min": 64}),
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, safety_tolerance, output_format,
                       input_image="", input_image_2="", input_image_3="", input_image_4="",
                       input_image_5="", input_image_6="", input_image_7="", input_image_8="",
                       width=0, height=0, seed=-1, webhook_url="", webhook_secret="", config=None):
        arguments = {
            "prompt": prompt,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        for key, val in [
            ("input_image", input_image), ("input_image_2", input_image_2),
            ("input_image_3", input_image_3), ("input_image_4", input_image_4),
            ("input_image_5", input_image_5), ("input_image_6", input_image_6),
            ("input_image_7", input_image_7), ("input_image_8", input_image_8)
        ]:
            if val:
                arguments[key] = val
        if width > 0:
            arguments["width"] = width
        if height > 0:
            arguments["height"] = height
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        try:
            task_id = self.post_request("flux-2-pro", arguments, config)
            if task_id:
                print(f"Task ID '{task_id}'")
                return self.get_result(task_id, output_format=output_format, config_override=config)
            return self.create_blank_image()
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return self.create_blank_image()


class Flux2Flex(BaseFlux):
    CATEGORY = "BFL/Flux2"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "guidance": ("FLOAT", {"default": 4.5, "min": 1.5, "max": 10.0}),
                "steps": ("INT", {"default": 50, "min": 1, "max": 50}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 5}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "input_image": ("STRING", {"default": ""}),
                "input_image_2": ("STRING", {"default": ""}),
                "input_image_3": ("STRING", {"default": ""}),
                "input_image_4": ("STRING", {"default": ""}),
                "input_image_5": ("STRING", {"default": ""}),
                "input_image_6": ("STRING", {"default": ""}),
                "input_image_7": ("STRING", {"default": ""}),
                "input_image_8": ("STRING", {"default": ""}),
                "width": ("INT", {"default": 0, "min": 64}),
                "height": ("INT", {"default": 0, "min": 64}),
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, guidance, steps, safety_tolerance, output_format,
                       input_image="", input_image_2="", input_image_3="", input_image_4="",
                       input_image_5="", input_image_6="", input_image_7="", input_image_8="",
                       width=0, height=0, seed=-1, webhook_url="", webhook_secret="", config=None):
        arguments = {
            "prompt": prompt,
            "guidance": guidance,
            "steps": steps,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        for key, val in [
            ("input_image", input_image), ("input_image_2", input_image_2),
            ("input_image_3", input_image_3), ("input_image_4", input_image_4),
            ("input_image_5", input_image_5), ("input_image_6", input_image_6),
            ("input_image_7", input_image_7), ("input_image_8", input_image_8)
        ]:
            if val:
                arguments[key] = val
        if width > 0:
            arguments["width"] = width
        if height > 0:
            arguments["height"] = height
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        try:
            task_id = self.post_request("flux-2-flex", arguments, config)
            if task_id:
                print(f"Task ID '{task_id}'")
                return self.get_result(task_id, output_format=output_format, config_override=config)
            return self.create_blank_image()
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return self.create_blank_image()


class Flux2Klein9b(BaseFlux):
    CATEGORY = "BFL/Flux2"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 5}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "input_image": ("STRING", {"default": ""}),
                "input_image_2": ("STRING", {"default": ""}),
                "input_image_3": ("STRING", {"default": ""}),
                "input_image_4": ("STRING", {"default": ""}),
                "width": ("INT", {"default": 0, "min": 64}),
                "height": ("INT", {"default": 0, "min": 64}),
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, safety_tolerance, output_format,
                       input_image="", input_image_2="", input_image_3="", input_image_4="",
                       width=0, height=0, seed=-1, webhook_url="", webhook_secret="", config=None):
        arguments = {
            "prompt": prompt,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        for key, val in [
            ("input_image", input_image), ("input_image_2", input_image_2),
            ("input_image_3", input_image_3), ("input_image_4", input_image_4)
        ]:
            if val:
                arguments[key] = val
        if width > 0:
            arguments["width"] = width
        if height > 0:
            arguments["height"] = height
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        try:
            task_id = self.post_request("flux-2-klein-9b", arguments, config)
            if task_id:
                print(f"Task ID '{task_id}'")
                return self.get_result(task_id, output_format=output_format, config_override=config)
            return self.create_blank_image()
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return self.create_blank_image()


class Flux2Klein4b(BaseFlux):
    CATEGORY = "BFL/Flux2"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 5}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "input_image": ("STRING", {"default": ""}),
                "input_image_2": ("STRING", {"default": ""}),
                "input_image_3": ("STRING", {"default": ""}),
                "input_image_4": ("STRING", {"default": ""}),
                "width": ("INT", {"default": 0, "min": 64}),
                "height": ("INT", {"default": 0, "min": 64}),
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, prompt, safety_tolerance, output_format,
                       input_image="", input_image_2="", input_image_3="", input_image_4="",
                       width=0, height=0, seed=-1, webhook_url="", webhook_secret="", config=None):
        arguments = {
            "prompt": prompt,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        for key, val in [
            ("input_image", input_image), ("input_image_2", input_image_2),
            ("input_image_3", input_image_3), ("input_image_4", input_image_4)
        ]:
            if val:
                arguments[key] = val
        if width > 0:
            arguments["width"] = width
        if height > 0:
            arguments["height"] = height
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
        try:
            task_id = self.post_request("flux-2-klein-4b", arguments, config)
            if task_id:
                print(f"Task ID '{task_id}'")
                return self.get_result(task_id, output_format=output_format, config_override=config)
            return self.create_blank_image()
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return self.create_blank_image()


class FluxCredits:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_credits"
    CATEGORY = "BFL/Utility"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {"optional": {"config": ("BFL_CONFIG",)}}

    def get_credits(self, config=None):
        config_loader_instance = get_config_loader(config)
        headers = {"x-key": config_loader_instance.get_x_key()}
        url = config_loader_instance.create_url("credits")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = json.dumps(response.json(), indent=2)
        else:
            result = f"Error {response.status_code}: {response.text}"
        return {"ui": {"text": (result,)}, "result": (result,)}


NODE_CLASS_MAPPINGS = {
    "FluxPro11_BFL": FluxPro11,
    "FluxDev_BFL": FluxDev,
    "FluxPro11Ultra_BFL": FluxPro11Ultra,
    "FluxProFill_BFL": FluxProFill,
    "FluxKontextPro_BFL": FluxKontextPro,
    "FluxKontextMax_BFL": FluxKontextMax,
    "FluxProExpand_BFL": FluxProExpand,
    "Flux2Max_BFL": Flux2Max,
    "Flux2Pro_BFL": Flux2Pro,
    "Flux2Flex_BFL": Flux2Flex,
    "Flux2Klein9b_BFL": Flux2Klein9b,
    "Flux2Klein4b_BFL": Flux2Klein4b,
    "FluxCredits_BFL": FluxCredits
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxPro11_BFL": "Flux Pro 1.1 (BFL)",
    "FluxDev_BFL": "Flux Dev (BFL)",
    "FluxPro11Ultra_BFL": "Flux Pro 1.1 Ultra (BFL)",
    "FluxProFill_BFL": "Flux Pro Fill (BFL)",
    "FluxKontextPro_BFL": "Flux Kontext Pro (BFL)",
    "FluxKontextMax_BFL": "Flux Kontext Max (BFL)",
    "FluxProExpand_BFL": "Flux Pro Expand (BFL)",
    "Flux2Max_BFL": "Flux 2 Max (BFL)",
    "Flux2Pro_BFL": "Flux 2 Pro (BFL)",
    "Flux2Flex_BFL": "Flux 2 Flex (BFL)",
    "Flux2Klein9b_BFL": "Flux 2 Klein 9B (BFL)",
    "Flux2Klein4b_BFL": "Flux 2 Klein 4B (BFL)",
    "FluxCredits_BFL": "Flux Credits (BFL)"
}
