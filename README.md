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

# Description

Uniovi Simur WearablePerMed Predictor.

<!-- pyscaffold-notes -->
##  Build and publish docker image
You must install docker previous to use these commands

To build the image execute this command:
```bash
$ docker build -t wearablepermed-predictor:1.18.0 .
```

To tag the image to be published in `simuruo` docker hub account execute this command:
```bash
$ docker build tag wearablepermed-predictor:1.18.0 simuruo/wearablepermed-predictor:1.18.0 
```

Login in `simuruo` docker hub account execute this command:
```bash
$ docker login -u simuruo
Password: 
```

To publish image in `simuruo` docker hub account execute this command:
```bash
$ docker push simuruo/wearablepermed-predictor:1.18.0
```

## Execute from Python package
If you want use our models published in Huggin Face you must execute a command like this:

```bash
$ predictor \
--model-type randomforest,
--sensor-channel accelerometer_gyroscope,
--segment-body wrist,
--class-type classes_4
--resources-folder /home/miguel/temp/models/wearablepermed_models/input,
--resource-id PMP1024_W1_M.csv,
--cases-folder /home/miguel/temp/models/wearablepermed_models/results,
--case-id case_M_BRF_acc_gyr_4_classes,
--case-file-format csv,
--verbose
```

If you want to use your custom models must execute a command like this:
```bash
$ predictor \
--model_file /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/models/RandomForest.pkl,
--label_file /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/models/label_encoder.pkl,
--resources-folder /home/miguel/temp/models/wearablepermed_models/input,
--resource-id PMP1024_W1_M.csv,
--cases-folder /home/miguel/temp/models/wearablepermed_models/results,
--case-id case_M_BRF_acc_gyr_4_classes,
--case-file-format csv,
--verbose
```

**Actually only Ranfom Forest is implemented in predictor**

## Execute from docker image
```bash
$ docker run \
--rm \
-u $(id -u):$(id -g) \
-v /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/input:/home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/input \
-v /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/output:/home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/output \
simuruo/wearablepermed-predictor:1.18.0 \
--model-type randomforest \
--sensor-channel accelerometer_gyroscope \
--segment-body wrist \
--class-type classes_4 \
--resources-folder /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/input \
--resource-id case_PI_BRF_acc_gyr_01/PMP1024_W1_PI_1.csv \
--cases-folder /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/output \
--case-id case_PI_BRF_acc_gyr_4_classes_01 \
--verbose
```

## Predictor arguments

These arguments are used if you select Python Package or Docker containers to execute predictor command:

- **model-type**: The model type: esann, capture24, randomforest, xgboost.

- **sensor-channe**: The model channels trained: accelerometer, accelerometer_gyroscope.

- **class-type**: The model class type trained: classes_4, classes_15.

- **segment-body (*)**: The model segment body trained: thigh, wrist, hip.

- **model-file**: if you want use your custom model set the model file

- **label-file**: if you want use your custom labels set the label file

- **resources-folder (*)**: The root resourcers folder.

- **resource-id (*)**: The resource file id in csv format.

- **cases-folder**: The root cases folder.

- **case-id**: Case unique name where save results under cases-folder.

- **case-file-format**: Case file format. Default is npz. Possible values: [npz, csv].

- **is-label-export**: Specify if predictions are export as label format. Default is False.

- **is-database-export**: The prediction result is database saved. Default is False.

- **verbose**: activate verbose logging mode.

(*) are mandatory arguments

If you want login inside the container execute this command.

```bash
$ docker run \
--rm \
-it \
-u $(id -u):$(id -g) \
-v /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/input:/home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/input \
-v /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/output:/home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/output \
--entrypoint sh \
simuruo/wearablepermed-predictor:1.18.0
```

## Default Value

All models offered by predictor are trained with

- Window size of 250 and overlapping of 50%.
- Right now only individual models are offered by predc¡ictor: Wrist, Thigh or Hip segment bodies.

## Build and Publish in Pypi and Docker Hub
1. Set the final version to the precitor python package from file `setup.cfg`

     ```bash
     version = 1.18.0
     ```

2. Set the new version in the shell scripts: `run_predictor.sh`, `run_predictor.bat`

     Linux/Mac `run_predictor.sh` script:
     ```bash
     # --- CONFIGURATION (Change these) ---
     PREDICTOR_VERSION="1.18.0"
     ```

     Windows `run_predictor.bat script:
     ```bash
     :: --- SYSTEM CONFIGURATION ---
     set PREDICTOR_VERSION=1.18.0
     ```
3. Rebuild and publish package in Pypi repository (You must have credentials)

     ```bash
     $ tox -e clean
     $ tox -e build
     $ tox -e publish -- --repository pypi
     ```

4. Finally build docker image with the last version selected and publish in `simuruo` Docker Hub account (You must have credentials)

     ```bash
     $ docker build -t wearablepermed-predictor:1.18.0 .
     $ docker tag wearablepermed-predictor:1.18.0 simuruo/wearablepermed-predictor:1.18.0
     $ docker push simuruo/wearablepermed-predictor:1.18.0
     ```

## Note

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.
