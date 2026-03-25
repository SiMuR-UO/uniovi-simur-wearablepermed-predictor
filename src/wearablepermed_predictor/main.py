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

# Your Collection of Objects (Source of Truth)
MODELS_CONFIG = [
    {
        'key': 'MODEL_PI_RF_ACC_GYR_4',
        'path': 'case_PI_BRF_acc_gyr_4_classes',
        'segment_body': 'Thigh',
        'help': 'Individual RandomForest Model for thigh with accelerometer, gyroscope and 4 classes'
    },    
    {
        'key': 'MODEL_PI_RF_ACC_GYR_15',
        'path': 'case_PI_BRF_acc_gyr_15_classes',
        'segment_body': 'Thigh',
        'help': 'Individual RandomForest Model for thigh with accelerometer, gyroscope and 15 classes'
    },
    {
        'key': 'MODEL_M_RF_ACC_GYR_4',
        'path': 'case_M_BRF_acc_gyr_4_classes',
        'segment_body': 'Wrist',
        'help': 'Individual RandomForest Model for wrist with accelerometer, gyroscope and 4 classes'
    },    
    {
        'key': 'MODEL_M_RF_ACC_GYR_15',
        'path': 'case_M_BRF_acc_gyr_15_classes',
        'segment_body': 'Wrist',
        'help': 'Individual RandomForest Model for wrist with accelerometer, gyroscope and 15 classes'
    },
    {
        'key': 'MODEL_C_RF_ACC_GYR_4',
        'path': 'case_C_BRF_acc_gyr_4_classes',
        'segment_body': 'hip',
        'help': 'Individual RandomForest Model for hip with accelerometer, gyroscope and 4 classes'
    },    
    {
        'key': 'MODEL_C_RF_ACC_GYR_15',
        'path': 'case_C_BRF_acc_gyr_15_classes',
        'segment_body': 'hip',
        'help': 'Individual RandomForest Model for hip with accelerometer, gyroscope and 15 classes'
    },       
]

# Helper to get keys for argparse choices
MODEL_LOOKUP = {m['key']: m for m in MODELS_CONFIG}

available_models = ", ".join(MODEL_LOOKUP.keys())

