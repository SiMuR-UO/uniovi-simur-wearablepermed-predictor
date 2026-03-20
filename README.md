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
--name prediction-by-rf-model \
-u $(id -u):$(id -g) \
-v <PREDICTOR_FOLDER>/data:/data \
-v <PREDICTOR_FOLDER>/results:/results \
wearablepermed-predictor:1.6.0 \
--segment-body Thigh \
--model-id MODEL_PI_RF_ACC_GYR_15 \
--resource-id /data/PMP1024_W1_PI_1.csv \
--prediction-id-folder /results
```

Where <PREDICTOR_FOLDER> is any absolute path in your computer. Is recomendable and not mandatory create inside this one, three subfolder called: models, data and results:
- models: subfolder where locate your npz models to be used by predictor.
- data: subfolder where locate your segment body signal files to be predict in csv format.
- results: subfolder where the model create the prediction files in format csv or npz.

## Predictor Arguments 

- **resource-id-file (*)** : segment body file in csv format with acceleromter and gyroscope come from MATRIX sensors.

- **model-id (*)** : is the model key to be used for prediction. **The actual implementation only support RandomForest Individual models**.

- **is-label-text**: this is a optional boolean argument. By default is False, but when set True the predictions are string values not numerical.

- **prediction-id-folder (*)**: the folder where the predictor will create the prediction file.

- **prediction-file-format**: optional file prediction format used to be return. By default npz is selected. You can pass these values: [npz, csv]

(*) are mandatory arguments

If you want go into the container execute this command.

```bash
$ docker run \
--rm \
-it \
--name prediction-by-rf-model \
-u $(id -u):$(id -g) \
-v /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data:/data \
-v /home/miguel/temp/predictor/results:/results \
--entrypoint sh \
wearablepermed-predictor:1.6.0
```

## Default Value

All models offered by preeictor are trained with

- Window size of 250 and overlapping of 50%.
- Right now only individual models are offered by predc¡ictor: Wrist, Thigh or Hip segment bodies.

## Note

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.
