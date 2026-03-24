<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/uniovi-simur-wearablepermed-predictor.svg?branch=main)](https://cirrus-ci.com/github/<USER>/uniovi-simur-wearablepermed-predictor)
[![ReadTheDocs](https://readthedocs.org/projects/uniovi-simur-wearablepermed-predictor/badge/?version=latest)](https://uniovi-simur-wearablepermed-predictor.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/uniovi-simur-wearablepermed-predictor/main.svg)](https://coveralls.io/r/<USER>/uniovi-simur-wearablepermed-predictor)
[![PyPI-Server](https://img.shields.io/pypi/v/uniovi-simur-wearablepermed-predictor.svg)](https://pypi.org/project/uniovi-simur-wearablepermed-predictor/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/uniovi-simur-wearablepermed-predictor.svg)](https://anaconda.org/conda-forge/uniovi-simur-wearablepermed-predictor)
[![Monthly Downloads](https://pepy.tech/badge/uniovi-simur-wearablepermed-predictor/month)](https://pepy.tech/project/uniovi-simur-wearablepermed-predictor)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/uniovi-simur-wearablepermed-predictor)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# uniovi-simur-wearablepermed-predictor

> Uniovi Simur WearablePerMed Predictor.

A longer description of your project goes here...

<!-- pyscaffold-notes -->
## Excute from docker
You must to be install docker previos to use this image

```bash
$ docker run \
--rm \
-u $(id -u):$(id -g) \
-v /home/miguel/temp/sample/data/PMP1024_W1_PI_1.csv:/home/miguel/temp/sample/data/PMP1024_W1_PI_1.csv \
-v /home/miguel/temp/sample/results:/home/miguel/temp/sample/results \
simuruo/wearablepermed-predictor:1.10.0 \
--model-id MODEL_PI_RF_ACC_GYR_15 \
--resource-id "/home/miguel/temp/sample/data/PMP1024_W1_PI_1.csv" \
--prediction-folder "/home/miguel/temp/sample/results"
```

## Predictor Arguments 

- **models-base-path** :The model base path where models are saved.

- **model-id (*)** :The model id to be load. Possible values are: [MODEL_PI_RF_ACC_GYR_15, MODEL_M_RF_ACC_GYR_15, MODEL_C_RF_ACC_GYR_15, MODEL_PI_RF_ACC_GYR_4, MODEL_M_RF_ACC_GYR_4, MODEL_C_RF_ACC_GYR_4. Example: MODEL_PI_RF_ACC_GYR_15]

- **resource-id (*)** : The resource file id in csv format.

- **prediction-folder (*)**: Prediction results folder.

- **prediction-file-format**: Prediction file format. Default is npz. Possible values: [npz, csv]

- **is-label-export**: Specify if predictions are export as label format. Default is False.

- **is-database-export**: The prediction result is database saved. Default is False.

- **v**: activate verbose results

(*) are mandatory arguments

If you want go into the container execute this command.

```bash
$ docker run \
--rm \
-it \
-u $(id -u):$(id -g) \
-v /home/miguel/temp/sample/data/PMP1024_W1_PI_1.csv:/home/miguel/temp/sample/data/PMP1024_W1_PI_1.csv \
-v /home/miguel/temp/sample/results:/home/miguel/temp/sample/results \
--entrypoint sh \
simuruo/wearablepermed-predictor:1.10.0
```

## Default Value

All models offered by predictor are trained with

- Window size of 250 and overlapping of 50%.
- Right now only individual models are offered by predc¡ictor: Wrist, Thigh or Hip segment bodies.

## Build and Publish in Pypi and Docker Hub
1. Set the final version to the precitor python package from file `setup.cfg`

     ```bash
     version = 1.11.0
     ```

2. Set the new version in the shell scripts: `run_predictor.sh`, `run_predictor.bat`

     Linux/Mac `run_predictor.sh` script:
     ```bash
     # --- CONFIGURATION (Change these) ---
     PREDICTOR_VERSION="1.11.0"
     ```

     Windows `run_predictor.bat script:
     ```bash
     :: --- SYSTEM CONFIGURATION ---
     set PREDICTOR_VERSION=1.11.0
     ```
3. Rebuild and publish package in Pypi repository (You must have credentials)

     ```bash
     $ tox -e clean
     $ tox -e build
     $ tox -e publish -- --repository pypi
     ```

4. Finally build docker image with the last version selected and publish in `simuruo` Docker Hub account (You must have credentials)

     ```bash
     $ docker build -t wearablepermed-predictor:1.11.0 .
     $ docker tag wearablepermed-predictor:1.11.0 simuruo/wearablepermed-predictor:1.11.0
     $ docker push simuruo/wearablepermed-predictor:1.11.0
     ```

## Note

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.
