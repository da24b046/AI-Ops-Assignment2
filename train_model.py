import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


# Load the generated dataset
df = pd.read_csv("spam_dataset.csv")

# Create the ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("nb", MultinomialNB())
])

# Train the model
model.fit(df["text"], df["label"])

# Save the complete pipeline
joblib.dump(model, "model.joblib")

print("Model trained and saved as model.joblib")
