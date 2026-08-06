# ComfyUI-FLUX-BFL-API

Custom nodes for integrating Flux models with the BFL API.

## Installation

### Option 1: Install via Custom Nodes Manager

1. Open the Custom Nodes Manager.
2. Search for "ComfyUI-FLUX-BFL-API".
3. Select the package and follow the installation instructions.

### Option 2: Manual Installation

1. Clone the repository:
    ```bash
    cd custom_nodes
    git clone https://github.com/gelasdev/ComfyUI-FLUX-BFL-API.git
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Get your BFL API key from [api.bfl.ai](https://api.bfl.ai).

4. Add your API key to the `config.ini` file:
    ```ini
    [API]
    X_KEY = YOUR_API_KEY
    BASE_URL = https://api.bfl.ai/v1/
    ```

## Configuration

You can either use `config.ini` for a global API key, or connect a **Flux Config (BFL)** node directly to any generation node to override the key, base URL, and region per-node. If no config node is connected, `config.ini` is used automatically.

## Nodes

### Generation
| Node | Description |
|---|---|
| Flux 3 Video T2V (BFL) | Text-to-video with FLUX 3 Video (up to 20 s, with audio) |
| Flux 3 Video I2V (BFL) | Image-to-video — feed keyframes from the Flux 3 Keyframes node or a single image |
| Flux 3 Video V2V (BFL) | Video continuation from an existing MP4 (URL or base64) |
| Flux Pro 1.1 (BFL) | Text-to-image with Flux Pro 1.1 |
| Flux Pro 1.1 Ultra (BFL) | High-resolution text-to-image |
| Flux Dev (BFL) | Text-to-image with Flux Dev |
| Flux Pro Fill (BFL) | Inpainting / outpainting |
| Flux Pro Expand (BFL) | Outpainting with directional padding |
| Flux Erase (BFL) | Object removal via binary mask (`flux-tools/erase-v1`) |
| Flux Outpaint (BFL) | Image extension via target canvas + reference offsets (`flux-tools/outpainting-v1`) |
| Flux Virtual Try-On (BFL) | Virtual try-on — dress a person image in a garment image (`flux-tools/vto-v1`) |
| Flux Virtual Try-On v2 (BFL) | Virtual try-on v2 — sharper face preservation, inputs up to 4 MP (`flux-tools/vto-v2`) |
| Flux Kontext Pro (BFL) | Image editing with context (up to 4 images) |
| Flux Kontext Max (BFL) | Image editing with context, max quality |
| Flux 2 Max (BFL) | Flux 2 Max generation |
| Flux 2 Pro (BFL) | Flux 2 Pro generation |
| Flux 2 Pro Preview (BFL) | Flux 2 Pro preview (latest advances) |
| Flux 2 Flex (BFL) | Flux 2 Flex generation |
| Flux 2 Klein 9B (BFL) | Flux 2 Klein 9B generation |
| Flux 2 Klein 9B Preview (BFL) | Flux 2 Klein 9B preview (latest advances) |
| Flux 2 Klein 4B (BFL) | Flux 2 Klein 4B generation |

The Flux 3 Video nodes output ComfyUI's native `VIDEO` type — connect them to the built-in Save Video / preview nodes (requires ComfyUI ≥ 0.3.30).

### Finetune
| Node | Description |
|---|---|
| Flux Pro Fill Finetune (BFL) | Inpainting with a finetuned model |
| Flux Pro 1.1 Ultra Finetune (BFL) | Ultra generation with a finetuned model |
| Flux Finetune Status (BFL) | Check the status of a finetune job |
| Flux My Finetunes (BFL) | List all your finetunes |
| Flux Finetune Details (BFL) | Get details of a specific finetune |
| Flux Delete Finetune (BFL) | Delete a finetune |

### Config
| Node | Description |
|---|---|
| Flux Config (BFL) | Override API key, base URL and region per-node |
| Flux Credits (BFL) | Check your remaining BFL API credits |

### Utils
| Node | Description |
|---|---|
| Image to Base64 (BFL) | Convert a ComfyUI IMAGE to base64 — choose `jpeg` (default) or `png` (lossless, recommended for masks) |
| Flux 3 Keyframes (BFL) | Combine up to 10 images (start, 8 middles, end) into the keyframes string for Flux 3 Video I2V — empty sockets are skipped; `timing: even` spreads them across the clip, `timing: custom` pins start at 0, middles at their `time_N` widgets and the end image at `end_time` (= clip length with `duration: auto`) |
| Video to Base64 (BFL) | Convert a ComfyUI VIDEO (LoadVideo output or a Flux 3 Video result) to a base64 MP4 string — feed it into Flux 3 Video V2V's `start_video` |

## Workflow

Example workflows are available in the `workflows` folder.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## Contributors

- [@pleberer](https://github.com/pleberer)
- [@Duanyll](https://github.com/Duanyll)

## Example

![image](https://github.com/user-attachments/assets/e74c4157-b113-4590-a19a-758ac044725f)
![image](https://github.com/user-attachments/assets/98011024-c929-4128-af76-af7925e3c445)
