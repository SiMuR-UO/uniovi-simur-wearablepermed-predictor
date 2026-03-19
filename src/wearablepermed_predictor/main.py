import os
import sys
import argparse
import logging
from pathlib import Path
import joblib
from pyaml_env import parse_config
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import predictor

__author__ = "Miguel Salinas Gancedo"
__copyright__ = "Miguel Salinas Gancedo"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def argument_spaces(arg):
    return arg.split(',')

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
        dest="resource_id",
        help="Resource Id"
    )
    parser.add_argument(
        "-model-id",
        "--model-id",
        dest="model_id",
        help="Model Id"
    )
    parser.add_argument(
        "-resource-file",
        "--resource-file",
        dest="resource_file",
        help="resource file [csv]"
    )    
    parser.add_argument(
        "-user-email",
        "--user-email",
        dest="user_email",
        help="User email"
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

def predict_by_mock(config, resource_file):
    # Create a list of mock Prediction objects
    mock_prediction = {}

    return mock_prediction

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

def predict_by_resource(resource_file, model_id):    
    predictions = predictor.predict(resource_file, model_id)

    return predictions

def send_email(args, config, resource_path, receiver_email):
    # SMTP server config
    smtp_host = config.host
    smtp_port = config.port
    sender_email = config.sender_email
    password = config.sender_password

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = config.subject

    # Email body
    body = f"<p>The predictions for your resource {args.resource_id} has been resolved</p>"
    msg.attach(MIMEText(body, "html"))

    try:
        # Connect to the server
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.send_message(msg)

        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        server.quit()

def main(args):
    # get arguments and configure app logger
    args = parse_args(args)
    setup_logging(args.loglevel)
    
    # STEP01: get predictions from resource id
    _logger.info("STEP01: Loading arguments")

    # get service arguments
    base_file = Path(__file__).resolve().parent.parent.parent
    model_id = args.model_id    
    resource_file = args.resource_file
    user_email = args.user_email

    # get job active profile            
    if not os.getenv('ARG_PYTHON_PROFILES_ACTIVE'):
        config = parse_config('./src/wearablepermed_predictor/environment/environment.yaml')        
    else:
        config = parse_config('./src/wearablepermed_predictor/environment/environment-' + os.getenv('ARG_PYTHON_PROFILES_ACTIVE') + '.yaml')

    # STEP02: Loading predictor model
    _logger.info("STEP02: Loading predictor model")
    predictor_model = load_model(model_id, base_file)

    # STEP03: get predictions from resource id
    _logger.info("STEP03: Get predictions from model id %s ", model_id)
    predictions = predict_by_resource(resource_file, predictor_model)

    #print(f"The predictions are: {predictions}")

    # STEP04: save resource predictions
    result_path = base_file / "results" / "predictions.json"

    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=4)

    print(f"File saved successfully at: {result_path.name}")

    # STEP05: send email to user
    if (user_email is not None):
        _logger.info("STEP05: Send email for user email %s ", user_email)
        send_email(args, config, resource_file, user_email)

        print(f"Email sent to: {user_email}")

    _logger.info("Predictor finalized")

def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])

if __name__ == "__main__":
    run()        