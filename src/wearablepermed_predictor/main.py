import os
import sys
import argparse
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

from wearablepermed_predictor.core import predict

__author__ = "Miguel Angel Salinas Gancedo<uo34525@uniovi.es>, Antonio Miguel López Rodriguez<amlopez@uniovi.es>"
__copyright__ = "Uniovi"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class ValidateSegments(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # 1. Check for duplicates
        if len(values) != len(set(values)):
            raise argparse.ArgumentError(self, f"Duplicate values found in {values}")
        
        # 2. Check maximum length
        if len(values) > 3:
            raise argparse.ArgumentError(self, f"Too many segments. Max is 3, you provided {len(values)}")
        
        setattr(namespace, self.dest, values)

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
        '-segment-body', 
        '--segment-body', 
        dest="segment_body",
        nargs='+',                         # Accepts 1 or more arguments
        choices=['Thigh', 'Wrist', 'Hip'], # Restricted collection
        action=ValidateSegments,           # Runs our custom validation logic
        required=True,                     # Ensures at least 1 is provided
        help="Body segments to process. Choices: wrist, thigh, hip (Max 3, no repeats)."
    )    
    parser.add_argument(
        "-resource-id-file",
        "--resource-id-file",
        required=True,
        dest="resource_id_file",
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
        "-prediction-file-format",
        "--prediction-file-format",
        default="npz",
        dest="prediction_file_format",
        help="prediction file_format"
    )
    parser.add_argument(
        "-prediction-id-folder",
        "--prediction-id-folder",
        required=True,
        dest="prediction_id_folder",
        help="Predictions folder results"
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

def predict_by_resource(segment_body, resource_id_file, model_id, predictor_label_encoder):    
    predictions = predict(segment_body, resource_id_file, model_id, predictor_label_encoder)

    return predictions

def main(args):
    # get arguments and configure app logger
    args = parse_args(args)
    setup_logging(args.loglevel)
    
    if len(args.segment_body) > 1:
        _logger.error("Predictor is not implemented to use more than one segment body using fusion models")    
        return

    # STEP01: get predictions from resource id
    _logger.info("STEP01: Loading arguments")

    # get service arguments
    base_file = Path(__file__).resolve().parent.parent.parent

    segment_body = args.segment_body    
    model_id = args.model_id    
    label_id = args.label_id
    resource_id_file = args.resource_id_file
    prediction_id_folder = args.prediction_id_folder    
    prediction_file_format = args.prediction_file_format

    # STEP02: Loading predictor model and labels if exist
    _logger.info("STEP02: Loading predictor model")
    predictor_model = load_model(model_id, base_file)

    predictor_labels = None
    if (label_id is not None):
        predictor_labels = load_labels(label_id, base_file)

    # STEP03: get predictions from resource id
    _logger.info(f"STEP03: Get predictions from model id {model_id} with label id {label_id}")
    predictions = predict_by_resource(segment_body, resource_id_file, predictor_model, predictor_labels)

    print(f"Prediction for a total of: {str(len(predictions))} items")

    # STEP04: save resource predictions
    if prediction_file_format == "npz":
        result_path = Path(prediction_id_folder) / "prediction.npz"

        np.savez_compressed(
            result_path, 
            timestamp=predictions[:,0], 
            label=predictions[:,1]
        )
    else:
        result_path = Path(prediction_id_folder) / "prediction.csv"

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