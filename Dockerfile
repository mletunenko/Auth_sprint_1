FROM python:3.12

WORKDIR /app/src

COPY requirements.txt requirements.txt

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -U pip wheel && python -m pip install -r requirements.txt

COPY src /app/src
COPY /post-process/wait-for-it.sh /scripts/
