import requests
import os
import json
import base64
from .base import BaseFinetuneFlux
from .config import config_loader

class FluxFinetune:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "create_finetune"
    CATEGORY = "BFL/Finetune"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "zip_file_path": ("STRING", {"default": ""}),
                "finetune_comment": ("STRING", {"default": "my-finetune"}),
                "trigger_word": ("STRING", {"default": "TOK"}),
                "mode": (["character", "product", "style", "general"], {"default": "general"}),
                "region": (["us", "eu"], {"default": "us"}),
                "iterations": ("INT", {"default": 300, "min": 100, "max": 2000}),
                "learning_rate": ("FLOAT", {"default": 0.00001, "min": 0.000001, "max": 0.01}),
                "captioning": ("BOOLEAN", {"default": True}),
                "priority": (["speed", "quality", "high_res_only"], {"default": "quality"}),
                "finetune_type": (["full", "lora"], {"default": "full"}),
                "lora_rank": ("INT", {"default": 32, "min": 8, "max": 128})
            },
            "optional": {
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""})
            }
        }

    def create_finetune(self, zip_file_path, finetune_comment, trigger_word, mode, region, iterations, learning_rate, 
                       captioning, priority, finetune_type, lora_rank, webhook_url="", webhook_secret=""):
        
        # Auto-adjust learning rate based on finetune_type if using default
        if learning_rate == 0.00001:  # Default value
            if finetune_type == "lora":
                learning_rate = 0.0001  # 10x higher for LoRA as per docs
                print(f"Auto-adjusted learning rate to {learning_rate} for LoRA finetune")
        
        # Read and encode ZIP file
        if not zip_file_path or not zip_file_path.strip():
            print("❌ Error: ZIP file path is required")
            return ("Error: ZIP file path is required",)
            
        try:
            print(f"📁 Reading ZIP file: {zip_file_path}")
            with open(zip_file_path.strip(), "rb") as f:
                file_data = base64.b64encode(f.read()).decode("utf-8")
                print(f"✅ ZIP file successfully encoded to base64 ({len(file_data)} characters)")
        except Exception as e:
            print(f"❌ Error reading ZIP file: {str(e)}")
            return ("Error: Could not read ZIP file",)
        
        arguments = {
            "file_data": file_data,
            "finetune_comment": finetune_comment,
            "trigger_word": trigger_word,
            "mode": mode,
            "iterations": iterations,
            "learning_rate": learning_rate,
            "captioning": captioning,
            "priority": priority,
            "finetune_type": finetune_type,
            "lora_rank": lora_rank
        }
        
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret

        try:
            post_url = config_loader.create_url("finetune", region=region)
            headers = {"x-key": os.environ["X_KEY"]}
            response = requests.post(post_url, json=arguments, headers=headers)
            
            # Log the full response details
            print("=" * 80)
            print("FINETUNE RESPONSE:")
            print("=" * 80)
            print(f"Status Code: {response.status_code}")
            print(f"Response Body:")
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
            except:
                print(f"Raw Response Text: {response.text}")
            print("=" * 80)
            
            if response.status_code == 200:
                result = response.json()
                finetune_id = result.get("id", "Unknown")
                regional_endpoint = config_loader.get_regional_endpoint(region)
                print(f"✅ Finetune created successfully with ID: {finetune_id}")
                print(f"Region: {region.upper()} ({regional_endpoint})")
                print(f"⚠️  Remember: Use the same region ({region}) for inference!")
                
                # Return the full response as JSON string for user
                return (json.dumps(result, indent=2),)
            else:
                print(f"❌ Error creating finetune: {response.status_code}")
                try:
                    error_response = response.json()
                    return (json.dumps(error_response, indent=2),)
                except:
                    return (f"HTTP {response.status_code}: {response.text}",)
        except Exception as e:
            print("=" * 80)
            print("FINETUNE EXCEPTION:")
            print("=" * 80)
            print(f"Exception Type: {type(e).__name__}")
            print(f"Exception Message: {str(e)}")
            import traceback
            print(f"Full Traceback:")
            traceback.print_exc()
            print("=" * 80)
            return ("Error",)

class FluxFinetuneStatus:
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("status", "progress", "result")
    FUNCTION = "check_finetune_status"
    CATEGORY = "BFL/Finetune"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": ""}),
                "region": (["us", "eu"], {"default": "us"})
            }
        }

    def check_finetune_status(self, finetune_id, region):
        if not finetune_id or not finetune_id.strip():
            return ("Error", "No finetune ID provided", "")
            
        try:
            # Use config_loader to get the correct regional endpoint
            polling_url = config_loader.create_url("get_result", region=region)
            
            headers = {"x-key": os.environ["X_KEY"]}
            params = {"id": finetune_id.strip()}
            
            print(f"🔍 Checking finetune status for ID: {finetune_id}")
            print(f"📡 Using endpoint: {polling_url}")
            
            response = requests.get(polling_url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "Unknown")
                progress = result.get("progress", "")
                result_data = result.get("result", "")
                
                print("=" * 50)
                print("FINETUNE STATUS:")
                print("=" * 50)
                print(f"Status: {status}")
                print(f"Progress: {progress}")
                if result_data:
                    print(f"Result: {result_data}")
                print("=" * 50)
                
                # Convert result to string if it's a dict
                if isinstance(result_data, dict):
                    result_str = json.dumps(result_data, indent=2)
                else:
                    result_str = str(result_data) if result_data else ""
                
                return (status, str(progress), result_str)
            else:
                print(f"❌ Error checking finetune status: {response.status_code}")
                print(f"Response: {response.text}")
                return ("Error", f"HTTP {response.status_code}", response.text)
                
        except Exception as e:
            print(f"❌ Exception checking finetune status: {str(e)}")
            return ("Error", "Exception occurred", str(e))

