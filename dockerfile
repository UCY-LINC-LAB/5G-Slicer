FROM fogify-jupiter AS builder

# USER root
# COPY requirements.txt ./
#
# RUN pip install --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt
COPY ns3-python /ns3-python
WORKDIR /ns3-python
RUN sh build.sh



FROM fogify-jupiter

COPY --from=builder /opt/ns/dist2/ns-3.33-py3-none-any.whl /ns3-python/ns-3.33-py3-none-any.whl
WORKDIR /ns3-python/
RUN pip install ns-3.33-py3-none-any.whl

USER root
COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN jupyter nbextension enable --py widgetsnbextension && jupyter labextension install jupyter-leaflet @jupyter-widgets/jupyterlab-manager
RUN conda install -c conda-forge widgetsnbextension jupyterlab_widgets && conda clean  -afy \
    && find /opt/conda/ -follow -type f -name '*.a' -delete \
    && find /opt/conda/ -follow -type f -name '*.pyc' -delete \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete
WORKDIR /ns3-python

RUN pip install ns-3.33-py3-none-any.whl

WORKDIR $HOME
USER $NB_UID
COPY . /home/jovyan/work
ENV GRANT_SUDO=yes
USER root
EXPOSE 5600
ENTRYPOINT ["tini", "-g", "--"]
CMD ["start-notebook.sh"]