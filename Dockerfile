FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:02ab-main

# Update env
RUN apt-get update -y

# Add UNIX tools
RUN apt-get install -y gcc g++ make perl zip unzip gzip wget

# Add dependencies
RUN apt-get install -y bedtools samtools
RUN python3 -m pip install MACS2

# Install HOMER
# Code from https://github.com/chrisamiller/docker-homer/blob/master/Dockerfile
RUN mkdir /opt/homer/ && cd /opt/homer && wget http://homer.ucsd.edu/homer/configureHomer.pl && /usr/bin/perl configureHomer.pl -install 

#softlink config file and data directory
RUN rm -rf /opt/homer/data && ln -s /opt/homerdata/data /opt/homer/data
RUN rm -f /opt/homer/config.txt && ln -s /opt/homerdata/config.txt /opt/homer/config.txt

ENV PATH=${PATH}:/opt/homer/bin/

# Latch demo configuration
RUN curl -L https://sourceforge.net/projects/bowtie-bio/files/bowtie2/2.4.4/bowtie2-2.4.4-linux-x86_64.zip/download -o bowtie2-2.4.4.zip &&\
    unzip bowtie2-2.4.4.zip &&\
    mv bowtie2-2.4.4-linux-x86_64 bowtie2

RUN apt-get install -y autoconf

COPY data /root/reference
ENV BOWTIE2_INDEXES="reference"


# STOP HERE:
# The following lines are needed to ensure your build environement works
# correctly with latch.
COPY wf /root/wf
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
RUN python3 -m pip install --upgrade latch
WORKDIR /root
