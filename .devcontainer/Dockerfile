FROM mcr.microsoft.com/devcontainers/base:jammy

RUN apt-get update -y && \
  apt install -y libgl1-mesa-glx curl software-properties-common wget && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install OpenFoam
RUN curl https://dl.openfoam.com/add-debian-repo.sh | sudo bash && \
    apt-get update -y && \
    apt-get -y install openfoam2406-default



# Determine architecture and download appropriate Miniconda installer
USER vscode
WORKDIR /home/vscode
RUN ARCH=$(uname -m) && \
  if [ "$ARCH" = "x86_64" ]; then \
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-py312_24.7.1-0-Linux-x86_64.sh"; \
  elif [ "$ARCH" = "aarch64" ]; then \
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-py312_24.7.1-0-Linux-aarch64.sh"; \
  else \
    echo "Unsupported architecture: $ARCH"; exit 1; \
  fi && \
  wget $MINICONDA_URL && \
  chmod +x $(basename $MINICONDA_URL) && \
  ./$(basename $MINICONDA_URL) -b && \
  rm $(basename $MINICONDA_URL)



# Install Python dependencies from requirements.txt if it exists
# Initialize conda and run package installs
RUN CONDA_PATH=/home/vscode/miniconda3/bin/conda && \
  $CONDA_PATH init && \
  $CONDA_PATH install -n base ipykernel --update-deps --force-reinstall -y
  # $CONDA_PATH install -n base -c conda-forge -c cadquery cadquery=master -y
  
RUN . /home/vscode/miniconda3/etc/profile.d/conda.sh && \
    conda activate base
    # pip install ezdxf --upgrade


RUN echo "source /usr/lib/openfoam/openfoam2406/etc/bashrc" >> /home/vscode/.bashrc