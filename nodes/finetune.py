import requests
import os
import json
import base64
from .base import BaseFinetuneFlux
from .config import config_loader
from .config_node import get_config_loader

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
            
            if response.status_code == 200:
                result = response.json()
                finetune_id = result.get("id", "Unknown")
                print(f"✅ Finetune created successfully with ID: {finetune_id}")
                print(f"⚠️  Remember: Use the same region ({region}) for inference!")
                
                return (json.dumps(result, indent=2),)
            else:
                print(f"❌ Error creating finetune: {response.status_code}")
                try:
                    error_response = response.json()
                    return (json.dumps(error_response, indent=2),)
                except:
                    return (f"HTTP {response.status_code}: {response.text}",)
        except Exception as e:
            print(f"❌ Error creating finetune: {str(e)}")
            error_response = {"error": "Exception occurred", "message": str(e)}
            return (json.dumps(error_response, indent=2),)

class FluxFinetuneStatus:
    RETURN_TYPES = ("STRING",)
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
            error_response = {"error": "No finetune ID provided"}
            return (json.dumps(error_response, indent=2),)
            
        try:
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
                
                return (json.dumps(result, indent=2),)
            else:
                print(f"❌ Error checking finetune status: {response.status_code}")
                print(f"Response: {response.text}")
                try:
                    error_response = response.json()
                    return (json.dumps(error_response, indent=2),)
                except:
                    return (f"HTTP {response.status_code}: {response.text}",)
                
        except Exception as e:
            print(f"❌ Exception checking finetune status: {str(e)}")
            error_response = {"error": "Exception occurred", "message": str(e)}
            return (json.dumps(error_response, indent=2),)

class FluxMyFinetunes:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_my_finetunes"
    CATEGORY = "BFL/Finetune"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "region": (["us", "eu"], {"default": "us"})
            }
        }

    def get_my_finetunes(self, region):
        try:
            my_finetunes_url = config_loader.create_url("my_finetunes", region=region)
            
            headers = {"x-key": os.environ["X_KEY"]}
            
            print(f"📋 Getting my finetunes from region: {region}")
            print(f"📡 Using endpoint: {my_finetunes_url}")
            
            response = requests.get(my_finetunes_url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Found {len(result) if isinstance(result, list) else 'N/A'} finetunes")
                return (json.dumps(result, indent=2),)
            else:
                print(f"❌ Error getting finetunes: {response.status_code}")
                try:
                    error_response = response.json()
                    return (json.dumps(error_response, indent=2),)
                except:
                    return (f"HTTP {response.status_code}: {response.text}",)
                
        except Exception as e:
            print(f"❌ Exception getting finetunes: {str(e)}")
            return (f"Error: {str(e)}",)

class FluxFinetuneDetails:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "get_finetune_details"
    CATEGORY = "BFL/Finetune"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": ""}),
                "region": (["us", "eu"], {"default": "us"})
            }
        }

    def get_finetune_details(self, finetune_id, region):
        if not finetune_id or not finetune_id.strip():
            return ("Error: Finetune ID is required",)
            
        try:
            details_url = config_loader.create_url("finetune_details", region=region)
            
            headers = {"x-key": os.environ["X_KEY"]}
            params = {"finetune_id": finetune_id.strip()}
            
            print(f"📋 Getting finetune details for ID: {finetune_id}")
            print(f"📡 Using endpoint: {details_url}")
            
            response = requests.get(details_url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Got finetune details successfully")
                return (json.dumps(result, indent=2),)
            else:
                print(f"❌ Error getting finetune details: {response.status_code}")
                try:
                    error_response = response.json()
                    return (json.dumps(error_response, indent=2),)
                except:
                    return (f"HTTP {response.status_code}: {response.text}",)
                
        except Exception as e:
            print(f"❌ Exception getting finetune details: {str(e)}")
            return (f"Error: {str(e)}",)

class FluxDeleteFinetune:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "delete_finetune"
    CATEGORY = "BFL/Finetune"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": ""}),
                "region": (["us", "eu"], {"default": "us"})
            }
        }

    def delete_finetune(self, finetune_id, region):
        if not finetune_id or not finetune_id.strip():
            return ("Error: Finetune ID is required",)
            
        try:
            delete_url = config_loader.create_url("delete_finetune", region=region)
            
            headers = {
                "x-key": os.environ["X_KEY"],
                "Content-Type": "application/json"
            }
            payload = {"finetune_id": finetune_id.strip()}
            
            print(f"🗑️  Deleting finetune ID: {finetune_id}")
            print(f"📡 Using endpoint: {delete_url}")
            
            response = requests.post(delete_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Finetune deleted successfully")
                return (json.dumps(result, indent=2),)
            else:
                print(f"❌ Error deleting finetune: {response.status_code}")
                try:
                    error_response = response.json()
                    return (json.dumps(error_response, indent=2),)
                except:
                    return (f"HTTP {response.status_code}: {response.text}",)
                
        except Exception as e:
            print(f"❌ Exception deleting finetune: {str(e)}")
            return (f"Error: {str(e)}",)

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
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, finetune_id, region, prompt, finetune_strength, steps, guidance, width, height, 
                      prompt_upsampling, safety_tolerance, output_format, image_prompt="", seed=-1, 
                      webhook_url="", webhook_secret="", config=None):
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
            
        return self.generate_regional_image("flux-pro-finetuned", arguments, region, config)
    
    def generate_regional_image(self, endpoint, arguments, region, config_override=None):
        if "width" in arguments and "height" in arguments:
            self.check_multiple_of_32(arguments["width"], arguments["height"])

        try:
            # Use ConfigLoader with optional config override
            config_loader_instance = get_config_loader(config_override)
            config_loader_instance.set_x_key()  # Ensure X_KEY is set in environment
            
            post_url = config_loader_instance.create_url(endpoint, region=region)
            headers = {"x-key": config_loader_instance.get_x_key()}
            response = requests.post(post_url, json=arguments, headers=headers)
            
            if response.status_code == 200:
                task_id = response.json().get("id")
                if task_id:
                    regional_endpoint = config_loader_instance.get_regional_endpoint(region)
                    print(f"Finetune Task ID '{task_id}' (Region: {region.upper()} - {regional_endpoint})")
                    return self.get_result(task_id, output_format=arguments.get("output_format", "jpeg"), config_override=config_override)
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
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, finetune_id, prompt, control_image, finetune_strength, prompt_upsampling, 
                      steps, output_format, guidance, safety_tolerance, seed=-1, webhook_url="", webhook_secret="", config=None):
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
            
        return super().generate_image("flux-pro-1.0-depth-finetuned", arguments, config)

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
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, finetune_id, prompt, control_image, finetune_strength, canny_low_threshold, 
                      canny_high_threshold, prompt_upsampling, steps, output_format, guidance, safety_tolerance, 
                      seed=-1, webhook_url="", webhook_secret="", config=None):
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
            
        return super().generate_image("flux-pro-1.0-canny-finetuned", arguments, config)

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
                      safety_tolerance, output_format, mask="", prompt="", seed=-1, webhook_url="", webhook_secret="", config=None):
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
            
        return super().generate_image("flux-pro-1.0-fill-finetuned", arguments, config)

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
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, finetune_id, region, prompt, finetune_strength, aspect_ratio, safety_tolerance, 
                      output_format, raw, seed=-1, webhook_url="", webhook_secret="", config=None):
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
            
        return self.generate_regional_image("flux-pro-1.1-ultra-finetuned", arguments, region, config)
    
    def generate_regional_image(self, endpoint, arguments, region, config_override=None):
        try:
            # Use ConfigLoader with optional config override
            config_loader_instance = get_config_loader(config_override)
            config_loader_instance.set_x_key()  # Ensure X_KEY is set in environment
            
            post_url = config_loader_instance.create_url(endpoint, region=region)
            headers = {"x-key": config_loader_instance.get_x_key()}
            response = requests.post(post_url, json=arguments, headers=headers)
            
            if response.status_code == 200:
                task_id = response.json().get("id")
                if task_id:
                    regional_endpoint = config_loader_instance.get_regional_endpoint(region)
                    print(f"Finetune Task ID '{task_id}' (Region: {region.upper()} - {regional_endpoint})")
                    return self.get_result(task_id, output_format=arguments.get("output_format", "jpeg"), config_override=config_override)
            else:
                print(f"Error initiating regional finetune request: {response.status_code}, {response.text}")
                return self.create_blank_image()
        except Exception as e:
            print(f"Error generating regional finetune image: {str(e)}")
            return self.create_blank_image()

