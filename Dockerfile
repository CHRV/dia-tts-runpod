FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu22.04

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    curl \
    git \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/

WORKDIR /app

COPY ./pyproject.toml .
COPY ./uv.lock .
RUN uv sync --locked

COPY ./handler.py .

CMD ["uv", "run", "handler.py"]

