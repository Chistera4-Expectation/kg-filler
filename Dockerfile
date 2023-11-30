FROM python:3.11-slim
RUN apt-get update && apt-get install -y git yq
COPY . /kgfiller
WORKDIR /kgfiller
RUN pip install -r requirements.txt
WORKDIR /kgfiller/data
RUN git checkout begin
WORKDIR /kgfiller
ENV SECRETS_PATH /run/secrets/all_secrets.yml
ENTRYPOINT [ "/usr/bin/bash", "entrypoint.sh" ]
