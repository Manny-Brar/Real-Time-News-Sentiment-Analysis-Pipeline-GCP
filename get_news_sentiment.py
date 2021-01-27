#%pip install --upgrade gcloud
#%pip install vaderSentiment

# importing libraries and tools
import os
import pandas as pd
import urllib3, requests
import gcloud 
from gcloud import storage
import six
from google.cloud import bigquery as bq
import json
from tqdm import tqdm
import vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



#Setup Credentials for access to NY Times API and google cloud platform
API_KEY= "QZMjBgVAPsdKNLvsrVZb5eMtAcBMha76"
os.environ['GOOGLE_APPLICATION_CREDENTIALS']='gcp-creds.json'


#Function to get nytimes news stream and create a csv dataframe and process the 'first_published_date' column as datetime format
def get_news_stream(API_KEY, limit):
    url= "https://api.nytimes.com/svc/news/v3/content/all/all.json?api-key="+API_KEY+"&limit="+str(limit)
    try:
        page=requests.get(url, verify=False)
        stream_news=pd.json_normalize(page.json()['results'])[['title', 'section', 'slug_name','byline','item_type','material_type_facet','des_facet','org_facet','per_facet','geo_facet','abstract','first_published_date', 'url']]
        stream_news['first_published_date']=pd.to_datetime(stream_news['first_published_date'],format='%Y-%m-%d %H:%M:%S')
    except:
        print("ERROR: Can't access articles from The New York Times")
        return
    return stream_news

stream_=get_news_stream(API_KEY, 120)


    
# Utilizing Vader Sentiment analysis, get polarity scores for columns 'title' and 'abstract'
def vader_sentiment():
    analyzer= SentimentIntensityAnalyzer()
    stream_['compound_title'] = [analyzer.polarity_scores(v)['compound'] for v in stream_['title']]
    stream_['neg_title'] = [analyzer.polarity_scores(v)['neg'] for v in stream_['title']]
    stream_['neu_title'] = [analyzer.polarity_scores(v)['neu'] for v in stream_['title']]
    stream_['pos_title'] = [analyzer.polarity_scores(v)['pos'] for v in stream_['title']]

    stream_['compound_ab'] = [analyzer.polarity_scores(v)['compound'] for v in stream_['abstract']]
    stream_['neg_ab'] = [analyzer.polarity_scores(v)['neg'] for v in stream_['abstract']]
    stream_['neu_ab'] = [analyzer.polarity_scores(v)['neu'] for v in stream_['abstract']]
    stream_['pos_ab'] = [analyzer.polarity_scores(v)['pos'] for v in stream_['abstract']]
    return stream_


# Creating new column's sentiment_score and sentiment, which is the sum of sentiment_Score from the title and abstract # and sentiment is simply a positive, negative or neutral value of the sentiment.
def sentiment_processing():
    stream_sentiment=stream_
    stream_sentiment[['sentiment_score']]=stream_sentiment['compound_title']+stream_sentiment['compound_ab']
    stream_sentiment.loc[stream_sentiment['sentiment_score']>0, 'sentiment'] = 'Positive'
    stream_sentiment.loc[stream_sentiment['sentiment_score']<0, 'sentiment'] = 'Negative'
    stream_sentiment.loc[stream_sentiment['sentiment_score']==0, 'sentiment'] = 'Neutral'
    print('COMPLETE: Sentiment Processing')

    
# Create a sentiment csv file and save locally
def sentiment_csv():
    stream_sentiment=vader_sentiment()
    stream_sentiment.to_csv('news_sentiment_stream.csv', index=False)
    print("File saved as csv")



# Function to upload and overwrite sentiment csv file to desired GCP Cloud Storage Bucket
def upload_file_to_bucket(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the GCP bucket."""
    client = storage.Client()
    bucket = client.get_bucket('sentiment_bucket_wcd')
    bucket_name = "sentiment_bucket_wcd"
    source_file_name = "news_sentiment_stream.csv"
    destination_blob_name = "news_sentiment_stream.csv"

    client = storage.Client()
    bucket = client.bucket('sentiment_bucket_wcd')
    blob = bucket.blob('news_sentiment_stream.csv')

    blob.upload_from_filename('news_sentiment_stream.csv')

    print(
        "File {} uploaded to {}.".format(
            source_file_name, bucket_name))
    
    
    
    
    
# Function to upload the sentiment csv file to the desired BigQuery dataset and table    
def upload_to_bq():
    # Construct a BigQuery client object.
    clientbq = bq.Client(project='linen-jet-293921')
    table_ref = clientbq.dataset("sentiment_df").table("nytimes-sentiment")

    job_config = bq.LoadJobConfig(write_disposition=bq.job.WriteDisposition.WRITE_TRUNCATE)
    job_config.source_format = bq.SourceFormat.CSV
    job_config.skip_leading_rows = 1 
    job_config.autodetect = True

    with open("news_sentiment_stream.csv", "rb") as source_file:
        job = clientbq.load_table_from_file(
            source_file, table_ref, job_config=job_config)

    # Waiting for job to complete
    print('Processing: Loading data to BigQuery table...')
    job.result()




# Main function to execute pipeline
def main():
    get_news_stream(API_KEY, 100)
    vader_sentiment()
    sentiment_processing()
    sentiment_csv()
    upload_file_to_bucket("sentiment_bucket_wcd", "news_stream.csv", "news_stream.csv")
    upload_to_bq()
    print('SUCCESS: NY Times News Sentiment ETL Pipeline Complete!')
    print('Table ready for query in BigQuery and CSV stored in GCP bucket')

    
if __name__ == "__main__":
    main()