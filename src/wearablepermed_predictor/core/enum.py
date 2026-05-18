from enum import Enum

class ML_Model(Enum):
    esann = 'ESANN'
    capture24 = 'CAPTURE24'
    randomforest = 'Random Forest'
    xgboost = 'XGBoost'

class Channel(Enum):
    accelerometer = 'Accelerometer'
    accelerometer_gyroscope = 'Accelerometer,Gyroscope'

class Segment_Body(Enum):
    thigh = 'Thigh'
    wrist = 'Wrist'
    hip = 'Hip'

class Class_Type(Enum):
    classes_4 = '4 Classes'
    classes_15 = '15 Classes'