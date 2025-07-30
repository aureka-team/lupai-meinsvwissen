FROM lupai-mw-core

COPY lupai_mw /src/lupai_mw
COPY requirements.txt pyproject.toml  /src/
RUN --mount=type=bind,target=/root/.cache,source=.git,target=/src/.git \
    uv pip install /src --no-deps

WORKDIR /src
CMD python -m lupai_mw.mcp.server
