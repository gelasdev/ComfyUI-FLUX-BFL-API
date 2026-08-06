import io
import json

import numpy as np
import requests

from .base import REQUEST_TIMEOUT, BaseFlux

try:
    from comfy_api.input_impl import VideoFromFile
except ImportError:
    VideoFromFile = None
    print("[BFL] comfy_api.input_impl not found — Flux 3 Video nodes disabled (requires ComfyUI >= 0.3.30)")

VIDEO_DURATIONS = ["auto"] + [str(i) for i in range(5, 21)]
VIDEO_ASPECT_RATIOS = ["auto", "21:9", "2:1", "16:9", "4:3", "1:1", "3:4", "9:16"]


class BaseFlux3Video(BaseFlux):
    CATEGORY = "BFL/Flux3"
    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "generate_video"

    # Video generation outlasts the 40-attempt image ceiling; 5s interval -> ~20 min.
    # A real v2v+fhd task was still Generating at 11 min, so 120 attempts proved too low.
    VIDEO_MAX_ATTEMPTS = 240

    @classmethod
    def common_input_types(cls):
        return {
            "prompt": ("STRING", {"default": "", "multiline": True}),
            "resolution": (["hd", "fhd"], {"default": "hd"}),
            "duration": (VIDEO_DURATIONS, {"default": "auto"}),
            "aspect_ratio": (VIDEO_ASPECT_RATIOS, {"default": "auto"}),
            "generate_audio": ("BOOLEAN", {"default": True}),
            "safety_tolerance": ("INT", {"default": 2, "min": 0, "max": 4}),
            "draft": ("BOOLEAN", {"default": False}),
        }

    def build_arguments(
        self, mode, prompt, resolution, duration, aspect_ratio, generate_audio, safety_tolerance, draft
    ):
        arguments = {"mode": mode, "prompt": prompt}
        if resolution != "hd":
            arguments["resolution"] = resolution
        if duration != "auto":
            arguments["duration"] = int(duration)
        if aspect_ratio != "auto":
            arguments["aspect_ratio"] = aspect_ratio
        if not generate_audio:
            arguments["generate_audio"] = False
        if safety_tolerance != 2:
            arguments["safety_tolerance"] = safety_tolerance
        if draft:
            arguments["draft"] = True
        return arguments

    def process_result(self, result, output_format="jpeg"):
        try:
            sample_url = result["result"]["sample"]
            video_response = requests.get(sample_url, timeout=REQUEST_TIMEOUT)
            video_response.raise_for_status()
            size_mb = len(video_response.content) / (1024 * 1024)
            print(f"[BFL] Video downloaded ({size_mb:.1f} MB)")
            return (VideoFromFile(io.BytesIO(video_response.content)),)
        except KeyError as e:
            print(f"[BFL] KeyError: Missing expected key {e}")
            return self.create_blank_image()
        except Exception as e:
            print(f"[BFL] Error processing video result: {str(e)}")
            return self.create_blank_image()

    def create_blank_image(self):
        """Return a 1-frame black 512x512 VIDEO instead of an IMAGE tensor.

        Keeps the BaseFlux method name because every failure path in
        BaseFlux.get_result / post_request calls create_blank_image();
        a VIDEO-returning node must never emit an IMAGE tensor.
        """
        import av  # ships with ComfyUI; only needed on failure paths

        buffer = io.BytesIO()
        container = av.open(buffer, mode="w", format="mp4")
        stream = container.add_stream("h264", rate=1)
        stream.width = 512
        stream.height = 512
        stream.pix_fmt = "yuv420p"
        frame = av.VideoFrame.from_ndarray(np.zeros((512, 512, 3), dtype=np.uint8), format="rgb24")
        for packet in stream.encode(frame):
            container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
        container.close()
        buffer.seek(0)
        return (VideoFromFile(buffer),)

    def generate_video_request(self, arguments, config=None):
        try:
            task_id = self.post_request("flux-3-video", arguments, config)
            if task_id:
                print(f"Task ID '{task_id}'")
                return self.get_result(task_id, max_attempts=self.VIDEO_MAX_ATTEMPTS, config_override=config)
            return self.create_blank_image()
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return self.create_blank_image()


class Flux3VideoT2V(BaseFlux3Video):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": cls.common_input_types(), "optional": {"config": ("BFL_CONFIG",)}}

    def generate_video(
        self, prompt, resolution, duration, aspect_ratio, generate_audio, safety_tolerance, draft, config=None
    ):
        arguments = self.build_arguments(
            "t2v", prompt, resolution, duration, aspect_ratio, generate_audio, safety_tolerance, draft
        )
        return self.generate_video_request(arguments, config)


