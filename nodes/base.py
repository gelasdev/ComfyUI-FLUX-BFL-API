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

REQUEST_TIMEOUT = 300  # seconds for connect + read

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

        session = requests.Session()
        prepared = session.prepare_request(requests.Request("POST", post_url, json=arguments, headers=headers))
        body = prepared.body.decode() if isinstance(prepared.body, bytes) else prepared.body
        headers_str = " \\\n    ".join(f"-H '{k}: {v}'" for k, v in prepared.headers.items())
        print(f"[BFL] curl -X POST '{prepared.url}' \\\n    {headers_str} \\\n    -d '{body}'")

        response = session.send(prepared, timeout=REQUEST_TIMEOUT)
        print(f"[BFL] POST response: {response.status_code}")

        if response.status_code == 200:
            task_id = response.json().get("id")
            print(f"[BFL] Task ID: {task_id}")
            return task_id
        else:
            print(f"[BFL] Error initiating request: {response.status_code}, {response.text}")
            return None

    def get_result(self, task_id, output_format="jpeg", max_attempts=40, config_override=None):
        # Use ConfigLoader with optional config override
        config_loader_instance = get_config_loader(config_override)

        headers = {"x-key": config_loader_instance.get_x_key()}
        get_url = config_loader_instance.create_url(f"get_result?id={task_id}")
        attempt = 1
        start_time = time.time()
        print(f"[BFL] Polling task {task_id} (max {max_attempts} attempts, 5s interval)")

        while attempt <= max_attempts:
            elapsed = time.time() - start_time
            try:
                print(f"[BFL] Poll attempt {attempt}/{max_attempts} | elapsed {elapsed:.1f}s | GET {get_url}")
                result_response = requests.get(get_url, headers=headers, timeout=REQUEST_TIMEOUT)
                print(f"[BFL] Poll response: {result_response.status_code}")

                if result_response.status_code != 200:
                    print(f"[BFL] HTTP error on attempt {attempt}/{max_attempts}: {result_response.status_code}, {result_response.text}")
                    attempt += 1
                    if attempt <= max_attempts:
                        time.sleep(5)
                    continue

                result = result_response.json()
                status = result.get("status")
                print(f"[BFL] Status: {status}")

                if Status(status) == Status.READY:
                    print(f"[BFL] Task {task_id} ready after {elapsed:.1f}s — downloading image")
                    return self.process_result(result, output_format=output_format)
                elif Status(status) == Status.PENDING:
                    print(f"[BFL] Attempt {attempt}/{max_attempts}: pending — retrying in 5s")
                    attempt += 1
                    if attempt <= max_attempts:
                        time.sleep(5)
                elif Status(status) in [Status.ERROR, Status.CONTENT_MODERATED, Status.REQUEST_MODERATED]:
                    print(f"[BFL] Terminal status '{status}' — stopping retries")
                    break
                else:
                    print(f"[BFL] Unknown status '{status}' on attempt {attempt}/{max_attempts}")
                    attempt += 1
                    if attempt <= max_attempts:
                        time.sleep(5)

            except ValueError as e:
                print(f"[BFL] JSON parsing error on attempt {attempt}/{max_attempts}: {str(e)}")
                attempt += 1
                if attempt <= max_attempts:
                    time.sleep(5)
            except Exception as e:
                print(f"[BFL] Unexpected error on attempt {attempt}/{max_attempts}: {str(e)}")
                attempt += 1
                if attempt <= max_attempts:
                    time.sleep(5)

        elapsed = time.time() - start_time
        print(f"[BFL] All {max_attempts} attempts exhausted for task {task_id} after {elapsed:.1f}s — returning blank image.")
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
