FROM python:3.12.3-slim-bookworm as python

ARG APP_DIR=/app
ARG APP_GROUP=qsystem
ARG APP_USER=qsystem
ENV PYTHONUNBUFFERED 1

# Install dependencies to build uwsgi and then remove them
# Install vim while we're at it
# And create a non-root user
RUN : \
    && BUILD_DEPS='build-essential gcc libc6-dev' \
    && apt-get update \
    && apt-get install -y --no-install-recommends $BUILD_DEPS vim \
    && pip install uwsgi==2.0.25.1 \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/* \
    # Create a non-root user
    && mkdir $APP_DIR \
    && groupadd -r $APP_GROUP \
    && useradd --no-log-init -m -d $APP_DIR -g $APP_GROUP $APP_USER

WORKDIR $APP_DIR
# Install Python dependencies
COPY ./requirements/main.txt ./requirements/prod.txt ./requirements/
RUN pip install -r ./requirements/main.txt -r ./requirements/prod.txt
ENV DJANGO_SETTINGS_MODULE="config.settings.production"
COPY ./ ./

RUN : \
    # Make scripts executable
    && find ./bin -type f -iname "*.sh" -exec chmod +x {} \; \
    # Move Dokku resources into place
    && mv ./dokku/* . && rm -rf ./dokku && pwd && ls .

ARG GIT_REV="N/A"
ENV GIT_REV=${GIT_REV}

ENTRYPOINT [ "/bin/bash" ]
