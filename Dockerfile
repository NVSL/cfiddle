FROM jupyter/scipy-notebook
### create user with a home directory
ARG NB_USER
ARG NB_UID
ARG FIDDLE_WHEEL
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}
ENV THIS_DOCKER_IMAGE ${ARG_THIS_DOCKER_IMAGE}
USER root

##### Install cfiddle

#COPY . ./cfiddle
#RUN (cd cfiddle; bash ./bin/cfiddle_install_prereqs.sh)
RUN  chown -R ${NB_USER} ./cfiddle
USER ${NB_USER}
RUN pip install cfiddle/$FIDDLE_WHEEL
RUN cfiddle_install_prereqs.sh
RUN mkdir -p ${HOME}/.jupyter
COPY jupyter_notebook_config.py ${HOME}/.jupyter/

WORKDIR ${HOME}/cfiddle/examples

ENTRYPOINT  [ "/home/jovyan/cfiddle/bin/with_env.sh",  "tini",  "-g",  "--"  ]
CMD start-notebook.sh
