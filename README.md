# Real-Time-News-Sentiment-Analysis-Pipeline-GCP

## Objective:
With all the negativity in news headlines recently, it can be a real strain on mental health when you are constantly bombarded with negative news articles and headlines. This project was intended to assist, when you just need a break from negative news articles and want to filter news by positive, neutral or negative sentiment. This was the problem I wanted to create a solution for and by developing a pipeline that performs real-time sentiment analysis on news articles and allows for the user to filter results based on positive or negative sentiment of each article.

## Sentiment Analysis:
Sentiment Analysis is a computational process to determine the overall sentiment of a piece of text. This sentiment is usually categorized into 3 main output’s, Positive, Neutral and Negative. This process can help determine the “mood” of the text and this can be extremely useful in a variety of use cases.

## GCP Processing Pipeline:
Cloud Scheduler is used to schedule the pipeline execution via a cronjob and using HTTP App Engine to run a Cloud Function which will execute a python script hosted on a VM Compute Engine and will log the function run data. The script returns news headlines data from the real-time Timeswire API. Next the script processes the data and utilizes VADER Sentiment analysis to analyze the title and abstract columns. Creates a aggregated sentiment score for each article. Then the data is stored as a CSV file and uploaded to a GCP Cloud Storage Bucket and also the data is loaded into a BigQuery table. Finally the BigQuery table is accessed by the DataStudio dashboard and data is refreshed every few minutes, for a real-time sentiment analysis dashboard.

![Real-Time News Sentiment Analysis](https://github.com/Manny-Brar/Real-Time-News-Sentiment-Analysis-Pipeline-GCP/blob/main/bandicam%202021-01-26%2017-25-43-560.jpg)
![NY Times API](https://github.com/Manny-Brar/Real-Time-News-Sentiment-Analysis-Pipeline-GCP/blob/main/bandicam%202021-01-26%2017-38-24-450.jpg)
![Data Infrastructure-GCP](https://github.com/Manny-Brar/Real-Time-News-Sentiment-Analysis-Pipeline-GCP/blob/main/bandicam%202021-01-26%2017-27-02-313.jpg)
![Real-Time News Sentiment Analysis Dashboard- GCP DataStudio](https://github.com/Manny-Brar/Real-Time-News-Sentiment-Analysis-Pipeline-GCP/blob/main/bandicam%202021-01-16%2018-53-04-542.jpg)