def model_object_type(selection):
    """Custom type function for argparse to return the full object"""
    if selection in MODEL_LOOKUP:
        return MODEL_LOOKUP[selection]

    # This part handles the error message if the user types something wrong
    raise argparse.ArgumentTypeError(f"Invalid model key: '{selection}'. Choose from {list(MODEL_LOOKUP.keys())}")

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_args(args):   
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Predictor Service")       
    parser.add_argument(
        '--models-folder',
        '---models-folder',
        required=True,
        dest="models_folder",        
        help=f"The root models folder."
    )      
    parser.add_argument(
        '-model-id',
        '--model-id',
        type=model_object_type,
        choices=list(MODEL_LOOKUP.values()), # We pass objects, but argparse uses their str() for help
        metavar="MODEL_KEY",
        required=True,
        dest="model_id",        
        help=f"The model id to be load. Options: {available_models}"
    )
    parser.add_argument(
        '--resources-folder',
        '---resources-folder',
        required=True,
        dest="resources_folder",        
        help=f"The root resourcers folder."
    )          
    parser.add_argument(
        "-resource-id",
        "--resource-id",
        required=True,
        dest="resource_id",
        help="The resource file id in csv format"
    )
    parser.add_argument(
        "-cases-folder",
        "--cases-folder",
        required=True,
        dest="cases_folder",
        help="The root cases folder"
    )
    parser.add_argument(
        '-case-id',
        '--case-id',
        dest="case_id",        
        help="Case unique name under prediction-folder."
    )          
    parser.add_argument(
        '-is-label-export',
        '--is-label-export',
        type=str2bool,
        nargs='?', # Allows the flag to be used without a value
        const=True, # Value used if flag is present but no value given
        default=False,
        dest="is_label_export",
        help="Specify if predictions are export as label format. Default is False."
    )       
    parser.add_argument(
        "-case-file-format",
        "--case-file-format",
        default="npz",
        dest="case_file_format",
        help="Case file format. Default is npz. Possible values: [npz, csv]"
    )
    parser.add_argument(
        '-is-database-export',
        '--is-database-export',
        type=str2bool,
        nargs='?', # Allows the flag to be used without a value
        const=True, # Value used if flag is present but no value given
        default=False,
        dest="is_database_export",
        help="The prediction result is database saved. Default is False."
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

def load_model(base_path, model_type):
    # 1. Reconstruct the exact same path used in store()
    model_path = base_path / model_type / 'RandomForest.pkl'
    
    # 2. Load the model from the disk
    if os.path.exists(model_path):
        model = joblib.load(model_path)

        return model
    else:
        _logger.error(f"Model not found for type {model_type}.")

        raise Exception(f"Model not found for type {model_type}.")        

def load_labels(base_path, model_type):
    # 1. Reconstruct the exact same path used in store()
    label_path = base_path / model_type / 'label_encoder.pkl'

    # 2. Load the model from the disk
    if os.path.exists(label_path):
        label = joblib.load(label_path)

        return label
    else:
        _logger.error(f"Labels not found for type {model_type}.")

        raise Exception(f"Labels not found for type {model_type}.")

def predict_by_resource(segment_body, resource_id, model_id, predictor_label_encoder):    
    predictions = predict(segment_body, resource_id, model_id, predictor_label_encoder)

    return predictions

def main(args):
    # get arguments and configure app logger
    args = parse_args(args)
    setup_logging(args.loglevel)
    
    # STEP01: get predictions from resource id
    _logger.info("STEP01: Loading arguments")

    # get service arguments
    models_folder = args.models_folder
    model_id = args.model_id
    resources_folder = args.resources_folder
    resource_id = args.resource_id
    cases_folder = args.cases_folder
    case_id = args.case_id
    case_file_format = args.case_file_format
    is_label_export = args.is_label_export
    is_database_export = args.is_database_export

    # create path variables from arguments
    models_path = Path(models_folder)
    resource_path = Path(resources_folder) / resource_id

    if case_id is not None:
        case_path_folder = Path(cases_folder) / case_id
        case_path_folder.mkdir(parents=True, exist_ok=True)
    else:
        case_path_folder = Path(cases_folder)

    try:
        # STEP02: Loading predictor model and labels if exist
        _logger.info("STEP02: Loading predictor model")
        predictor_model = load_model(models_path, model_id['path'])

        predictor_labels = None
        if is_label_export == True:
            predictor_labels = load_labels(models_path, model_id['path'])

        # STEP03: get predictions from resource id
        _logger.info(f"STEP03: Get predictions from model type {model_id['key']}")
        
        predictions = predict_by_resource([model_id['segment_body']], resource_path, predictor_model, predictor_labels)

        _logger.info(f"Prediction for a total of: {str(len(predictions))} items")

        # STEP04: save resource predictions in host or return the dataframe to be used by job
        if is_database_export == False:
            if case_file_format == "npz":
                case_file_path = case_path_folder / "prediction.npz"

                np.savez_compressed(
                    case_file_path, 
                    timestamp=predictions[:,0], 
                    label=predictions[:,1]
                )
            else:
                case_file_path = case_path_folder / "prediction.csv"

                df = pd.DataFrame({
                    'timestamp': predictions[:,0],
                    'label': predictions[:,1]
                })

                df.to_csv(case_file_path, index=False)

            _logger.info(f"Host saved prediction successfully for model id: {model_id} at: {case_file_path.name}")
            _logger.info("Predictor finalized")            
        else:
            df = pd.DataFrame({
                'timestamp': predictions[:,0],
                'label': predictions[:,1]
            })
                    
            _logger.info(f"Return prediction successfully for model id: {model_id}")
            _logger.info("Predictor finalized")

            return df
    except Exception as e:
        _logger.error(f"An error occurred: {e}")

        raise e        

def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])

if __name__ == "__main__":
    run()        