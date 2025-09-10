# LupAI Meinsvwissen

## Environment Setup

### Prerequisites

-   Install Make:

    ```bash
    sudo apt install make
    ```

-   Install the latest version of Docker by following the official [Docker installation guide](https://docs.docker.com/engine/install/ubuntu/).

### Dev Container

This project uses a preconfigured Dev Container.

-   Open this repository in VS Code:
    ```bash
    code .
    ```
-   After installing the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension, press F1 to open the Command Palette, type _Dev Containers_, and select: **Reopen in Container**

### Jupyter

Jupyter is preconfigured inside the Dev Container.
You can explore examples in the [notebooks/](notebooks/) directory.
When opening a notebook, select the appropriate kernel in the top-right corner: **Python Environments -> Python 3.13 (Global Env)**

### Custom Python Library

A local Python package named **lupai_mw** is included in the environment. After you add to or modify this library, it is not necessary to rebuild the container. However, if you are using it in a Jupyter notebook, you should restart that notebook.

### Python Dependencies

You can install additional Python libraries by adding them to the **requirements.txt**. You should rebuild the container afterward (F1 + Rebuild Container).

### Environment Variables

You can define environment variables in a `.env` file placed at the root of the project. These variables will be automatically loaded into the environment inside the Dev Container.

**Example `.env` file:**

```env
MY_CUSTOM_VAR=some-value
```
