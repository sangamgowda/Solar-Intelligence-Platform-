import joblib
import os

MODELS_DIR = r"c:\Users\sanga\OneDrive\Desktop\Projects2.0\ML_and_DL_modeled_application\backend\models"

def check_model(name):
    path = os.path.join(MODELS_DIR, name)
    try:
        model = joblib.load(path)
        print(f"Model: {name}")
        if hasattr(model, 'n_features_in_'):
            print(f"  n_features_in_: {model.n_features_in_}")
        elif hasattr(model, 'n_features_'):
            print(f"  n_features_: {model.n_features_}")
        elif hasattr(model, 'feature_name'):
            print(f"  feature_name length: {len(model.feature_name())}")
            # print(f"  feature_name: {model.feature_name()}")
        else:
            print("  Could not determine number of features")
    except Exception as e:
        print(f"Error loading {name}: {e}")

models = ["Tirchy_ML_model.pkl", "Tirchy_ML_model copy.pkl", "Bangalore_ML_model.pkl"]
for m in models:
    check_model(m)

features_path = os.path.join(MODELS_DIR, "features.pkl")
features = joblib.load(features_path)
print(f"\nFeatures in features.pkl: {len(features['features'])}")
