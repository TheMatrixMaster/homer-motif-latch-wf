FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:9a7d-main

# Update env
RUN apt-get update -y

# Add UNIX tools
RUN apt-get install -y gcc g++ make perl zip unzip gzip wget curl

# Get miniconda and set path
RUN curl -O \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

ENV PATH="/root/miniconda3/bin:$PATH"
ARG PATH="/root/miniconda3/bin:$PATH"

# testing conda installation
RUN conda --version && conda clean --all --yes

# Samtools
RUN conda install -c bioconda samtools

# Homer
RUN conda install -c bioconda homer
RUN perl /root/miniconda3/share/homer*/configureHomer.pl -install hg38

COPY data /root/reference
COPY wf /root/wf

# STOP HERE:
# The following lines are needed to ensure your build environement works
# correctly with latch.
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
RUN python3 -m pip install --upgrade latch
WORKDIR /root
