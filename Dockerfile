FROM python:3.12.3-slim-bullseye as python

WORKDIR /app

# Install dependencies to build uwsgi and then remove them
# Install curl and vim while we're at it
RUN : \
    && BUILD_DEPS='build-essential gcc libc6-dev libpcre3-dev' \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_DEPS curl libpcre3 vim \
    && pip install uwsgi==2.0.25.1 \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements/main.txt ./requirements/prod.txt ./requirements/
RUN pip install -r ./requirements/main.txt -r ./requirements/prod.txt
ENV DJANGO_SETTINGS_MODULE="config.settings.production"
COPY ./ ./

RUN : \
    # Make scripts executable
    && find ./bin -type f -iname "*.sh" -exec chmod +x {} \;

ARG GIT_REV="N/A"
ENV GIT_REV=${GIT_REV}

ENTRYPOINT [ "/bin/bash" ]
