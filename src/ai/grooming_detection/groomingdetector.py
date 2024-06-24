import html
import os
import pickle
import re
import ssl
import nltk
from nltk import WordNetLemmatizer

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download("wordnet")
wnl = WordNetLemmatizer()
tf_idf_dir = os.path.join(os.path.dirname(__file__), 'models', 'tf_idf_vectoriser.pk')
lr_dir = os.path.join(os.path.dirname(__file__), 'models', 'lr_model.pk')


# Load the fitted TF-IDF vectoriser
with open(tf_idf_dir, "rb") as f:
    tfidf_vectoriser = pickle.load(f)

# Load the trained Logistic Regression model
with open(lr_dir, "rb") as f:
    lr_model = pickle.load(f)


class GroomingDetector:
    """
    Class for predicting probability of grooming in text
    """

    __instance = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(GroomingDetector, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

    @staticmethod
    def clean_text(text):
        """
        Performs small amount of data cleaning while preserving potentially important features
        :param text:
        :return:
        """
        # Convert HTML characters to ASCII
        text = html.unescape(text)
        # Lemmatise
        text = wnl.lemmatize(text)
        # Remove any non-ASCII characters
        text = ''.join([i if ord(i) < 128 else ' ' for i in text])
        # Remove trailing whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @staticmethod
    def vectorise(cleaned_text):
        """
        Uses saved TF-IDF vectoriser to vectoriser the cleaned text
        :param cleaned_text:
        :return:
        """
        tfidf_vectorised_text = tfidf_vectoriser.transform(cleaned_text)
        return tfidf_vectorised_text

    @staticmethod
    def predict_grooming(tfidf_vectorised_text):
        probability = lr_model.predict_proba(tfidf_vectorised_text)[0][1]
        predicted_class = lr_model.predict(tfidf_vectorised_text)
        return predicted_class, probability

    def detect_grooming(self, raw_text):
        cleaned_text = [self.clean_text(raw_text)]
        vectorised_text = self.vectorise(cleaned_text)
        predicted_class, probability = self.predict_grooming(vectorised_text)
        if predicted_class == 1:
            return f"GROOMING DETECTED: '{raw_text}' with probability {probability:.3f} "
        else:
            return None


# print(GroomingDetector().detect_grooming("dont u have school 2mor?"))
