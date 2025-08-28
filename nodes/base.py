import requests
from PIL import Image
import io
import numpy as np
import torch
import os
import time
from .status import Status
from .config import config_loader
from .config_node import get_config_loader

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

    def post_request(self, url_path, arguments, config_override=None):
        # Use ConfigLoader with optional config override
        config_loader_instance = get_config_loader(config_override)
        config_loader_instance.set_x_key()  # Ensure X_KEY is set in environment
        
        post_url = config_loader_instance.create_url(url_path)
        headers = {"x-key": config_loader_instance.get_x_key()}
        response = requests.post(post_url, json=arguments, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("id")
        else:
            print(f"Error initiating request: {response.status_code}, {response.text}")
            return None

    def get_result(self, task_id, output_format="jpeg", max_attempts=20, config_override=None):
        # Use ConfigLoader with optional config override
        config_loader_instance = get_config_loader(config_override)
        
        headers = {"x-key": config_loader_instance.get_x_key()}
        get_url = config_loader_instance.create_url(f"get_result?id={task_id}")
        attempt = 1
        
        while attempt <= max_attempts:
            try:
                result_response = requests.get(get_url, headers=headers)
                
                if result_response.status_code != 200:
                    print(f"HTTP Error on attempt {attempt}/{max_attempts}: {result_response.status_code}, {result_response.text}")
                    attempt += 1
                    if attempt <= max_attempts:
                        time.sleep(5)
                    continue
                
                result = result_response.json()
                status = result.get("status")
                
                if Status(status) == Status.READY:
                    return self.process_result(result, output_format=output_format)
                elif Status(status) == Status.PENDING:
                    print(f"Attempt {attempt}/{max_attempts}: Image not ready, status is '{status}'. Retrying in 5 seconds...")
                    attempt += 1
                    if attempt <= max_attempts:
                        time.sleep(5)
                elif Status(status) in [Status.ERROR, Status.CONTENT_MODERATED, Status.REQUEST_MODERATED]:
                    print(f"Terminal status '{status}' - stopping retries")
                    break
                else:
                    print(f"Unknown status '{status}' on attempt {attempt}/{max_attempts}")
                    attempt += 1
                    if attempt <= max_attempts:
                        time.sleep(5)
                    
            except ValueError as e:
                print(f"JSON parsing error on attempt {attempt}/{max_attempts}: {str(e)}")
                attempt += 1
                if attempt <= max_attempts:
                    time.sleep(5)
            except Exception as e:
                print(f"Unexpected error on attempt {attempt}/{max_attempts}: {str(e)}")
                attempt += 1
                if attempt <= max_attempts:
                    time.sleep(5)
        
        print(f"All attempts exhausted for task_id {task_id}. Returning blank image.")
        return self.create_blank_image()

    def generate_image(self, url_path, arguments, config_override=None):
        if "width" in arguments and "height" in arguments:
            self.check_multiple_of_32(arguments["width"], arguments["height"])

        try:
            task_id = self.post_request(url_path, arguments, config_override)
            if task_id:
                print(f"Task ID '{task_id}'")
                return self.get_result(task_id, output_format=arguments.get("output_format", "jpeg"), config_override=config_override)
            return self.create_blank_image()
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return self.create_blank_image()

class BaseFinetuneFlux(BaseFlux):
    CATEGORY = "BFL/Finetune" 