FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu22.04

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    curl \
    git \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app


RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-cache

COPY . .

RUN uv sync --locked --no-cache

CMD ["uv", "run", "handler.py"]

