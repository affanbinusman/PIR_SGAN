FROM ubuntu:bionic

RUN apt -y update && apt -y upgrade
RUN apt -y install python3.7 python3-pip git wget unzip vim

RUN git clone https://github.com/affanbinusman/PIR_SGAN.git

WORKDIR /PIR_SGAN/sgan

RUN python3.7 -m pip install -r requirements.txt

RUN sh scripts/download_data.sh
RUN sh scripts/download_models.sh
#RUN cp -r scripts/dataset .
#RUN cp -r scripts/models .
