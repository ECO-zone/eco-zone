FROM python:3.12.3-slim-bullseye as python

ENV DJANGO_SETTINGS_MODULE="config.settings.production"

# Install dependencies to build uwsgi and then remove them
# Install curl and vim while we're at it
RUN : \
    && BUILD_DEPS='build-essential gcc libc6-dev libpcre3-dev' \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_DEPS curl libpcre3 vim \
    && pip install uwsgi==2.0.25.1 \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and switch to a non-root user
RUN useradd -m ecozone
USER ecozone

WORKDIR /app

# Install Python dependencies
COPY --chown=ecozone:ecozone ./requirements/main.txt ./requirements/prod.txt ./requirements/
RUN pip install --no-cache-dir -r ./requirements/main.txt -r ./requirements/prod.txt

COPY --chown=ecozone:ecozone ./ ./

RUN : \
    # Make scripts executable
    && find ./bin -type f -iname "*.sh" -exec chmod +x {} \;

ENTRYPOINT [ "/bin/bash" ]
