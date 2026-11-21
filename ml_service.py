"""Local ML model: TF-IDF + Logistic Regression trained on data/training_messages.csv."""
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "training_messages.csv"
SAFE_LABEL = "Safe"


def train_model() -> Pipeline:
    df = pd.read_csv(DATA_PATH)
    model = Pipeline([
        # char n-grams handle Taglish/Bisaya spelling variations and typos better than words only
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5),
                                  lowercase=True, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, C=10, class_weight="balanced")),
    ])
    model.fit(df["message"], df["label"])
    return model


def predict(model: Pipeline, text: str) -> dict:
    """Return the predicted category and the probability that the text is a scam."""
    probs = model.predict_proba([text])[0]
    classes = list(model.classes_)
    best = classes[int(probs.argmax())]
    p_safe = float(probs[classes.index(SAFE_LABEL)])
    return {
        "category": best,
        "scam_probability": round((1 - p_safe) * 100),
        "confidence": round(float(probs.max()) * 100),
    }
