FROM python:3.11-slim
RUN apt-get update && apt-get install -y git yq
RUN mkdir /kgfiller
COPY ./requirements.txt /kgfiller/requirements.txt
RUN pip install -r /kgfiller/requirements.txt
COPY . /kgfiller
WORKDIR /kgfiller
RUN rm -rf /kgfiller/data
ENV SECRETS_PATH /run/secrets/all_secrets.yml
ENV RESTORE_ALL_CACHES false
ENV POST_MORTEM false
ENV TIMEOUT 2d
ENTRYPOINT [ "/usr/bin/bash", "entrypoint.sh" ]
