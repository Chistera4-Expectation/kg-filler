FROM python:3.11-slim
RUN apt-get update && apt-get install -y git yq
COPY . /kgfiller
WORKDIR /kgfiller
RUN pip install -r requirements.txt
ENV SECRETS_PATH /run/secrets/all_secrets.yml
ENV RESTORE_ALL_CACHES false
ENV POST_MORTEM false
ENTRYPOINT [ "/usr/bin/bash", "entrypoint.sh" ]
