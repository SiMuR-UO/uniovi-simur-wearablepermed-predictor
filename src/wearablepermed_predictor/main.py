from enum import Enum
import os
import sys
import argparse
import logging
import joblib
from tensorflow import keras
import numpy as np
import pandas as pd
from pathlib import Path
from huggingface_hub import HfApi

from wearablepermed_predictor.core.enum import ML_Model, Channel, Segment_Body, Class_Type
from wearablepermed_predictor.core import predictor_characteristics, predictor_convolutional

__author__ = "Miguel Angel Salinas Gancedo<uo34525@uniovi.es>, Antonio Miguel López Rodriguez<amlopez@uniovi.es>"
__copyright__ = "Uniovi"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

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
        '-organization-id',
        '--organization-id',
        default="simuruo",
        dest="organization_id",        
        help="The organization Id."
    )
    parser.add_argument(
        '-model-file',
        '--model-file',
        dest="model_file",        
        help="The custom model file."
    )
    parser.add_argument(
        '-label-file',
        '--label-file',
        dest="label_file",        
        help="The custom label file."
    )         
    parser.add_argument(
        '-model-type',
        '--model-type',
        required=True,
        dest="model_type",    
        choices=[m.name for m in ML_Model],        
        help=f"The Model Type. Choose from: {', '.join([m.name for m in ML_Model])}"        
    )
    parser.add_argument(
        '-sensor-channel',
        '--sensor-channel',
        dest="sensor_channel",    
        choices=[m.name for m in Channel],        
        help=f"The Sensor Channels. Choose from: {', '.join([m.name for m in Channel])}"        
    )
    parser.add_argument(
        '-segment-body',
        '--segment-body',
        required=True,
        dest="segment_body",    
        choices=[m.name for m in Segment_Body],        
        help=f"The Segment Body. Choose from: {', '.join([m.name for m in Segment_Body])}"        
    )
    parser.add_argument(
        '-class-type',
        '--class-type',
        dest="class_type",    
        choices=[m.name for m in Class_Type],        
        help=f"The Class Type. Choose from: {', '.join([m.name for m in Class_Type])}"        
    )                    
    parser.add_argument(
        '-models-folder',
        '--models-folder',
        dest="models_folder",        
        help="The root models folder."
    )
    parser.add_argument(
        '-resources-folder',
        '--resources-folder',
        required=True,
        dest="resources_folder",        
        help="The root resourcers folder."
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

def set_model_id(model_type, sensor_channel, segment_body, class_type):
    # Model id policy name
    return model_type + "_" + sensor_channel + "_" + segment_body + "_" + class_type

def get_hf_model_id(author, model_type, sensor_channel, segment_body, class_type):
    api = HfApi()

    # construct the filter for Hugging Face
    filter = model_type + "," + sensor_channel + "," + segment_body + "," + class_type

    models = list(api.list_models(author=author, filter=filter))

    if len(models) == 0:
        raise Exception("Any model exist for these arguments")

    for model in models:
        model_id = model.id  # e.g. "simuruo/some-model-name"
        break

    return model_id

def load_model(model_type, model_file):
    if os.path.exists(model_file):
        if (ML_Model.randomforest.name == model_type or ML_Model.xgboost.name == model_type):
            model = joblib.load(model_file)
        else:
            model = keras.models.load_model(model_file)

        return model
    else:
        _logger.error(f"Model not found for type {model_file}.")

        raise Exception(f"Model not found for type {model_file}.")        

def load_labels(label_file):
    if os.path.exists(label_file):
        label = joblib.load(label_file)

        return label
    else:
        _logger.error(f"Labels not found for type {label_file}.")

        raise Exception(f"Labels not found for type {label_file}.")

def predict_by_resource(segment_body, resource_id, model_type, model_id, sensor_channel, predictor_label_encoder): 
    # the utils package use capitalize segment bodies
    segment_body_capitalized = [s.capitalize() for s in segment_body]

    if (ML_Model.randomforest.name == model_type or ML_Model.xgboost.name == model_type):
        predictions = predictor_characteristics.predict(segment_body_capitalized, resource_id, model_type, model_id, sensor_channel, predictor_label_encoder)
    else:
        predictions = predictor_convolutional.predict(segment_body_capitalized, resource_id, model_id, sensor_channel, predictor_label_encoder)

    return predictions

def main(args):
    # get arguments and configure app logger
    args = parse_args(args)
    setup_logging(args.loglevel)
    
    # get service arguments
    # model arguments
    organization_id = args.organization_id
    models_folder = args.models_folder
    model_type = args.model_type
    sensor_channel = args.sensor_channel
    segment_body = args.segment_body
    class_type = args.class_type    
    model_id = set_model_id(model_type, sensor_channel, segment_body, class_type)

    # resource arguments
    resources_folder = args.resources_folder
    resource_id = args.resource_id

    # case result arguments
    cases_folder = args.cases_folder
    case_id = args.case_id
    case_file_format = args.case_file_format    
    is_label_export = args.is_label_export
    is_database_export = args.is_database_export

    # STEP01: get resources from arguments
    _logger.info("STEP01: Loading resource arguments")

    # get model from Huggin Face or from local configuration
    if model_type is not None:
        # only Random Forest is just implemented
        #if model_type != "randomforest":
        #    raise Exception("Only Ranbdom Forest is implemented")            

        # create folder is not exist and get fix model id from huggingface
        models_folder = Path(__file__).resolve().parent.parent.parent / 'models' / model_id
        models_folder.mkdir(parents=True, exist_ok=True)
        _logger.info(f"Creating models folder in: {str(models_folder)}")

        if ML_Model.randomforest.name == model_type:
            model_file = models_folder / 'RandomForest_1.pkl'
            label_file = models_folder / 'label_encoder.pkl'
        elif ML_Model.xgboost.name == model_type:            
            model_file = models_folder / 'XGBoost.pkl'
            label_file = models_folder / 'label_encoder.pkl'
        elif ML_Model.capture24.name == model_type:            
            model_file = models_folder / 'CAPTURE24.h5'
            label_file = models_folder / 'label_encoder.pkl'
        else:            
            model_file = models_folder / 'ESANN.h5'
            label_file = models_folder / 'label_encoder.pkl'

        model_id = get_hf_model_id(organization_id, model_type, sensor_channel, segment_body, class_type)

        if model_id is None:
            raise Exception("Model Id not exist for this arguments")
        
        # download model id from hf
        HfApi().snapshot_download(
            repo_id=model_id,
            repo_type="model",
            local_dir=str(models_folder))
    else:
        # define custom model id locally
        model_file = Path(model_file)
        label_file = Path(label_file)

    resource_path = Path(resources_folder) / resource_id

    if cases_folder is not None:
        if case_id is not None:
            case_path_folder = Path(cases_folder) / case_id
            case_path_folder.mkdir(parents=True, exist_ok=True)
        else:
            case_path_folder = Path(cases_folder)

    try:
        # STEP02: Loading predictor model and labels if exist
        _logger.info("STEP02: Loading predictor model")
        model_predictor = load_model(model_type, model_file)

        model_labels = None
        if is_label_export == True:
            model_labels = load_labels(label_file)

        # STEP03: get predictions from resource id
        _logger.info(f"STEP03: Get predictions from model type {model_id}")
        
        predictions = predict_by_resource([segment_body], resource_path, model_type, model_predictor, sensor_channel, model_labels)

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