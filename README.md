# IMDb Top 100 Movie Analysis

分析 IMDb Top 100 电影的相关数据，包括评论爬取、数据处理、模型训练与评估，Word Cloud 等

## 项目结构

- `Helper.py`、`driver.py`、`logger.py`、`main.py`、`scraper.py`：
  - 这些文件用于爬取 IMDb 上的电影相关数据。
  - `main.py` 的主要功能是利用之前的 Top 100 `movie_id`，爬取每部电影的 100 条相关评论。

- `Bert.py`、`XGBosst+NB.py`：
  - 包含三个模型的训练与结果分析，其中每条电影评论的sentiment标签由VADER生成：

| 模型         | Accuracy | Precision | Recall | F1-Score |
|--------------|----------|-----------|--------|----------|
| **BERT**     | 0.8695   | 0.6387    | 0.6037 | 0.6207   |
| **Naive Bayes** | 0.8286   | 0.8000    | 0.0367 | 0.0702   |
| **XGBoost**  | 0.8523   | 0.5738    | 0.6300 | 0.6006   |

- `Word_cloud.py`：
  - 对每部电影的评论生成独立的词云图，帮助直观分析评论内容（Remove Stopwords和电影行业常见Stopwords）。
  - 示例图如下：

 ![image](https://github.com/user-attachments/assets/a85c89da-f41e-47d6-b3ab-8958ddb64dfb)

## 当前database的EER


![image](https://github.com/user-attachments/assets/17d4ce21-2bc4-4e04-a6b5-bb2d6e2efb83)

