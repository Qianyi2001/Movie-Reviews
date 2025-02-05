from Helper import mysqlHelper
from logger import log_message

import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
import string
import matplotlib.pyplot as plt
from wordcloud import WordCloud

stop_words = set(stopwords.words('english'))

# add custom stopwords for movie
custom_stopwords = {
    "movie", "film", "story", "character", "scene", "watch", "seen",
    "plot", "acting", "director", "performance", "cinema", "like",
    "good", "bad", "great", "one", "really", "well", "time"
}
stop_words.update(custom_stopwords)


def clean_text(text):
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = text.lower()  # Convert to lowercase
    words = text.split()
    words = [word for word in words if word not in stop_words]  # Remove stop words
    return ' '.join(words)


def load_and_preprocess_data():
    log_message("INFO", "Connecting to database and loading data.")
    db = mysqlHelper(
        host="localhost",
        port=3306,
        user="root",
        password="85581123xpi",
        database='imdb_top_movies'
    )

    db.connect()
    try:
        results = db.execute_query("SELECT * FROM movie_comment")
    except Exception as e:
        print(e)
    movie_comments = pd.DataFrame(results)
    movie_comments['cleaned_comment'] = movie_comments['comment_content'].apply(clean_text)

    try:
        results = db.execute_query("SELECT * FROM movies")
    except Exception as e:
        print(e)
    movies = pd.DataFrame(results)

    db.close()
    log_message("INFO", "Merging movie data and comments.")

    cleaned_movie_comments = movie_comments[['movie_id', 'cleaned_comment', 'time']]
    cleaned_movies = movies[['movie_id', 'title']]
    merge_data = pd.merge(cleaned_movies, cleaned_movie_comments, on='movie_id', how='left')

    return merge_data


def generate_wordclouds(merge_data):
    log_message("INFO", "Generating word clouds for movies.")

    unique_titles = merge_data['title'].unique()
    for title in unique_titles:
        comments = merge_data[merge_data['title'] == title]['cleaned_comment'].dropna()
        combined_text = ' '.join(comments)

        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(combined_text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=14, pad=20)
        plt.show()


def main():
    log_message("INFO", "Starting movie review analysis pipeline.")

    merge_data = load_and_preprocess_data()

    generate_wordclouds(merge_data)

    log_message("INFO", "Movie review analysis completed successfully.")


if __name__ == "__main__":
    main()
