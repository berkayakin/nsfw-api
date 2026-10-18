FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    KERAS_BACKEND=tensorflow \
    TF_CPP_MIN_LOG_LEVEL=2 \
    OPENNSFW2_HOME=/opt/opennsfw2

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Bake the model weights in so a container start never depends on downloading them.
# Plain RUN (not ADD --checksum) so it also builds with the legacy builder / docker-compose v1.
ARG WEIGHTS_URL=https://github.com/bhky/opennsfw2/releases/download/v0.1.0/open_nsfw_weights.h5
ARG WEIGHTS_SHA256=14ca261f48bdd88c1eecba96a761bd1579b523adae1b749b0a4ffd8b7ed8babe
RUN python -c "import hashlib, os, sys, urllib.request; \
path = os.environ['OPENNSFW2_HOME'] + '/.opennsfw2/weights/open_nsfw_weights.h5'; \
os.makedirs(os.path.dirname(path), exist_ok=True); \
urllib.request.urlretrieve(sys.argv[1], path); \
digest = hashlib.sha256(open(path, 'rb').read()).hexdigest(); \
sys.exit(0 if digest == sys.argv[2] else 'weights checksum mismatch: ' + digest)" \
    "$WEIGHTS_URL" "$WEIGHTS_SHA256"

EXPOSE 8000
