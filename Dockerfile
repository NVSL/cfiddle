FROM jupyter/scipy-notebook:lab-3.2.5
### create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}
ENV THIS_DOCKER_IMAGE ${ARG_THIS_DOCKER_IMAGE}
USER root

##### Install cfiddle

COPY  . ./cfiddle
RUN (export CFIDDLE_INSTALL_CROSS_COMPILERS=yes;cd cfiddle; bash ./install_prereqs.sh)
RUN  chown -R ${NB_USER} ./cfiddle
USER ${NB_USER}
RUN cd cfiddle;  pip install  .
RUN mkdir -p ${HOME}/.jupyter
COPY jupyter_notebook_config.py ${HOME}/.jupyter/

WORKDIR ${HOME}/cfiddle/examples

ENTRYPOINT  [ "/home/jovyan/cfiddle/bin/with_env.sh",  "tini",  "-g",  "--"  ]
CMD start-notebook.sh
