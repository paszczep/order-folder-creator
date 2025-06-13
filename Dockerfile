FROM ghcr.io/astral-sh/uv:python3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /dir_manager

COPY requirements.txt ./

RUN uv pip install \
    --requirement requirements.txt \
    --system

RUN apk add \
        samba-client \
        subversion

COPY config/ config/
COPY app/ app/

COPY entrypoint.sh ./
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
