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

## Multi-Agent System (work in progress)

### Diagrams

#### 1. Install the [excalidraw extension](https://marketplace.visualstudio.com/items?itemName=pomdtr.excalidraw-editor) locally in VS Code.

#### 2. Once installed, you can view the [diagrams](./diagrams/multi-agent.excalidraw) directly in VS Code.

## Testing the multi-agent system

### 1. Create Qdrant Data

To test the **multi-agent system**, you need to set up and initialize the Qdrant collections, which will be accessible via tools in the **MCP server**.

#### 1.1 Start Required Services

##### Start Redis

```bash
make redis-start
```

##### Start Qdrant

```bash
make qdrant-start
```

Once Qdrant is running, you can access its [web dashboard](http://localhost:6333/dashboard).

#### 1.2 Initialize Qdrant Collections

After both Redis and Qdrant are running, create the required Qdrant collections by running:

```bash
make create-qdrant-collections
```

### 2. Start the MCP server

```bash
make mcp-start
```

### 3. OpenAI API Key

Create a .env file in the root directory of the project and define the OPENAI_API_KEY variable:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Replace **your_openai_api_key_here** with your actual OpenAI API key.

### 4. Run the test script

```bash
make make test-chat
```
