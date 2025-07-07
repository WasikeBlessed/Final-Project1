import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Load the dataset
df = pd.read_csv("Crop_recommendation.csv")  # Make sure this CSV is in the same folder

# Prepare data
X = df.drop("label", axis=1)
y = df["label"]

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model
with open("crop_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved as crop_model.pkl")
