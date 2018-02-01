FROM mottosso/maya:2017

MAINTAINER andresmweber@gmail.com

ENV TEST_PATH /root/test-results
ENV PYTHONPATH /root/nvenv/lib/python2.7/site-packages
ENV MAYA_VERSION 2017

RUN yum install -y \
    epel-release \
    https://centos6.iuscommunity.org/ius-release.rpm \
    git2u

RUN yum install -y python27

RUN mkdir $TEST_PATH

RUN echo alias hpython="\"$HOME/nvenv/bin/python\"" >> ~/.bashrc