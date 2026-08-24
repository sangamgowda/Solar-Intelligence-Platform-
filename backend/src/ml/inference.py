import os
import joblib
import numpy as np
import tensorflow as tf

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(APP_DIR, "models")

LSTM_MODEL_PATH = os.path.join(MODELS_DIR, "Tirchy_LSTM_model_nolag.h5")
X_SCALER_PATH = os.path.join(MODELS_DIR, "X_scaler_lstm.pkl")
Y_SCALER_PATH = os.path.join(MODELS_DIR, "y_scaler_lstm.pkl")
LSTM_CONFIG_PATH = os.path.join(MODELS_DIR, "lstm_config.pkl")

LGBM_GHI_PATH = os.path.join(MODELS_DIR, "Tirchy_ML_model copy.pkl")
BIAS_INFO_PATH = os.path.join(MODELS_DIR, "bias_correction.pkl")
FEATURES_INFO_PATH = os.path.join(MODELS_DIR, "features.pkl")

# Global variables to hold loaded models
lstm_model = None
X_scaler = None
y_scaler = None
lstm_config = None
SEQ_LEN = None
HORIZON = None
LSTM_FEATURES = None

lgbm_ghi_model = None
lgbm_bias_info = None
lgbm_features_info = None
lgbm_features = None

def load_models():
    global lstm_model, X_scaler, y_scaler, lstm_config, SEQ_LEN, HORIZON, LSTM_FEATURES
    global lgbm_ghi_model, lgbm_bias_info, lgbm_features_info, lgbm_features
    
    if lstm_model is None:
        lstm_model = tf.keras.models.load_model(LSTM_MODEL_PATH, compile=False)
        X_scaler = joblib.load(X_SCALER_PATH)
        y_scaler = joblib.load(Y_SCALER_PATH)
        lstm_config = joblib.load(LSTM_CONFIG_PATH)
        SEQ_LEN = lstm_config['SEQ_LEN']
        HORIZON = lstm_config['HORIZON']
        LSTM_FEATURES = lstm_config['features']

        lgbm_ghi_model = joblib.load(LGBM_GHI_PATH)
        lgbm_bias_info = joblib.load(BIAS_INFO_PATH)
        lgbm_features_info = joblib.load(FEATURES_INFO_PATH)
        lgbm_features = lgbm_features_info['features']

def predict_lstm_sequence(df):
    load_models()
    X_scaled = X_scaler.transform(df[LSTM_FEATURES])
    X_seq = X_scaled[-SEQ_LEN - HORIZON : -HORIZON].reshape(1, SEQ_LEN, len(LSTM_FEATURES))
    y_pred_scaled = lstm_model.predict(X_seq, verbose=0).reshape(-1, 1)
    y_pred = y_scaler.inverse_transform(y_pred_scaled).flatten()
    return np.maximum(y_pred, 0)

def predict_lgbm_sequence(df_target):
    load_models()
    predictions = lgbm_ghi_model.predict(df_target[lgbm_features])
    return np.maximum(predictions + lgbm_bias_info['validation_bias'], 0)
