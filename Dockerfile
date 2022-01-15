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


##### Install cfiddle

COPY  . ./cfiddle
RUN  chown -R ${NB_USER} ./cfiddle
USER ${NB_USER}
#RUN cd cfiddle; python setup.py build && pip install  -e .
RUN cd cfiddle;  pip install  .
ENV LD_LIBRARY_PATH  /opt/conda/lib/python3.9/site-packages/cfiddle/resources/libcfiddle/build
#ENV LD_LIBRARY_PATH  /home/jovyan/cfiddle/src/cfiddle/resources/libcfiddle/build/
#   

RUN mkdir -p .jupyter
COPY  jupyter_notebook_config.py .jupyter/

WORKDIR ${HOME}/cfiddle/examples

