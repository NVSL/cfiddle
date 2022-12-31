FROM jupyter/scipy-notebook
### create user with a home directory
ARG NB_USER
ARG NB_UID
ARG FIDDLE_WHEEL
ARG ARG_THIS_DOCKER_IMAGE
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}
ENV THIS_DOCKER_IMAGE ${ARG_THIS_DOCKER_IMAGE}
USER root

##### Install cfiddle

COPY $FIDDLE_WHEEL .
RUN pip install ${FIDDLE_WHEEL##*/}
RUN cfiddle_install_prereqs.sh
COPY . cfiddle
RUN chown -R ${NB_USER}  cfiddle
##### Setup Jupyter

USER ${NB_USER}
RUN mkdir -p ${HOME}/.jupyter
COPY jupyter_notebook_config.py ${HOME}/.jupyter/

WORKDIR ${HOME}/cfiddle/examples

ENTRYPOINT  [ "cfiddle_with_env.sh",  "tini",  "-g",  "--"  ]
CMD start-notebook.sh
