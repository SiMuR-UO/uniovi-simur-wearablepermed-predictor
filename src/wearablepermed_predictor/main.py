import os
import sys
import argparse
import logging
import joblib
import smtplib
import numpy as np
import pandas as pd
from pathlib import Path
from pyaml_env import parse_config

import predictor_characteristics

__author__ = "Miguel Angel Salinas Gancedo<uo34525@uniovi.es>, Alejandro Castellanos Alonso<uo265351@uniovi.es>, Antonio Miguel López Rodriguez<amlopez@uniovi.es>"
__copyright__ = "Uniovi"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

def parse_args(args):   
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Predictor Job")
    parser.add_argument(
        "-resource-id",
        "--resource-id",
        required=True,
        dest="resource_id",
        help="resource file [csv]"
    )    
    parser.add_argument(
        "-model-id",
        "--model-id",
        required=True,
        dest="model_id",
        help="Model Id"
    )
    parser.add_argument(
        "-label-id",
        "--label-id",
        dest="label_id",
        help="Label Id"
    )
    parser.add_argument(
        "-prediction-format",
        "--prediction-format",
        default="npz",
        dest="prediction_format",
        help="prediction format"
    )             
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )   
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )

    return parser.parse_args(args)

def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )

def load_model(model_id, base_path):
    # 1. Reconstruct the exact same path used in store()
    file_path = os.path.join(base_path, 'models', model_id)
    
    # 2. Load the model from the disk
    if os.path.exists(file_path):
        model = joblib.load(file_path)

        return model
    else:
        print("Error: Model file not found.")

        return None

def load_labels(label_id, base_path):
    # 1. Reconstruct the exact same path used in store()
    file_path = os.path.join(base_path, 'models', label_id)
    
    # 2. Load the model from the disk
    if os.path.exists(file_path):
        labels = joblib.load(file_path)

        return labels
    else:
        print("Error: Labels file not found.")

        return None

def predict_by_resource(resource_id, model_id, predictor_label_encoder):    
    predictions = predictor_characteristics.predict(resource_id, model_id, predictor_label_encoder)

    return predictions

def main(args):
    # get arguments and configure app logger
    args = parse_args(args)
    setup_logging(args.loglevel)
    
    # STEP01: get predictions from resource id
    _logger.info("STEP01: Loading arguments")

    # get service arguments
    base_file = Path(__file__).resolve().parent.parent.parent

    model_id = args.model_id    
    label_id = args.label_id
    resource_id = args.resource_id
    prediction_format = args.prediction_format

    # STEP02: Loading predictor model
    _logger.info("STEP02: Loading predictor model")
    predictor_model = load_model(model_id, base_file)

    if (label_id is not None):
        predictor_labels = load_labels(label_id, base_file)

    # STEP03: get predictions from resource id
    _logger.info(f"STEP03: Get predictions from model id {model_id} with label id {label_id}")
    predictions = predict_by_resource(resource_id, predictor_model, predictor_labels)

    print(f"Prediction for a total of: {str(len(predictions))} items")

    # STEP04: save resource predictions
    if prediction_format == "npz":
        result_path = base_file / "results" / "predictions.npz"

        np.savez_compressed(
            result_path, 
            timestamp=predictions[:,0], 
            label=predictions[:,1]
        )
    else:
        result_path = base_file / "results" / "predictions.csv"

        df = pd.DataFrame({
            'timestamp': predictions[:,0],
            'label': predictions[:,1]
        })

        df.to_csv(result_path, index=False)

    print(f"File saved successfully at: {result_path.name}")

    _logger.info("Predictor finalized")

def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])

if __name__ == "__main__":
    run()        