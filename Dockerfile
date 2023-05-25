FROM python:3.8-slim-buster
ENV PYTHONBUFFERED = 1
WORKDIR /django
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
USER root
RUN apt-get update
RUN apt-get -y install emboss
RUN apt -y install ncbi-blast+
RUN apt -y install ncbi-entrez-direct
#RUN apt -y install wget
#RUN sh -c "$(wget -q ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -O -)"
#RUN export PATH=${PATH}:${HOME}/edirect
#RUN useradd -u 8877 nonroot
#USER nonroot