NODE_CLASS_MAPPINGS = {
    "FluxFinetune_BFL": FluxFinetune,
    "FluxFinetuneStatus_BFL": FluxFinetuneStatus,
    "FluxMyFinetunes_BFL": FluxMyFinetunes,
    "FluxFinetuneDetails_BFL": FluxFinetuneDetails,
    "FluxDeleteFinetune_BFL": FluxDeleteFinetune,
    "FluxProFinetune_BFL": FluxProFinetune,
    "FluxProDepthFinetune_BFL": FluxProDepthFinetune,
    "FluxProCannyFinetune_BFL": FluxProCannyFinetune,
    "FluxProFillFinetune_BFL": FluxProFillFinetune,
    "FluxPro11UltraFinetune_BFL": FluxPro11UltraFinetune
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxFinetune_BFL": "Flux Finetune Creator (BFL)",
    "FluxFinetuneStatus_BFL": "Flux Finetune Status (BFL)",
    "FluxMyFinetunes_BFL": "Flux My Finetunes (BFL)",
    "FluxFinetuneDetails_BFL": "Flux Finetune Details (BFL)",
    "FluxDeleteFinetune_BFL": "Flux Delete Finetune (BFL)",
    "FluxProFinetune_BFL": "Flux Pro Finetune (BFL)",
    "FluxProDepthFinetune_BFL": "Flux Pro Depth Finetune (BFL)",
    "FluxProCannyFinetune_BFL": "Flux Pro Canny Finetune (BFL)",
    "FluxProFillFinetune_BFL": "Flux Pro Fill Finetune (BFL)",
    "FluxPro11UltraFinetune_BFL": "Flux Pro 1.1 Ultra Finetune (BFL)"
} 