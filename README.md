# Email Ham and Spam Prediction

This project is an email classification system built using **Logistic Regression** and **TF-IDF Vectorizer**. The trained model is deployed via a **Gradio** web interface, allowing users to input an email and receive a prediction of **Ham** (legitimate) or **Spam**.

---

## Project Development

The project was developed in two main stages:

1. **Model Training**  
   - A dataset of emails labeled as Ham or Spam was used to train a **Logistic Regression** classifier.  
   - Text preprocessing included lowercase conversion, removal of special characters, and tokenization.  
   - **TF-IDF Vectorizer** was used to convert text into numerical feature vectors.  
   - After training, the model and vectorizer were saved using `joblib` for reuse.

2. **Application Development**  
   - A Gradio-based web application was created to load the trained model and vectorizer.  
   - The app accepts user input (email text), preprocesses it, and passes it to the model.  
   - The predicted class (**Ham** or **Spam**) is displayed on the web interface.

---

## How the Project Runs

1. The application starts by loading the trained **Logistic Regression** and the **TF-IDF Vectorizer** model (`spam_detector_lr.pkl`).  
2. A user inputs an email message through the web interface.  
3. The text is cleaned and transformed into TF-IDF features.  
4. The Logistic Regression model predicts whether the email is **Ham** or **Spam**.  
5. The prediction is displayed to the user in real time.

---

