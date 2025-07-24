FROM lupai-mw-core

COPY lupai /src/lupai_mw
COPY requirements.txt pyproject.toml /src/
RUN --mount=type=bind,target=/root/.cache,source=.git,target=/src/.git \
    uv pip install /src --no-deps

ARG API_PORT
WORKDIR /src/lupai_mw/api
CMD fastapi run app.py --port ${API_PORT}
