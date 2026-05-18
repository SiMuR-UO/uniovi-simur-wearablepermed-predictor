import logging
import numpy as np
import xgboost as xgb

from wearablepermed_predictor.core.enum import ML_Model, Channel, Segment_Body, Class_Type
from wearablepermed_utils.core import load_WPM_data, apply_windowing_WPM_segmented_data_predictor, extract_features

_logger = logging.getLogger(__name__)

WINDOW_SIZE = 250
WINDOW_OVERLAPPING = 0.5

def predict(segment_body, resource_id_file, model_type, model_id, predictor_label_encoder=None):
    try:
        # 1 Load IMU data based on the segment (csv files)
        data_imu = load_WPM_data(resource_id_file, segment_body[0])

        _logger.info(f"Resource id {resource_id_file} for segment body {segment_body[0]} loaded")

        # 2 windowed temporal series
        activity_data = data_imu[:,1:7]
        activity_timestamp = data_imu[:,0]

        window_size_samples = 250
        window_overlapping_percent = 50
        windowed_data = apply_windowing_WPM_segmented_data_predictor(activity_data, window_size_samples, window_overlapping_percent)

        _logger.info(f"Resource id {resource_id_file} windowed")

        # 3 extract characteristics from windows data
        extract_features_data = extract_features(windowed_data)
        _logger.info(f"Shape extract features: {extract_features_data.shape}.")
        
        # 4 calculate predictions. We can obtain the number or labels and get with the first timestamp for each window
        if ML_Model.xgboost.name == model_type:            
            extract_features_data_dmatrix = xgb.DMatrix(extract_features_data)
            predictions = model_id.predict(extract_features_data_dmatrix)
        else:
            predictions = model_id.predict(extract_features_data).astype(int) #TODO [Check astype to remove]

        _logger.info(f"Resource id {resource_id_file} predicted")

        # 5 expand classification to cover all values followinf the pattern: "Winner Takes All"
        # Create an empty array for the full results
        total_samples = activity_data.shape[0]
        step = int(WINDOW_SIZE * WINDOW_OVERLAPPING)

        full_predictions = np.full(total_samples, -1, dtype=np.int8)

        # Loop through and fill the full array
        for index, prediction in enumerate(predictions):
            start = index * step
            end = start + WINDOW_SIZE
            
            # Ensure we don't go out of bounds at the very end
            if end > total_samples:
                end = total_samples

            # Check to ensure start doesn't exceed total_samples
            if start >= total_samples:
                break                

            full_predictions[start:end] = np.argmax(prediction)

        # the last items not expandes set the last prediction for each ones
        full_predictions[full_predictions == -1] = np.argmax(predictions[-1])

        # 6 substitute the numeric label values for strings if you pass this relation
        if predictor_label_encoder is not None:
            full_predictions = predictor_label_encoder.inverse_transform(full_predictions)

        combined_data = np.column_stack((activity_timestamp, full_predictions))

        _logger.info(f"Resource id {resource_id_file} predictions timestamp expanded")

        return combined_data
    except Exception as e:
        _logger.error(f"An error occurred: {e}")

        raise e