FROM python:3.6-stretch

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENV GUROBI_HOME /gurobi/gurobi810/linux64/
ENV GRB_LICENSE_FILE=/gurobi/gurobi.lic
ENV PATH /usr/local/nvidia/bin/:$PATH
ENV PATH /gurobi/gurobi810/linux64/bin/:$PATH
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64
ENV LD_LIBRARY_PATH /gurobi/gurobi810/linux64/lib/:$LD_LIBRARY_PATH

# Tell nvidia-docker the driver spec that we need as well as to
# use all available devices, which are mounted at /usr/local/nvidia.
# The LABEL supports an older version of nvidia-docker, the env
# variables a newer one.
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
LABEL com.nvidia.volumes.needed="nvidia_driver"

COPY . /

RUN apt-get update --fix-missing && apt-get install -y \
    bzip2 \
    ca-certificates \
    curl \
    gcc \
    git \
    libc-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    wget \
    libevent-dev \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir \
    mkl \
    pip install -r requirements.txt

RUN cd /gurobi/gurobi810/linux64 && python3 setup.py install

RUN cd /

CMD ["/bin/bash"]