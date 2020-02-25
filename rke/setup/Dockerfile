# Tao image tren moi truong python 3.7 cai google cloud sdk
FROM python:3.7
RUN apt-get update && apt-get install -y curl gnupg2 && \
    echo "deb http://packages.cloud.google.com/apt cloud-sdk-bionic main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    rm -rf /var/cache/*