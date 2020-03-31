# start from base -- builder
FROM ubuntu:18.04 as builder
RUN pwd
# label(s)
LABEL maintainer="Mirko D'Andrea"
LABEL email="mirko.dandrea@cimafoundation.org"
LABEL version="1.0.0"
LABEL release_date="2020/01/13"

# change default shell (from sh to bash)
SHELL ["/bin/bash", "-c"]

# install system-wide deps 
RUN apt-get update
RUN apt-get install -y \
	gcc \
	g++ \
	make \
	build-essential \
	libpng-dev \
	libpng++-dev\
	libgeotiff-dev \ 
	libjpeg-dev \
	libz-dev \
	libc6-dev \
	bash-completion \
	python3 \
	python3-pip \
	python3-virtualenv \
	nano 

RUN useradd -m -p fp -s /bin/bash risico
WORKDIR /home/risico/
ADD ./risico.tgz .
ADD --chown=risico RISICO2015 .
RUN chmod +x RISICO2015

WORKDIR /home/risico/
ADD --chown=risico run_risico.sh .
RUN chmod +x run_risico.sh


# create venv for adapter
WORKDIR /home/risico/
ADD ./adapter.tgz ./
RUN chown -R risico:risico ./adapter

USER risico
WORKDIR /home/risico/adapter
RUN python3 -m virtualenv --python=python3 .venv
ENV PATH=/home/risico/adapter/.venv/bin:$PATH
RUN which python
RUN which pip
RUN pip install -r requirements.txt
RUN python --version



WORKDIR /home/risico/
ENTRYPOINT ["/home/risico/run_risico.sh"]
