# src/utils.py

import joblib
import numpy as np

# Load model once
model = joblib.load("crop_model.pkl")

def predict_crop(n, p, k, temp, humidity, ph, rainfall):
    data = np.array([[n, p, k, temp, humidity, ph, rainfall]])
    prediction = model.predict(data)
    return prediction[0]
