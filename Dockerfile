FROM jupyter/scipy-notebook:lab-3.2.5
### create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}
USER root

##### install system packages
COPY install_prereqs.sh ./
RUN bash ./install_prereqs.sh


##### Install fiddle
USER ${NB_USER}

COPY .clean_checkout ./fiddle
RUN cd fiddle; pip install  .
ENV LD_LIBRARY_PATH  /opt/conda/lib/python3.9/site-packages/fiddle/resources/libfiddle

RUN mkdir -p .jupyter
COPY  jupyter_notebook_config.py .jupyter/

WORKDIR ${HOME}/fiddle/examples

