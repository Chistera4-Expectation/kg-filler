FROM python:3.11-slim
RUN apt-get update && apt-get install -y git gh
COPY . /kgfiller
WORKDIR /kgfiller
#RUN pip install -r requirements.txt
WORKDIR /kgfiller/data
RUN git checkout begin
WORKDIR /kgfiller
ENV GH_TOKEN_PATH /run/secrets/gh_token
ENV OPENAI_API_KEY_PATH /run/secrets/openai_api_key
ENV HUGGING_USERNAME_PATH /run/secrets/hugging_username
ENV HUGGING_PASSWORD_PATH /run/secrets/hugging_password
ENTRYPOINT [ "/usr/bin/bash", "entrypoint.sh" ]