class FluxProFinetune(BaseFinetuneFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": "my-finetune"}),
                "region": (["us", "eu"], {"default": "us"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "finetune_strength": ("FLOAT", {"default": 1.2, "min": 0.0, "max": 2.0}),
                "steps": ("INT", {"default": 40, "min": 1, "max": 50}),
                "guidance": ("FLOAT", {"default": 2.5, "min": 1.5, "max": 5}),
                "width": ("INT", {"default": 1024, "min": 256, "max": 1440}),
                "height": ("INT", {"default": 768, "min": 256, "max": 1440}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "image_prompt": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""})
            }
        }

    def generate_image(self, finetune_id, region, prompt, finetune_strength, steps, guidance, width, height, 
                      prompt_upsampling, safety_tolerance, output_format, image_prompt="", seed=-1, 
                      webhook_url="", webhook_secret=""):
        arguments = {
            "finetune_id": finetune_id,
            "prompt": prompt,
            "finetune_strength": finetune_strength,
            "steps": steps,
            "guidance": guidance,
            "width": width,
            "height": height,
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        
        if image_prompt:
            arguments["image_prompt"] = image_prompt
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
            
        return self.generate_regional_image("flux-pro-finetuned", arguments, region)
    
    def generate_regional_image(self, endpoint, arguments, region):
        if "width" in arguments and "height" in arguments:
            self.check_multiple_of_32(arguments["width"], arguments["height"])

        try:
            post_url = config_loader.create_url(endpoint, region=region)
            headers = {"x-key": os.environ["X_KEY"]}
            response = requests.post(post_url, json=arguments, headers=headers)
            
            if response.status_code == 200:
                task_id = response.json().get("id")
                if task_id:
                    regional_endpoint = config_loader.get_regional_endpoint(region)
                    print(f"Finetune Task ID '{task_id}' (Region: {region.upper()} - {regional_endpoint})")
                    return self.get_result(task_id, output_format=arguments.get("output_format", "jpeg"))
            else:
                print(f"Error initiating regional finetune request: {response.status_code}, {response.text}")
                return self.create_blank_image()
        except Exception as e:
            print(f"Error generating regional finetune image: {str(e)}")
            return self.create_blank_image()

class FluxProDepthFinetune(BaseFinetuneFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": "my-finetune"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "control_image": ("STRING", {"default": None}),
                "finetune_strength": ("FLOAT", {"default": 1.1, "min": 0.1, "max": 2.0}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "steps": ("INT", {"default": 50, "min": 15, "max": 50}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "guidance": ("FLOAT", {"default": 15, "min": 1.5, "max": 100.0}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""})
            }
        }

    def generate_image(self, finetune_id, prompt, control_image, finetune_strength, prompt_upsampling, 
                      steps, output_format, guidance, safety_tolerance, seed=-1, webhook_url="", webhook_secret=""):
        arguments = {
            "finetune_id": finetune_id,
            "prompt": prompt,
            "control_image": control_image,
            "finetune_strength": finetune_strength,
            "prompt_upsampling": prompt_upsampling,
            "steps": steps,
            "output_format": output_format,
            "guidance": guidance,
            "safety_tolerance": safety_tolerance
        }
        
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
            
        return super().generate_image("flux-pro-1.0-depth-finetuned", arguments)

class FluxProCannyFinetune(BaseFinetuneFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": "my-finetune"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "control_image": ("STRING", {"default": None}),
                "finetune_strength": ("FLOAT", {"default": 1.1, "min": 0.1, "max": 2.0}),
                "canny_low_threshold": ("INT", {"default": 250, "min": 0, "max": 255}),
                "canny_high_threshold": ("INT", {"default": 250, "min": 0, "max": 255}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "steps": ("INT", {"default": 50, "min": 15, "max": 50}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "guidance": ("FLOAT", {"default": 30, "min": 1.5, "max": 100.0}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""})
            }
        }

    def generate_image(self, finetune_id, prompt, control_image, finetune_strength, canny_low_threshold, 
                      canny_high_threshold, prompt_upsampling, steps, output_format, guidance, safety_tolerance, 
                      seed=-1, webhook_url="", webhook_secret=""):
        arguments = {
            "finetune_id": finetune_id,
            "prompt": prompt,
            "control_image": control_image,
            "finetune_strength": finetune_strength,
            "canny_low_threshold": canny_low_threshold,
            "canny_high_threshold": canny_high_threshold,
            "prompt_upsampling": prompt_upsampling,
            "steps": steps,
            "output_format": output_format,
            "guidance": guidance,
            "safety_tolerance": safety_tolerance
        }
        
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
            
        return super().generate_image("flux-pro-1.0-canny-finetuned", arguments)

class FluxProFillFinetune(BaseFinetuneFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": "my-finetune"}),
                "image": ("STRING", {"default": None}),
                "finetune_strength": ("FLOAT", {"default": 1.1, "min": 0.1, "max": 2.0}),
                "steps": ("INT", {"default": 28, "min": 15, "max": 50}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "guidance": ("FLOAT", {"default": 60.0, "min": 1.5, "max": 100.0}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"})
            },
            "optional": {
                "mask": ("STRING", {"default": ""}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""})
            }
        }

    def generate_image(self, finetune_id, image, finetune_strength, steps, prompt_upsampling, guidance, 
                      safety_tolerance, output_format, mask="", prompt="", seed=-1, webhook_url="", webhook_secret=""):
        arguments = {
            "finetune_id": finetune_id,
            "image": image,
            "finetune_strength": finetune_strength,
            "steps": steps,
            "prompt_upsampling": prompt_upsampling,
            "guidance": guidance,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format
        }
        
        if mask:
            arguments["mask"] = mask
        if prompt:
            arguments["prompt"] = prompt
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
            
        return super().generate_image("flux-pro-1.0-fill-finetuned", arguments)

class FluxPro11UltraFinetune(BaseFinetuneFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": "my-finetune"}),
                "region": (["us", "eu"], {"default": "us"}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "finetune_strength": ("FLOAT", {"default": 1.2, "min": 0.0, "max": 2.0}),
                "aspect_ratio": (["16:9", "4:3", "1:1", "3:2", "21:9", "9:16", "3:4", "2:3", "9:21"], {"default": "16:9"}),
                "safety_tolerance": ("INT", {"default": 2, "min": 1, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "raw": ("BOOLEAN", {"default": False})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""})
            }
        }

    def generate_image(self, finetune_id, region, prompt, finetune_strength, aspect_ratio, safety_tolerance, 
                      output_format, raw, seed=-1, webhook_url="", webhook_secret=""):
        arguments = {
            "finetune_id": finetune_id,
            "prompt": prompt,
            "finetune_strength": finetune_strength,
            "aspect_ratio": aspect_ratio,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
            "raw": raw
        }
        
        if seed != -1:
            arguments["seed"] = seed
        if webhook_url:
            arguments["webhook_url"] = webhook_url
        if webhook_secret:
            arguments["webhook_secret"] = webhook_secret
            
        return self.generate_regional_image("flux-pro-1.1-ultra-finetuned", arguments, region)
    
    def generate_regional_image(self, endpoint, arguments, region):
        try:
            post_url = config_loader.create_url(endpoint, region=region)
            headers = {"x-key": os.environ["X_KEY"]}
            response = requests.post(post_url, json=arguments, headers=headers)
            
            if response.status_code == 200:
                task_id = response.json().get("id")
                if task_id:
                    regional_endpoint = config_loader.get_regional_endpoint(region)
                    print(f"Finetune Task ID '{task_id}' (Region: {region.upper()} - {regional_endpoint})")
                    return self.get_result(task_id, output_format=arguments.get("output_format", "jpeg"))
            else:
                print(f"Error initiating regional finetune request: {response.status_code}, {response.text}")
                return self.create_blank_image()
        except Exception as e:
            print(f"Error generating regional finetune image: {str(e)}")
            return self.create_blank_image()

NODE_CLASS_MAPPINGS = {
    "FluxFinetune_BFL": FluxFinetune,
    "FluxFinetuneStatus_BFL": FluxFinetuneStatus,
    "FluxProFinetune_BFL": FluxProFinetune,
    "FluxProDepthFinetune_BFL": FluxProDepthFinetune,
    "FluxProCannyFinetune_BFL": FluxProCannyFinetune,
    "FluxProFillFinetune_BFL": FluxProFillFinetune,
    "FluxPro11UltraFinetune_BFL": FluxPro11UltraFinetune
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxFinetune_BFL": "Flux Finetune Creator (BFL)",
    "FluxFinetuneStatus_BFL": "Flux Finetune Status (BFL)",
    "FluxProFinetune_BFL": "Flux Pro Finetune (BFL)",
    "FluxProDepthFinetune_BFL": "Flux Pro Depth Finetune (BFL)",
    "FluxProCannyFinetune_BFL": "Flux Pro Canny Finetune (BFL)",
    "FluxProFillFinetune_BFL": "Flux Pro Fill Finetune (BFL)",
    "FluxPro11UltraFinetune_BFL": "Flux Pro 1.1 Ultra Finetune (BFL)"
} 