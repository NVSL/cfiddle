FROM jupyter/scipy-notebook:lab-3.2.5
### create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}
USER root

##### system packages

RUN apt-get update --fix-missing; apt-get update
RUN apt-get install -y less emacs-nox gcc make g++ cmake gdb build-essential graphviz curl && apt-get clean -y #gcc-8 g++-8 libhdf5-dev uuid-runtime  openssh-client time  default-jdk

##### Redare2

RUN curl -L https://github.com/radareorg/radare2/releases/download/5.3.1/radare2-dev_5.3.1_amd64.deb -o /tmp/radare2-dev_5.3.1_amd64.deb
RUN curl -L https://github.com/radareorg/radare2/releases/download/5.3.1/radare2_5.3.1_amd64.deb -o /tmp/radare2_5.3.1_amd64.deb
RUN apt install /tmp/radare2_5.3.1_amd64.deb  /tmp/radare2-dev_5.3.1_amd64.deb

##### python stuff

RUN pip install wheel			   

##### Google test

RUN (cd /tmp; git clone https://github.com/google/googletest.git && cd googletest && cmake CMakeLists.txt; make install)

USER ${NB_USER}

##### Install fiddle

RUN git clone https://github.com/NVSL/fiddle.git && cd fiddle; pip install  .
ENV LD_LIBRARY_PATH  /opt/conda/lib/python3.9/site-packages/fiddle/resources/libfiddle

RUN mkdir -p .jupyter
COPY  jupyter_notebook_config.py .jupyter/

WORKDIR ${HOME}/fiddle/examples

