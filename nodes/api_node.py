import requests
from PIL import Image
import io
import numpy as np
import torch
import os
import configparser
import time
from urllib.parse import urljoin

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

    def process_result(self, result):
        try:
            sample_url = result['result']['sample']
            img_response = requests.get(sample_url)
            img = Image.open(io.BytesIO(img_response.content))
            img_array = np.array(img).astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_array)[None,]
            img.show()
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

    def get_result(self, task_id):
        get_url = config_loader.create_url(f"get_result?id={task_id}")
        headers = {"x-key": os.environ["X_KEY"]}
        result_response = requests.get(get_url, headers=headers)

        if result_response.status_code == 200:
            try:
                result = result_response.json()
                if result and "result" in result and "sample" in result["result"]:
                    return self.process_result(result)
                else:
                    print(f"Error: Unexpected response structure: {result}")
                    return self.create_blank_image()
            except ValueError as e:
                print(f"Error parsing JSON response: {str(e)}")
                print(f"Response content: {result_response.text}")
                return self.create_blank_image()
        else:
            print(f"Error fetching result: {result_response.status_code}, {result_response.text}")
            return self.create_blank_image()

    def generate_image(self, url_path, arguments):
        self.check_multiple_of_32(arguments["width"], arguments["height"])

        try:
            task_id = self.post_request(url_path, arguments)
            if task_id:
                time.sleep(5)
                return self.get_result(task_id)
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
                "prompt_upsampling": ("BOOLEAN", {"default": True}),
                "steps": ("INT", {"default": 2, "min": 1, "max": 100}),
                "safety_tolerance": (["1", "2", "3", "4", "5", "6"], {"default": "2"}),
            },
            "optional": {
                "seed": ("INT", {"default": -1})
            }
        }

    def generate_image(self, prompt, width, height, prompt_upsampling, steps, safety_tolerance, seed=-1):
        arguments = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "prompt_upsampling": prompt_upsampling,
            "steps": steps,
            "safety_tolerance": safety_tolerance
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
                "steps": ("INT", {"default": 28, "min": 1, "max": 100}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": (["1", "2", "3", "4", "5", "6"], {"default": "2"}),
                "guidance": ("INT", {"default": 3, "min": 1, "max": 10}),
            },
            "optional": {
                "seed": ("INT", {"default": 42})
            }
        }

    def generate_image(self, prompt, width, height, steps, prompt_upsampling, safety_tolerance, guidance, seed=42):
        arguments = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "guidance": guidance,
            "seed": seed
        }
        return super().generate_image("flux-dev", arguments)


class FluxPro(BaseFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "width": ("INT", {"default": 1024, "min": 256, "max": 1440}),
                "height": ("INT", {"default": 768, "min": 256, "max": 1440}),
                "steps": ("INT", {"default": 40, "min": 1, "max": 100}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": (["1", "2", "3", "4", "5", "6"], {"default": "2"}),
                "guidance": ("FLOAT", {"default": 2.5, "min": 0.1, "max": 10}),
                "interval": ("INT", {"default": 2}),
            },
            "optional": {
                "seed": ("INT", {"default": 42})
            }
        }

    def generate_image(self, prompt, width, height, steps, prompt_upsampling, safety_tolerance, guidance, interval, seed=42):
        arguments = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "guidance": guidance,
            "interval": interval,
            "seed": seed
        }
        return super().generate_image("flux-pro", arguments)


NODE_CLASS_MAPPINGS = {
    "FluxPro11_BFL": FluxPro11,
    "FluxDev_BFL": FluxDev,
    "FluxPro_BFL": FluxPro
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxPro11_BFL": "Flux Pro 1.1 (BFL)",
    "FluxDev_BFL": "Flux Dev (BFL)",
    "FluxPro_BFL": "Flux Pro (BFL)"
}
