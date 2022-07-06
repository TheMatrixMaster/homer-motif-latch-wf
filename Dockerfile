FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:02ab-main

# Update env
RUN apt-get update -y

# Add UNIX tools
RUN apt-get install -y gcc g++ make perl zip unzip gzip wget

# Add dependencies
RUN apt-get update && apt-get install -y libnss-sss samtools r-base r-base-dev tabix wget libssl-dev libcurl4-openssl-dev libxml2-dev && apt-get clean all

## Now install R and littler, and create a link for littler in /usr/local/bin
## Also set a default CRAN repo, and make sure littler knows about it too
RUN apt-get update \
    && apt-get install -y \
        r-base \
        r-base-dev \
        r-recommended \
    && echo 'options(repos = list(CRAN = "http://cran.rstudio.com/"))' >> /etc/R/Rprofile.site \
    && rm -rf /tmp/downloaded_packages/ /tmp/*.rds \
    && rm -rf /var/lib/apt/lists/*

## R packages - common stuff
RUN Rscript -e 'install.packages(c("devtools", "dplyr", "ggplot2", "reshape2"))' \
    && rm -rf /tmp/downloaded_packages/ /tmp/*.rds


# Install HOMER
# Code from https://github.com/chrisamiller/docker-homer/blob/master/DockerfileRUN
RUN mkdir /opt/homer/ && cd /opt/homer && wget http://homer.ucsd.edu/homer/configureHomer.pl && /usr/bin/perl configureHomer.pl -install 

#softlink config file and data directory
RUN rm -rf /opt/homer/data && ln -s /opt/homerdata/data /opt/homer/data
RUN rm -f /opt/homer/config.txt && ln -s /opt/homerdata/config.txt /opt/homer/config.txt

ENV PATH=${PATH}:/opt/homer/bin/

COPY data /root/reference

# STOP HERE:
# The following lines are needed to ensure your build environement works
# correctly with latch.
COPY wf /root/wf
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
RUN python3 -m pip install --upgrade latch
WORKDIR /root
