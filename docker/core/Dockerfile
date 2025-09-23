ARG UV_VERSION=0.8.20
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv_source

FROM ubuntu:plucky

ARG PYTHON_VERSION=3.13
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    curl \
    git-core \
    gcc \
    g++ \
    openssh-client \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-dev \
    python3-setuptools \
    ca-certificates \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/tmp/* /var/lib/apt/lists/*

RUN rm /usr/lib/python${PYTHON_VERSION}/EXTERNALLY-MANAGED
RUN update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1

ENV UV_SYSTEM_PYTHON=1
COPY --from=uv_source /uv /uvx /bin/

WORKDIR /tmp

COPY ./requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    uv pip install \
    --find-links https://github.com/aureka-team/common/releases/expanded_assets/index \
    --find-links https://github.com/aureka-team/llm-agents/releases/expanded_assets/index \
    --find-links https://github.com/aureka-team/multi-agents/releases/expanded_assets/index \
    --find-links https://github.com/aureka-team/rage2/releases/expanded_assets/index \
    -r requirements.txt

RUN rm -rf /tmp/*
WORKDIR /root

ENV REDIS_HOST=lupai-mw-redis
ENV QDRANT_HOST=lupai-mw-qdrant

ENV DENSE_EMBED_DOC_CACHE_PATH=/resources/cache/embeddings/documents
ENV DENSE_EMBED_QUERY_CACHE_PATH=/resources/cache/embeddings/queries
ENV FAST_EMBED_SPARSE_CACHE=/resources/cache/fes
ENV HF_HUB_CACHE=/resources/cache/hf