class Flux3Keyframes:
    """Combine up to 10 images into the keyframes string for Flux 3 Video I2V.

    Empty sockets are skipped. With timing "even" the connected images are sent
    as a plain list: the first starts the video, the last ends it, the middles
    fall evenly in between (per the BFL API, 3 or more need a set duration on
    the video node). With timing "custom" every image is sent as a
    [seconds, image] pair — the API allows no mixing, so all frames get a time:
    start_image is pinned at 0, each middle at its time widget, and end_image
    at end_time, which with duration "auto" also sets the clip length ("the
    video runs to the last pair's second, rounded up").
    """

    CATEGORY = "BFL/Flux3"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("keyframes",)
    FUNCTION = "combine"

    MIDDLE_SLOTS = [(f"image_{i}", f"time_{i}") for i in range(2, 10)]

    @classmethod
    def INPUT_TYPES(cls):
        image_socket = ("STRING", {"forceInput": True, "tooltip": "Base64 image (from Image to Base64) or image URL"})
        time_widget = (
            "FLOAT",
            {
                "default": 0.0,
                "min": 0.0,
                "max": 20.0,
                "step": 0.05,
                "tooltip": 'Second to pin the matching image at — only used when timing is "custom"',
            },
        )
        optional = {"start_image": image_socket}
        for image_name, time_name in cls.MIDDLE_SLOTS:
            optional[image_name] = image_socket
            optional[time_name] = time_widget
        optional["end_image"] = image_socket
        optional["end_time"] = (
            "FLOAT",
            {
                "default": 5.0,
                "min": 0.0,
                "max": 20.0,
                "step": 0.05,
                "tooltip": 'Second the end image lands at (timing "custom") — with duration "auto" '
                "this is the clip length",
            },
        )
        return {
            "required": {
                "timing": (
                    ["even", "custom"],
                    {
                        "default": "even",
                        "tooltip": "even: images fall evenly across the clip; custom: start at 0, middles at "
                        "their time widgets, end at end_time",
                    },
                ),
            },
            "optional": optional,
        }

    def combine(self, timing="even", **inputs):
        frames = []
        if inputs.get("start_image"):
            frames.append([0.0, inputs["start_image"]])
        for image_name, time_name in self.MIDDLE_SLOTS:
            if inputs.get(image_name):
                frames.append([inputs.get(time_name, 0.0), inputs[image_name]])
        end_image = inputs.get("end_image")
        if end_image:
            frames.append([inputs.get("end_time", 0.0), end_image])
        if not frames:
            return ("",)
        if timing == "custom":
            frames.sort(key=lambda pair: pair[0])
            times = [pair[0] for pair in frames]
            if len(set(times)) != len(times):
                print(f"[BFL] Warning: duplicate keyframe times {times} — set a distinct time for each image")
            if end_image and frames[-1][1] is not end_image:
                print("[BFL] Warning: end_time is not the largest time — the end image will not end the video")
            return (json.dumps(frames),)
        return (json.dumps([image for _, image in frames]),)


class Flux3VideoI2V(BaseFlux3Video):
    @classmethod
    def INPUT_TYPES(cls):
        common = cls.common_input_types()
        return {
            "required": {
                "prompt": common.pop("prompt"),
                "keyframes": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Connect a Flux 3 Keyframes node, or paste a single image URL/base64, "
                        'or a JSON array of images or [seconds, image] pairs (up to 10): [[0, "..."], [4.5, "..."]]',
                    },
                ),
                **common,
            },
            "optional": {"config": ("BFL_CONFIG",)},
        }

    def generate_video(
        self,
        prompt,
        keyframes,
        resolution,
        duration,
        aspect_ratio,
        generate_audio,
        safety_tolerance,
        draft,
        config=None,
    ):
        arguments = self.build_arguments(
            "i2v", prompt, resolution, duration, aspect_ratio, generate_audio, safety_tolerance, draft
        )
        if not keyframes.strip():
            print("[BFL] i2v requires keyframes — connect a Flux 3 Keyframes node or an image string")
            return self.create_blank_image()
        try:
            arguments["keyframes"] = json.loads(keyframes)
        except ValueError:
            # Not JSON: treat as a single bare image (URL or base64) opening the clip, per the API docs
            arguments["keyframes"] = keyframes
        parsed = arguments["keyframes"]
        if (
            isinstance(parsed, list)
            and len(parsed) >= 3
            and all(isinstance(k, str) for k in parsed)
            and duration == "auto"
        ):
            print("[BFL] Warning: 3+ plain keyframes need a set duration — BFL rejects duration=auto for these")
        return self.generate_video_request(arguments, config)


class Flux3VideoV2V(BaseFlux3Video):
    @classmethod
    def INPUT_TYPES(cls):
        common = cls.common_input_types()
        return {
            "required": {"prompt": common.pop("prompt"), "start_video": ("STRING", {"default": ""}), **common},
            "optional": {"config": ("BFL_CONFIG",)},
        }

    def generate_video(
        self,
        prompt,
        start_video,
        resolution,
        duration,
        aspect_ratio,
        generate_audio,
        safety_tolerance,
        draft,
        config=None,
    ):
        arguments = self.build_arguments(
            "v2v", prompt, resolution, duration, aspect_ratio, generate_audio, safety_tolerance, draft
        )
        arguments["start_video"] = start_video
        return self.generate_video_request(arguments, config)


NODE_CLASS_MAPPINGS = (
    {
        "Flux3VideoT2V_BFL": Flux3VideoT2V,
        "Flux3VideoI2V_BFL": Flux3VideoI2V,
        "Flux3VideoV2V_BFL": Flux3VideoV2V,
        "Flux3Keyframes_BFL": Flux3Keyframes,
    }
    if VideoFromFile
    else {}
)

NODE_DISPLAY_NAME_MAPPINGS = (
    {
        "Flux3VideoT2V_BFL": "Flux 3 Video T2V (BFL)",
        "Flux3VideoI2V_BFL": "Flux 3 Video I2V (BFL)",
        "Flux3VideoV2V_BFL": "Flux 3 Video V2V (BFL)",
        "Flux3Keyframes_BFL": "Flux 3 Keyframes (BFL)",
    }
    if VideoFromFile
    else {}
)
