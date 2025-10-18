import joblib
import os

def predict_message(message_text):
    """
    Loads the trained model and vectorizer, then predicts if a message is phishing.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, 'phishing_detector_model.pkl')
    vectorizer_path = os.path.join(script_dir, 'tfidf_vectorizer.pkl')

    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}. Please ensure train_model.py was run successfully.")
        return None
    if not os.path.exists(vectorizer_path):
        print(f"Error: Vectorizer file not found at {vectorizer_path}. Please ensure train_model.py was run successfully.")
        return None

    try:
        # Load the trained model and vectorizer
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)

        # Preprocess the message
        message_vectorized = vectorizer.transform([message_text])

        # Make a prediction
        prediction = model.predict(message_vectorized)
        prediction_proba = model.predict_proba(message_vectorized)

        label = "Phishing" if prediction[0] == 1 else "Legitimate"
        confidence = prediction_proba[0][prediction[0]] * 100

        print(f"\n--- Prediction Result ---")
        print(f"Message: \"{message_text}\"")
        print(f"Prediction: {label}")
        print(f"Confidence: {confidence:.2f}%")
        print(f"-------------------------")

        return label, confidence

    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        return None

if __name__ == "__main__":
    print("Welcome to the Phishing Detector!")
    print("Enter a message to check if it's phishing (type 'quit' to exit).")

    while True:
        user_input = input("\nEnter a message: ")
        if user_input.lower() == 'quit':
            break
        
        predict_message(user_input)

    print("Exiting Phishing Detector. Goodbye!")