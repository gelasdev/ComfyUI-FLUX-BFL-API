import requests
import json
from .base import BaseFinetuneFlux
from .config_node import get_config_loader


class FluxFinetuneStatus:
    RETURN_TYPES = ("STRING",)
    FUNCTION = "check_finetune_status"
    CATEGORY = "BFL/Finetune"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": ""})
            },
            "optional": {
                "config": ("BFL_CONFIG",)
            }
        }

    def check_finetune_status(self, finetune_id, config=None):
        if not finetune_id or not finetune_id.strip():
            error_response = {"error": "No finetune ID provided"}
            return (json.dumps(error_response, indent=2),)

        try:
            config_loader_instance = get_config_loader(config)
            config_loader_instance.set_x_key()
            polling_url = config_loader_instance.create_url("get_result")

            headers = {"x-key": config_loader_instance.get_x_key()}
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
            "required": {},
            "optional": {
                "config": ("BFL_CONFIG",)
            }
        }

    def get_my_finetunes(self, config=None):
        try:
            config_loader_instance = get_config_loader(config)
            config_loader_instance.set_x_key()
            my_finetunes_url = config_loader_instance.create_url("my_finetunes")

            headers = {"x-key": config_loader_instance.get_x_key()}

            print(f"📋 Getting my finetunes")
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
                "finetune_id": ("STRING", {"default": ""})
            },
            "optional": {
                "config": ("BFL_CONFIG",)
            }
        }

    def get_finetune_details(self, finetune_id, config=None):
        if not finetune_id or not finetune_id.strip():
            return ("Error: Finetune ID is required",)

        try:
            config_loader_instance = get_config_loader(config)
            config_loader_instance.set_x_key()
            details_url = config_loader_instance.create_url("finetune_details")

            headers = {"x-key": config_loader_instance.get_x_key()}
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
                "finetune_id": ("STRING", {"default": ""})
            },
            "optional": {
                "config": ("BFL_CONFIG",)
            }
        }

    def delete_finetune(self, finetune_id, config=None):
        if not finetune_id or not finetune_id.strip():
            return ("Error: Finetune ID is required",)

        try:
            config_loader_instance = get_config_loader(config)
            config_loader_instance.set_x_key()
            delete_url = config_loader_instance.create_url("delete_finetune")

            headers = {
                "x-key": config_loader_instance.get_x_key(),
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


class FluxProFillFinetune(BaseFinetuneFlux):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "finetune_id": ("STRING", {"default": "my-finetune"}),
                "image": ("STRING", {"default": None}),
                "finetune_strength": ("FLOAT", {"default": 1.1, "min": 0.1, "max": 2.0}),
                "steps": ("INT", {"default": 50, "min": 15, "max": 50}),
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
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, finetune_id, image, finetune_strength, steps, prompt_upsampling, guidance,
                       safety_tolerance, output_format, mask="", prompt="", seed=-1,
                       webhook_url="", webhook_secret="", config=None):
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
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "finetune_strength": ("FLOAT", {"default": 1.2, "min": 0.0, "max": 2.0}),
                "aspect_ratio": (["16:9", "4:3", "1:1", "3:2", "21:9", "9:16", "3:4", "2:3", "9:21"], {"default": "16:9"}),
                "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 6}),
                "output_format": (["jpeg", "png"], {"default": "jpeg"}),
                "raw": ("BOOLEAN", {"default": False})
            },
            "optional": {
                "seed": ("INT", {"default": -1}),
                "image_prompt": ("STRING", {"default": ""}),
                "image_prompt_strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0}),
                "prompt_upsampling": ("BOOLEAN", {"default": False}),
                "webhook_url": ("STRING", {"default": ""}),
                "webhook_secret": ("STRING", {"default": ""}),
                "config": ("BFL_CONFIG",)
            }
        }

    def generate_image(self, finetune_id, prompt, finetune_strength, aspect_ratio, safety_tolerance,
                       output_format, raw, seed=-1, image_prompt="", image_prompt_strength=0.1,
                       prompt_upsampling=False, webhook_url="", webhook_secret="", config=None):
        arguments = {
            "finetune_id": finetune_id,
            "prompt": prompt,
            "finetune_strength": finetune_strength,
            "aspect_ratio": aspect_ratio,
            "safety_tolerance": safety_tolerance,
            "output_format": output_format,
            "raw": raw,
            "prompt_upsampling": prompt_upsampling
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
        return self.generate_regional_image("flux-pro-1.1-ultra-finetuned", arguments, config)

    def generate_regional_image(self, endpoint, arguments, config_override=None):
        try:
            config_loader_instance = get_config_loader(config_override)
            config_loader_instance.set_x_key()

            post_url = config_loader_instance.create_url(endpoint)
            headers = {"x-key": config_loader_instance.get_x_key()}
            print(f"[BFL] POST {post_url}")
            response = requests.post(post_url, json=arguments, headers=headers, timeout=30)
            print(f"[BFL] POST response: {response.status_code}")

            if response.status_code == 200:
                task_id = response.json().get("id")
                if task_id:
                    print(f"[BFL] Finetune Task ID: {task_id} — endpoint: {post_url}")
                    return self.get_result(task_id, output_format=arguments.get("output_format", "jpeg"), config_override=config_override)
            else:
                print(f"[BFL] Error initiating regional finetune request: {response.status_code}, {response.text}")
                return self.create_blank_image()
        except Exception as e:
            print(f"[BFL] Error generating regional finetune image: {str(e)}")
            return self.create_blank_image()


NODE_CLASS_MAPPINGS = {
    "FluxFinetuneStatus_BFL": FluxFinetuneStatus,
    "FluxMyFinetunes_BFL": FluxMyFinetunes,
    "FluxFinetuneDetails_BFL": FluxFinetuneDetails,
    "FluxDeleteFinetune_BFL": FluxDeleteFinetune,
    "FluxProFillFinetune_BFL": FluxProFillFinetune,
    "FluxPro11UltraFinetune_BFL": FluxPro11UltraFinetune
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxFinetuneStatus_BFL": "Flux Finetune Status (BFL)",
    "FluxMyFinetunes_BFL": "Flux My Finetunes (BFL)",
    "FluxFinetuneDetails_BFL": "Flux Finetune Details (BFL)",
    "FluxDeleteFinetune_BFL": "Flux Delete Finetune (BFL)",
    "FluxProFillFinetune_BFL": "Flux Pro Fill Finetune (BFL)",
    "FluxPro11UltraFinetune_BFL": "Flux Pro 1.1 Ultra Finetune (BFL)"
}
