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

3. Get your BFL API key from [api.bfl.ml](https://api.bfl.ml).

4. Add your API key to the `config.ini` file:
    ```ini
    [API]
    key = YOUR_API_KEY
    ```

## Usage

After setting up, you can begin using the custom nodes with Flux models through the BFL API.

## Workflow

An example workflow has been added to the `workflow` folder.

## Example

![image](https://github.com/user-attachments/assets/966427cb-af20-4e59-a59f-6fc507fabdd2)
![image](https://github.com/user-attachments/assets/6e66e4e7-2b04-48f4-8af3-f3859063d366)


