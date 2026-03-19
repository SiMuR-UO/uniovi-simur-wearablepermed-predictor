import logging

from wearablepermed_utils.core import load_WPM_data, apply_windowing_WPM_segmented_data_predictor, extract_features

_logger = logging.getLogger(__name__)

def predict(resource_file, predictor_model, predictor_label_encoder=None):
    try:
        # 1 Load IMU data based on the segment
        data_imu = load_WPM_data(resource_file, "Wrist")

        # 2 Enventanar series temporales (y realizar extracción de características)
        activity_data = data_imu[:,1:7]
        window_size_samples = 250
        window_overlapping_percent = 50
        windowed_data = apply_windowing_WPM_segmented_data_predictor(activity_data, window_size_samples, window_overlapping_percent)

        # 3 Extract features from windowed dataset
        extract_features_data = extract_features(windowed_data)
        print(extract_features_data.shape)
        
        # 4 calculate predictions. We can obtain the number or labels
        predictions = predictor_model.predict(extract_features_data)

        if predictor_label_encoder is not None:
            predictions = predictor_label_encoder.inverse_transform(predictions.astype(int))

        return predictions
    except Exception as e:
        _logger.error(f"An error occurred: {e}")

    return []  