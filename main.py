from driver import init_webdriver
from scraper import scrape_comments
from logger import log_message
from Helper import save_reviews_to_db, mysqlHelper

def main():
    log_message("INFO", "Starting the review scraper...")

    # ---------- 1. Connect to DB ----------
    log_message("INFO", "Connecting to the database...")
    db = mysqlHelper(
        host="localhost",
        port=3306,
        user="root",
        password="85581123xpi",
        database='imdb_top_movies'
    )
    db.connect()
    log_message("INFO", "Database connection established.")

    # ---------- 2. Fetch movie IDs ----------
    query = "SELECT movie_id FROM imdb_top_movies.movies"
    try:
        movie_ids = [row['movie_id'] for row in db.execute_query(query)]
        log_message("INFO", f"Retrieved {len(movie_ids)} movie IDs from the database.")
    except Exception as e:
        log_message("ERROR", f"Failed to fetch movie IDs: {e}")
        db.close()
        return

    # ---------- 3. Initialize WebDriver ----------
    driver = init_webdriver(chromedriver_path='chromedriver.exe', headless=False)
    log_message("INFO", "WebDriver initialized.")

    # ---------- 4. Scrape reviews ----------
    all_reviews = []
    for movie_id in movie_ids:
        log_message("INFO", f"Scraping reviews for movie_id: {movie_id}")
        reviews_data = scrape_comments(driver, movie_id)

        if reviews_data:
            all_reviews.extend(reviews_data)
            log_message("INFO", f"Collected {len(reviews_data)} reviews for movie_id {movie_id}.")
        else:
            log_message("WARNING", f"No reviews found for movie_id {movie_id}.")

    # ---------- Save all reviews to the database ----------
    if all_reviews:
        log_message("INFO", f"Saving {len(all_reviews)} reviews to the database...")
        save_reviews_to_db(db, all_reviews)
        log_message("INFO", f"Successfully saved {len(all_reviews)} reviews to the database.")
    else:
        log_message("WARNING", "No reviews collected. Nothing to save.")

    # ---------- 5. Quit ----------
    driver.quit()
    db.close()
    log_message("INFO", "Review scraper completed successfully.")

if __name__ == "__main__":
    main()
