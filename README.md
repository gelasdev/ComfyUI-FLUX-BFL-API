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
| Flux Pro 1.1 (BFL) | Text-to-image with Flux Pro 1.1 |
| Flux Pro 1.1 Ultra (BFL) | High-resolution text-to-image |
| Flux Dev (BFL) | Text-to-image with Flux Dev |
| Flux Pro Fill (BFL) | Inpainting / outpainting |
| Flux Pro Expand (BFL) | Outpainting with directional padding |
| Flux Kontext Pro (BFL) | Image editing with context (up to 4 images) |
| Flux Kontext Max (BFL) | Image editing with context, max quality |
| Flux 2 Max (BFL) | Flux 2 Max generation |
| Flux 2 Pro (BFL) | Flux 2 Pro generation |
| Flux 2 Flex (BFL) | Flux 2 Flex generation |
| Flux 2 Klein 9B (BFL) | Flux 2 Klein 9B generation |
| Flux 2 Klein 4B (BFL) | Flux 2 Klein 4B generation |

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
| Image to Base64 (BFL) | Convert a ComfyUI IMAGE to a base64 data URI for use as image input |

## Workflow

Example workflows are available in the `workflows` folder.

## Contributors

- [@pleberer](https://github.com/pleberer)
- [@Duanyll](https://github.com/Duanyll)

## Example

![image](https://github.com/user-attachments/assets/e74c4157-b113-4590-a19a-758ac044725f)
![image](https://github.com/user-attachments/assets/98011024-c929-4128-af76-af7925e3c445)
