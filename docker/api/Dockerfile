FROM lupai-mw-core

COPY lupai_mw /src/lupai_mw
COPY requirements.txt pyproject.toml /src/
RUN --mount=type=bind,target=/root/.cache,source=.git,target=/src/.git \
    uv pip install /src --no-deps

ARG API_PORT
WORKDIR /src
CMD uvicorn lupai_mw.api.app:app --host 0.0.0.0 --port "$API_PORT" \
    --ws websockets \
    --ws-ping-interval 60 \
    --ws-ping-timeout 180
