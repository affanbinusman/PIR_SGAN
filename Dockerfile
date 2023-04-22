FROM ubuntu:bionic

RUN apt -y update && apt -y upgrade
RUN apt -y install python3.7 python3-pip curl wget unzip vim

RUN python3.7 -m pip install attrdict==2.0.0
RUN python3.7 -m pip install numpy==1.14.5
RUN python3.7 -m pip install Pillow==6.2.0
RUN python3.7 -m pip install six==1.11.0
RUN python3.7 -m pip install torch==1.11.0
RUN python3.7 -m pip install torchvision==0.12.0
RUN python3.7 -m pip install fastapi
RUN python3.7 -m pip install uvicorn
RUN python3.7 -m pip install scipy==1.2.0

ADD "https://api.github.com/repos/affanbinusman/PIR_SGAN/commits/calculate-distance?per_page=1" latest_commit
RUN curl -sLO "https://github.com/affanbinusman/PIR_SGAN/archive/calculate-distance.zip" && unzip calculate-distance.zip
RUN mv /PIR_SGAN-calculate-distance /PIR_SGAN-main

WORKDIR /PIR_SGAN-main/sgan

RUN sh scripts/download_data.sh
RUN sh scripts/download_models.sh
