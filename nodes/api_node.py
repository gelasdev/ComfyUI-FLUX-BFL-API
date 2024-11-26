import requests
from PIL import Image
import io
import numpy as np
import torch
import os
import configparser
import time
from enum import Enum
from urllib.parse import urljoin

class Status(Enum):
    TASK_NOT_FOUND = "Task not found"
    PENDING = "Pending"
    REQUEST_MODERATED = "Request Moderated"
    CONTENT_MODERATED = "Content Moderated"
    READY = "Ready"
    ERROR = "Error"

class ConfigLoader:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        config_path = os.path.join(parent_dir, "config.ini")
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.set_x_key()

    def get_key(self, section, key):
        try:
            return self.config[section][key]
        except KeyError:
            raise KeyError(f"{key} not found in section {section} of config file.")

    def create_url(self, path):
        try:
            base_url = self.get_key('API', 'BASE_URL')
            return urljoin(base_url, path)
        except KeyError as e:
            raise KeyError(f"Error constructing URL: {str(e)}")

    def set_x_key(self):
        try:
            x_key = self.get_key('API', 'X_KEY')
            os.environ["X_KEY"] = x_key
        except KeyError as e:
            print(f"Error: {str(e)}")


config_loader = ConfigLoader()

class BaseFlux:
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"
    CATEGORY = "BFL"

    def process_result(self, result, output_format="jpeg"):
        try:
            sample_url = result['result']['sample']
            img_response = requests.get(sample_url)
            img = Image.open(io.BytesIO(img_response.content))
            
            with io.BytesIO() as output:
                img.save(output, format=output_format.upper())
                output.seek(0)
                img_converted = Image.open(output)

                img_array = np.array(img_converted).astype(np.float32) / 255.0
                img_tensor = torch.from_numpy(img_array)[None,]
                return (img_tensor,)
        except KeyError as e:
            print(f"KeyError: Missing expected key {e}")
            return self.create_blank_image()
        except Exception as e:
            print(f"Error processing image result: {str(e)}")
            return self.create_blank_image()

    def create_blank_image(self):
        blank_img = Image.new('RGB', (512, 512), color='black')
        img_array = np.array(blank_img).astype(np.float32) / 255.0
        img_tensor = torch.from_numpy(img_array)[None,]
        return (img_tensor,)

    def check_multiple_of_32(self, width, height):
        if width % 32 != 0 or height % 32 != 0:
            raise ValueError(f"Width {width} and height {height} must be multiples of 32.")

    def post_request(self, url_path, arguments):
        post_url = config_loader.create_url(url_path)
        headers = {"x-key": os.environ["X_KEY"]}
        response = requests.post(post_url, json=arguments, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("id")
        else:
            print(f"Error initiating request: {response.status_code}, {response.text}")
            return None

    def get_result(self, task_id, output_format="jpeg", attempt=1, max_attempts=20):
        if attempt > max_attempts:
            print(f"Max attempts reached for task_id {task_id}. Image not ready.")
            return self.create_blank_image()
        
        get_url = config_loader.create_url(f"get_result?id={task_id}")
        headers = {"x-key": os.environ["X_KEY"]}
        result_response = requests.get(get_url, headers=headers)

        if result_response.status_code == 200:
            try:
                result = result_response.json()
                status = result.get("status")
                if Status(status) == Status.READY:
                    return self.process_result(result, output_format=output_format)
                elif Status(status) == Status.PENDING:
                    print(f"Attempt {attempt}: Image not ready, status is '{status}'. Retrying in 5 seconds...")
                    time.sleep(5)
                    return self.get_result(task_id, output_format, attempt + 1, max_attempts)
                else:
                    print(f"Error: Unexpected status '{status}'")
                    return self.create_blank_image()
            except ValueError as e:
                print(f"Error parsing JSON response: {str(e)}")
                print(f"Response content: {result_response.text}")
                return self.create_blank_image()
        else:
            print(f"Error fetching result: {result_response.status_code}, {result_response.text}")
            return self.create_blank_image()

    def generate_image(self, url_path, arguments):
        if "width" in arguments and "height" in arguments:
            self.check_multiple_of_32(arguments["width"], arguments["height"])

        try:
            task_id = self.post_request(url_path, arguments)
            if task_id:
                print(f"Task ID '{task_id}'")
                return self.get_result(task_id, output_format=arguments.get("output_format", "jpeg"))
            return self.create_blank_image()
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return self.create_blank_image()


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
                "seed": ("INT", {"default": -1})
            }
        }

    def generate_image(self, prompt, width, height, prompt_upsampling, safety_tolerance, output_format, seed):
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
        return super().generate_image("flux-pro-1.1", arguments)


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
                "seed": ("INT", {"default": -1})
            }
        }

    def generate_image(self, prompt, width, height, steps, prompt_upsampling, safety_tolerance, guidance, output_format, seed):
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
        return super().generate_image("flux-dev", arguments)


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
                "seed": ("INT", {"default": -1})
            }
        }

    def generate_image(self, prompt, width, height, steps, prompt_upsampling, safety_tolerance, guidance, interval, output_format, seed):
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
        return super().generate_image("flux-pro", arguments)


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
                "seed": ("INT", {"default": -1})
            }
        }

    def generate_image(self, prompt, aspect_ratio, safety_tolerance, output_format, raw, seed):
        arguments = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
            "raw": raw
        }
        if seed != -1:
            arguments["seed"] = seed
        return super().generate_image("flux-pro-1.1-ultra", arguments)

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
                "seed": ("INT", {"default": -1})
            }
        }

    def generate_image(self, image, mask=None, prompt=None, steps=50, prompt_upsampling=False, guidance=60.0,
                      safety_tolerance=2, output_format="jpeg", seed=-1):
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

        return super().generate_image("flux-pro-1.0-fill", arguments)

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
                "seed": ("INT", {"default": -1})
            }
        }

    def generate_image(self, prompt, control_image, prompt_upsampling, steps, guidance, safety_tolerance, output_format, seed):
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
        return super().generate_image("flux-pro-1.0-canny", arguments)


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
                "seed": ("INT", {"default": -1})
            }
        }

    def generate_image(self, prompt, control_image, prompt_upsampling, steps, guidance, safety_tolerance, output_format, seed):
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
        return super().generate_image("flux-pro-1.0-depth", arguments)

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
                "seed": ("INT", {"default": -1})
            }
        }

    def generate_image(self, prompt, image_prompt, width, height, prompt_upsampling, safety_tolerance, output_format, seed):
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
        return super().generate_image("flux-pro-1.1", arguments)

NODE_CLASS_MAPPINGS = {
    "FluxPro11_BFL": FluxPro11,
    "FluxDev_BFL": FluxDev,
    "FluxPro_BFL": FluxPro,
    "FluxPro11Ultra_BFL": FluxPro11Ultra,
    "FluxPro11Redux_BFL": FluxPro11Redux,
    "FluxProFill_BFL": FluxProFill,
    "FluxProCanny_BFL": FluxProCanny,
    "FluxProDepth_BFL": FluxProDepth
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxPro11_BFL": "Flux Pro 1.1 (BFL)",
    "FluxDev_BFL": "Flux Dev (BFL)",
    "FluxPro_BFL": "Flux Pro (BFL)",
    "FluxPro11Ultra_BFL": "Flux Pro 1.1 Ultra (BFL)",
    "FluxPro11Redux_BFL": "Flux Pro 1.1 Redux (BFL)",
    "FluxProFill_BFL": "Flux Pro Fill (BFL)",
    "FluxProCanny_BFL": "Flux Pro Canny (BFL)",
    "FluxProDepth_BFL": "Flux Pro Depth (BFL)"
}
