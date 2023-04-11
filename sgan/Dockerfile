FROM ubuntu:bionic

RUN apt -y update && apt -y upgrade
RUN apt -y install python3.7 python3-pip curl wget unzip vim

ADD "https://api.github.com/repos/affanbinusman/PIR_SGAN/commits?per_page=1" latest_commit
RUN curl -sLO "https://github.com/affanbinusman/PIR_SGAN/archive/main.zip" && unzip main.zip

WORKDIR /PIR_SGAN-main/sgan

RUN python3.7 -m pip install -r requirements.txt
RUN python3.7 -m pip install fastapi
RUN python3.7 -m pip install uvicorn

RUN sh scripts/download_data.sh
RUN sh scripts/download_models.sh
