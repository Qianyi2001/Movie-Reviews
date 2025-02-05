import time
from selenium.webdriver.common.by import By
from logger import log_message
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_top_movie_urls(driver, url, top_n=100):
    log_message("INFO", "Fetching movie URLs...")
    driver.get(url)

    movie_url_elements = driver.find_elements(
        By.XPATH, '//*[@id="__next"]/main/div/div[3]/section/div/div[2]/div/ul/li/div[2]/div/div/div[1]/a'
    )

    top_movie_urls = [{
            "ranking": idx + 1,
            "movie_url": elem.get_attribute('href')}
        for idx, elem in enumerate(movie_url_elements[:top_n])]

    log_message("INFO", f"Found {len(top_movie_urls)} movie URLs.")
    return top_movie_urls

def parse_movie_page(driver, movie_info):
    ranking = movie_info["ranking"]
    movie_url = movie_info["movie_url"]
    driver.get(movie_url)
    time.sleep(1)

    try:
        # ---------- 1. movie basic info ----------
        title = driver.find_element(
            By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/h1/span'
        ).text.strip()

        release_year = driver.find_element(
            By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[1]/a'
        ).text.strip()

        movie_classification = driver.find_element(
            By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[2]'
        ).text.strip()

        length = driver.find_element(
            By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul/li[3]'
        ).text.strip()

        rating_element = driver.find_element(
            By.XPATH,
            '/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/'
            'div[3]/div[2]/div[2]/div[1]/div/div[1]/a/span/div/div[2]/div[1]'
        )
        rating = driver.execute_script("return arguments[0].textContent;", rating_element).split('/')[0]

        user_reviews = driver.find_element(
            By.XPATH,
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/'
            'div[3]/div[2]/div[2]/ul/li[1]/a/span/span[1]'
        ).text.strip()

        critic_reviews = driver.find_element(
            By.XPATH,
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/'
            'div[3]/div[2]/div[2]/ul/li[2]/a/span/span[1]'
        ).text.strip()

        meta_score = driver.find_element(
            By.XPATH,
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/'
            'div[3]/div[2]/div[2]/ul/li[3]/a/span/span[1]/span'
        ).text.strip()

        # ---------- 2. movie people info ----------
        directors_list = driver.find_elements(
            By.XPATH,
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/'
            'div[3]/div[2]/div[2]/div[2]/div/ul/li[1]/div/ul/li/a'
        )
        director_names = [
            driver.execute_script("return arguments[0].textContent;", item).strip()
            for item in directors_list
        ]
        director_ids = [
            item.get_attribute('href').split('/name/')[1].split('/')[0]
            for item in directors_list
        ]

        writers_list = driver.find_elements(
            By.XPATH,
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/'
            'div[3]/div[2]/div[2]/div[2]/div/ul/li[2]/div/ul/li/a'
        )
        writer_names = [
            driver.execute_script("return arguments[0].textContent;", item).strip()
            for item in writers_list
        ]
        writer_ids = [
            item.get_attribute('href').split('/name/')[1].split('/')[0]
            for item in writers_list
        ]

        stars_list = driver.find_elements(
            By.XPATH,
            '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/'
            'div[3]/div[2]/div[2]/div[2]/div/ul/li[3]/div/ul/li/a'
        )
        star_names = [
            driver.execute_script("return arguments[0].textContent;", item).strip()
            for item in stars_list
        ]
        star_ids = [
            item.get_attribute('href').split('/name/')[1].split('/')[0]
            for item in stars_list
        ]

        # ---------- 3. combine movie basic info ----------
        movie_id = movie_url.split('/title/')[1].split('/')[0]
        movie_dict = {
            "movie_id": movie_id,
            "ranking": ranking,
            "title": title,
            "release_year": release_year,
            "movie_classification": movie_classification,
            "length": length,
            "imdb_rating": rating,
            "user_reviews": user_reviews,
            "critic_reviews": critic_reviews,
            "meta_score": meta_score,
            "movie_url": movie_url
        }

        # ---------- 4. combine people info ----------
        people_list_temp = []
        movie_people_list_temp = []

        for role, people_ids, people_names in [
            ("director", director_ids, director_names),
            ("writer", writer_ids, writer_names),
            ("star", star_ids, star_names)
        ]:
            for person_id, person_name in zip(people_ids, people_names):
                people_list_temp.append({
                    "person_id": person_id,
                    "name": person_name
                })
                movie_people_list_temp.append({
                    "movie_id": movie_id,
                    "person_id": person_id,
                    "role": role
                })

        log_message("INFO", f"Successfully processed movie ranking {ranking}: {title}")

        return movie_dict, people_list_temp, movie_people_list_temp

    except Exception as e:
        log_message("ERROR", f"Failed to process movie ranking {ranking}: {e}")
        return None, [], []


def scrape_comments(driver, movie_id):
    url = f'https://www.imdb.com/title/{movie_id}/reviews/?ref_=tt_ururv_sm'
    driver.get(url)

    # 点击“Show more 25”按钮 10 次
    for i in range(10):
        try:
            expand_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="__next"]/main/div/section/div/section/div/div[1]/section[1]/div[3]/div/span[1]/button/span/span')
                )
            )
            driver.execute_script("arguments[0].click();", expand_button)
            time.sleep(1)
        except Exception as e:
            log_message("ERROR", f"Error clicking 'Show more 25' button on attempt {i+1}: {e}")
            break

    review_elements = driver.find_elements(By.CLASS_NAME, 'user-review-item')
    log_message("INFO", f"Found {len(review_elements)} review elements on the page")

    reviews = []
    for review in review_elements:
        try:
            user_name_element = review.find_elements(By.CLASS_NAME, 'ipc-link--base')
            comment_title_element = review.find_elements(By.CLASS_NAME, 'ipc-title__text')
            review_time_element = review.find_elements(By.CLASS_NAME, 'review-date')
            comment_content_element = review.find_elements(By.CLASS_NAME, 'ipc-html-content-inner-div')

            if user_name_element and comment_title_element and review_time_element and comment_content_element:
                user_name = user_name_element[0].text.strip()
                comment_title = comment_title_element[0].text.strip()
                review_time = review_time_element[0].text.strip()
                comment_content = comment_content_element[0].text.strip()

                # Skip None content review
                if comment_content:
                    reviews.append({
                        "movie_id": movie_id,
                        "user_name": user_name,
                        "comment_title": comment_title,
                        "comment_content": comment_content,
                        "time": review_time
                    })

            # Get 100 reveiews and stop
            if len(reviews) >= 100:
                log_message("INFO", "Collected 100 reviews. Stopping.")
                break

        except Exception as e:
            log_message("ERROR", f"Error processing a review element: {e}")
            continue

    log_message("INFO", f"Total reviews collected: {len(reviews)}")
    return reviews