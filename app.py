# app.py

import re
import joblib
import gradio as gr

# ===============================
# 1. Load the trained model
# ===============================
model = joblib.load("spam_detector_lr.pkl")

# ===============================
# 2. Text cleaning function
# ===============================
def clean_text(text):
    """
    Basic preprocessing: lowercase, remove special chars, URLs, extra spaces.
    """
    text = text.lower()                          # lowercase
    text = re.sub(r'\n', ' ', text)             # remove line breaks
    text = re.sub(r'\s+', ' ', text)            # remove extra spaces
    text = re.sub(r'http\S+', '', text)         # remove URLs
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)  # remove special chars
    return text.strip()

# ===============================
# 3. Prediction function
# ===============================
def predict_email(email_text):
    """
    Predict whether an email is Spam or Ham.
    """
    cleaned_text = clean_text(email_text)
    pred = model.predict([cleaned_text])[0]
    return "Spam 🚨" if pred == 1 else "Ham ✅"

# ===============================
# 4. Gradio interface
# ===============================
demo = gr.Interface(
    fn=predict_email,
    inputs=gr.Textbox(lines=6, placeholder="Paste email text here..."),
    outputs="text",
    title="Email Spam Detection (Improved)",
    description="TF-IDF + Logistic Regression model for Spam vs Ham classification on 200k+ emails"
)

# Launch the app (Hugging Face automatically handles public URL)
demo.launch()
