import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

print(f"DEBUG: Script is running from: {os.path.abspath(os.path.dirname(__file__))}")

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, "phishing_dataset.csv")

# --- 1. Load the Dataset ---
print(f"DEBUG: Attempting to load dataset from: {dataset_path}")
if not os.path.exists(dataset_path):
    print(f"Error: Dataset not found at {dataset_path}. Please run create_csv.py first.")
    exit()

try:
    df = pd.read_csv(dataset_path)
    print(f"DEBUG: File size of '{os.path.basename(dataset_path)}': {os.path.getsize(dataset_path)} bytes")
except Exception as e:
    print(f"Error loading CSV file: {e}")
    exit()

# Check if the DataFrame has the expected columns
if 'message' not in df.columns or 'label' not in df.columns:
    print("Error: CSV must contain 'message' and 'label' columns.")
    exit()

# Display class distribution (important for imbalanced datasets)
print("\nClass distribution in full dataset (as read by pandas):")
print(df['label'].value_counts())

# --- 2. Prepare Data for Training ---
X = df['message']
y = df['label']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

print("\nClass distribution in training set:")
print(y_train.value_counts())
print("\nClass distribution in test set:")
print(y_test.value_counts())

# --- 3. Feature Engineering (TF-IDF) ---
vectorizer = TfidfVectorizer(max_features=5000) # Limit features to 5000 for efficiency
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# --- 4. Train the Model (Logistic Regression) ---
model = LogisticRegression(max_iter=1000) # Increase max_iter for convergence
model.fit(X_train_vectorized, y_train)

# --- 5. Evaluate the Model ---
y_pred = model.predict(X_test_vectorized)

print("\n🧪 Evaluation Metrics:")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
# Add target_names for better readability of the report
print(classification_report(y_test, y_pred, target_names=['Legitimate (0)', 'Phishing (1)']))

# --- 6. Save the Trained Model and Vectorizer ---
model_path = os.path.join(script_dir, 'phishing_detector_model.pkl')
vectorizer_path = os.path.join(script_dir, 'tfidf_vectorizer.pkl')

joblib.dump(model, model_path)
joblib.dump(vectorizer, vectorizer_path)

print("✅ Model and vectorizer saved successfully.")
print(f"DEBUG: Model file saved to: {model_path}")
print(f"DEBUG: Vectorizer file saved to: {vectorizer_path}")
print(f"DEBUG: Model file size: {os.path.getsize(model_path)} bytes")
print(f"DEBUG: Vectorizer file size: {os.path.getsize(vectorizer_path)} bytes")

print("\nYou can now run 'python predict_phishing.py'")