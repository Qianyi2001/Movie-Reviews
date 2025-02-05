from Helper import mysqlHelper
from logger import log_message

import pandas as pd
import re
import nltk
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.sentiment import SentimentIntensityAnalyzer
import string

# Load stopwords and stemmer
nltk.download('stopwords')
nltk.download('vader_lexicon')

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
sia = SentimentIntensityAnalyzer()


def clean_text(text):
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    words = text.split()
    words = [stemmer.stem(word) for word in words if word not in stop_words]  # Remove stop words and apply stemming
    return ' '.join(words)


def get_sentiment(text):
    score = sia.polarity_scores(text)['compound']  # Using Compound Score
    if score >= 0.05:
        return 0  # Positive
    elif score <= -0.05:
        return 1  # Negative
    else:
        return 2  # Neutral


def load_and_preprocess_data():
    db = mysqlHelper(
        host="localhost",
        port=3306,
        user="root",
        password="85581123xpi",
        database='imdb_top_movies'
    )

    db.connect()
    query = "SELECT * FROM movie_comment"
    try:
        results = db.execute_query(query)
    except Exception as e:
        print(e)
    db.close()

    movie_comments = pd.DataFrame(results)

    log_message("INFO", "Loading movie comments dataset.")
    df = movie_comments[['comment_content']].copy()

    log_message("INFO", "Starting text preprocessing.")
    df['cleaned_comment'] = df['comment_content'].apply(clean_text)

    log_message("INFO", "Applying VADER sentiment classification.")
    df['sentiment'] = df['cleaned_comment'].apply(get_sentiment)

    # Filter out neutral comments
    df = df[df['sentiment'] != 2]
    log_message("INFO", f"Filtered dataset contains {len(df)} non-neutral comments.")

    return df


def train_and_evaluate_models(df):
    log_message("INFO", "Splitting data into training and testing sets.")
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_comment'], df['sentiment'], test_size=0.2, random_state=690
    )

    # Apply TF-IDF vectorization
    log_message("INFO", "Applying TF-IDF vectorization.")
    vectorizer = TfidfVectorizer(max_features=10000)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    neg, pos = y_train.value_counts()
    models = {
        "Naive Bayes": MultinomialNB(class_prior=[neg / len(y_train), pos / len(y_train)]),
        "XGBoost": XGBClassifier(n_estimators=100, random_state=690, eval_metric="logloss", scale_pos_weight=neg / pos)
    }

    results = []
    for name, model in models.items():
        log_message("INFO", f"Training model: {name}")
        model.fit(X_train_tfidf, y_train)

        # Predict and evaluate
        y_pred = model.predict(X_test_tfidf)
        acc = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        log_message("INFO",
                    f"Model {name} - Accuracy: {acc:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1-Score: {f1:.4f}")
        results.append([name, acc, precision, recall, f1])

    return pd.DataFrame(results, columns=["Model", "Accuracy", "Precision", "Recall", "F1-Score"])


def main():
    df = load_and_preprocess_data()

    # Train and evaluate models
    results_df = train_and_evaluate_models(df)

    log_message("INFO", "Sentiment analysis and model comparison completed successfully.")


if __name__ == "__main__":
    main()
