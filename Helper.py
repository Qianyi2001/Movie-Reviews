import pymysql
import pandas as pd
from logger import log_message
class mysqlHelper:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
        except pymysql.MySQLError as e:
            raise Exception(f"Database connection failed: {e}")

    def close(self):
        if self.connection:
            self.connection.close()

    # For SELECT only
    def execute_query(self, query, params=None):
        try:
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except pymysql.MySQLError as e:
            raise Exception(f"Query execution failed: {e}")

    # For DML only
    def execute_non_query(self, query, params=None):
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(query, params)
                self.connection.commit()
                return affected_rows
        except pymysql.MySQLError as e:
            self.connection.rollback()
            raise Exception(f"Non-query execution failed: {e}")

    # Execute a query with multiple.
    def execute_many(self, query, param_list):
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.executemany(query, param_list)
                self.connection.commit()
                print(f"Executed {len(param_list)} statements successfully.")
                return affected_rows
        except pymysql.MySQLError as e:
            self.connection.rollback()
            raise Exception(f"Batch query execution failed: {e}")

def save_to_database(result):
    """
    一次性完成:
      1) 连接并创建数据库 'imdb_top_movies'（如果不存在）
      2) 基于当前时间戳创建 3 张表: movies_..., people_..., movie_people_...
      3) 分别插入 movies_list, people_list, movie_people_list 数据
      4) 查询并打印结果 (DataFrame)

    :param result: dict
                   {
                     "movies": [...],
                     "people": [...],
                     "movie_people": [...]
                   }
    """
    log_message("INFO", "Starting database operations...")

    # 1. 初始化 db 连接
    db = mysqlHelper(
        host="localhost",
        port=3306,
        user="root",
        password="85581123xpi",
        database=None  # 先连接到默认库，再手动创建/切换
    )
    db.connect()

    try:
        # 2. 创建数据库 (如果不存在) 并切换过去
        db.execute_non_query("CREATE DATABASE IF NOT EXISTS `imdb_top_movies`;")
        log_message("INFO", "Database 'imdb_top_movies' created or already exists.")
        db.execute_non_query("USE `imdb_top_movies`;")
        log_message("INFO", "Switched to database 'imdb_top_movies'.")

        # 3. 基于当前时间戳创建表名
        movies_table = f"movies"
        people_table = f"people"
        movie_people_table = f"movie_people"

        # 3.1 创建 movies_table
        create_movies_table = f"""
        CREATE TABLE IF NOT EXISTS `{movies_table}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            movie_id VARCHAR(50),
            ranking INT,
            title VARCHAR(255),
            release_year INT,
            movie_classification VARCHAR(50),
            length VARCHAR(50),
            imdb_rating FLOAT,
            user_reviews VARCHAR(50),
            critic_reviews VARCHAR(50),
            meta_score INT,
            movie_url TEXT
        );
        """
        db.execute_non_query(create_movies_table)
        log_message("INFO", f"Table '{movies_table}' created or already exists.")

        # 3.2 创建 people_table
        create_people_table = f"""
        CREATE TABLE IF NOT EXISTS `{people_table}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            person_id VARCHAR(50),
            name VARCHAR(255)
        );
        """
        db.execute_non_query(create_people_table)
        log_message("INFO", f"Table '{people_table}' created or already exists.")

        # 3.3 创建 movie_people_table
        create_movie_people_table = f"""
        CREATE TABLE IF NOT EXISTS `{movie_people_table}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            movie_id VARCHAR(50),
            person_id VARCHAR(50),
            role VARCHAR(50)
        );
        """
        db.execute_non_query(create_movie_people_table)
        log_message("INFO", f"Table '{movie_people_table}' created or already exists.")

        # 4. 分别插入数据
        movies_list = result.get("movies", [])
        people_list = result.get("people", [])
        movie_people_list = result.get("movie_people", [])

        # 4.1 插入 movies
        insert_movies_sql = f"""
        INSERT INTO `{movies_table}` (
            movie_id,
            ranking,
            title,
            release_year,
            movie_classification,
            length,
            imdb_rating,
            user_reviews,
            critic_reviews,
            meta_score,
            movie_url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # 将数据格式化成元组列表
        movies_data = []
        for m in movies_list:
            movies_data.append((
                m.get("movie_id"),
                m.get("ranking"),
                m.get("title"),
                int(m.get("release_year")),
                m.get("movie_classification"),
                m.get("length"),
                float(m.get("imdb_rating")),
                m.get("user_reviews"),
                m.get("critic_reviews"),
                m.get("meta_score"),
                m.get("movie_url")
            ))
        db.execute_many(insert_movies_sql, movies_data)
        log_message("INFO", f"Inserted {len(movies_data)} rows into '{movies_table}'.")

        # 4.2 插入 people
        insert_people_sql = f"""
        INSERT INTO `{people_table}` (
            person_id,
            name
        )
        VALUES (%s, %s)
        """
        people_data = [
            (p.get("person_id"), p.get("name")) for p in people_list
        ]
        db.execute_many(insert_people_sql, people_data)
        log_message("INFO", f"Inserted {len(people_data)} rows into '{people_table}'.")

        # 4.3 插入 movie_people
        insert_movie_people_sql = f"""
        INSERT INTO `{movie_people_table}` (
            movie_id,
            person_id,
            role
        )
        VALUES (%s, %s, %s)
        """
        movie_people_data = [
            (mp.get("movie_id"), mp.get("person_id"), mp.get("role"))
            for mp in movie_people_list
        ]
        db.execute_many(insert_movie_people_sql, movie_people_data)
        log_message("INFO", f"Inserted {len(movie_people_data)} rows into '{movie_people_table}'.")

        # 5. 查询并打印结果
        # 5.1 movies
        select_movies_sql = f"SELECT * FROM `{movies_table}`;"
        movies_query_result = db.execute_query(select_movies_sql)
        movies_columns = [
            "id",
            "movie_id",
            "ranking",
            "title",
            "release_year",
            "movie_classification",
            "length",
            "imdb_rating",
            "user_reviews",
            "critic_reviews",
            "meta_score",
            "movie_url"
        ]
        movies_df = pd.DataFrame(movies_query_result, columns=movies_columns)
        log_message("INFO", f"Retrieved {len(movies_df)} records from table '{movies_table}'.")
        print("=== Movies Table ===")
        print(movies_df)

        # 5.2 people
        select_people_sql = f"SELECT * FROM `{people_table}`;"
        people_query_result = db.execute_query(select_people_sql)
        people_columns = [
            "id",
            "person_id",
            "name"
        ]
        people_df = pd.DataFrame(people_query_result, columns=people_columns)
        log_message("INFO", f"Retrieved {len(people_df)} records from table '{people_table}'.")
        print("\n=== People Table ===")
        print(people_df)

        # 5.3 movie_people
        select_movie_people_sql = f"SELECT * FROM `{movie_people_table}`;"
        movie_people_query_result = db.execute_query(select_movie_people_sql)
        movie_people_columns = [
            "id",
            "movie_id",
            "person_id",
            "role"
        ]
        movie_people_df = pd.DataFrame(movie_people_query_result, columns=movie_people_columns)
        log_message("INFO", f"Retrieved {len(movie_people_df)} records from table '{movie_people_table}'.")
        print("\n=== Movie-People Table ===")
        print(movie_people_df)

    except Exception as e:
        log_message("ERROR", f"Database operation failed: {e}")
    finally:
        db.close()

def save_reviews_to_db(db, reviews):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS imdb_top_movies.movie_comment (
        id INT AUTO_INCREMENT PRIMARY KEY,
        movie_id VARCHAR(50),
        time VARCHAR(255),
        user_name VARCHAR(255),
        comment_title TEXT,
        comment_content TEXT
    )
    """
    db.execute_non_query(create_table_query)

    insert_query = """
    INSERT INTO imdb_top_movies.movie_comment (movie_id, time, user_name, comment_title, comment_content)
    VALUES (%s, %s, %s, %s, %s)
    """

    # Prepare data for batch execution
    review_tuples = [
        (
            review['movie_id'],
            review['time'],
            review['user_name'],
            review['comment_title'],
            review['comment_content']
        )
        for review in reviews
    ]

    try:
        # Execute batch insert
        db.execute_many(insert_query, review_tuples)
        print(f"Successfully saved {len(reviews)} reviews to the database.")
    except Exception as e:
        print(f"Error saving reviews to the database: {e}")
        raise  # Optionally re-raise the exception for further debugging


