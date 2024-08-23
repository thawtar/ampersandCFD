import os
from pathlib import Path
import logging

#logging string
logging.basicConfig(level=logging.INFO,format="[%(asctime)s]:[%(message)s]")

project_name = "ampersandCFD"

list_of_files = [
    "./github/workflows/.gitkeep",
    f"{project_name}/__init__.py",
    f"{project_name}/src/__init__.py",
    f"{project_name}/tests/__init__.py",
    f"{project_name}/config/__init__.py",
    f"{project_name}/docs/__init__.py",
    #f"{project_name}/pipeline/__init__.py",
    f"{project_name}/constants/__init__.py",
    "config/config.yaml",
    #"requirements.txt",
    "setup.py",
    "templates/index.html",
    "params.yaml",
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir,exist_ok=True)
        logging.info(f"Creating directory {filedir} for the file: {filename}")

    if(not os.path.exists(filepath) or (os.path.getsize(filepath)==0)):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating empty file: {filename}")
    else:
        logging.info(f"{filename} already exists.")


