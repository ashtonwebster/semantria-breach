from __future__ import print_function
from time import strftime
import semantria
import uuid
import time
import sys
import re
import urllib2
import urllib
import datetime

def retrieve_tweets(search_term, number): 
    response = urllib2.urlopen('http://www.tweets2csv.com/export.php?&q=' + urllib.quote_plus(search_term) + '&rpp=' + number)
    html = response.read()
    lines = html.split("\n");
    tweets = []; 
    for line in lines:
        #remove lines that don't match
        if re.compile(ur'^(?!<b.*).+').match(line) and  not re.compile(ur'^Author').match(line) :
            #check if first line
            tweet_list = re.split(ur'(?<!\\),', line);
            #if correct number of fields
            if (len(tweet_list) == 4) :
                tweets.append(tweet_list[1])
    return tweets


#gets the tweets and results
def make_queries(search_term, count_request, session) :
    initialTexts = retrieve_tweets(search_term, count_request)

    for text in initialTexts:
	   doc = {"id": str(uuid.uuid4()).replace("-", ""), "text": text}
	   status = session.queueDocument(doc)
	   if status == 202:
		  print("\"", doc["id"], "\" document queued successfully.", "\r\n")

    length = len(initialTexts)
    results = []

    while len(results) < length:
	   print("Retrieving your processed results...", len(results), ",", length, "\r\n")
	   time.sleep(2)
	   # get processed documents
	   status = session.getProcessedDocuments()
	   results.extend(status)
    return results

#prints results to screen/file
def interperet_results(results, search_term, length) :
    count = 0.0 # number of documents found
    entity_total = 0.0 # entity sentiment for companies
    document_total = 0.0 # document sentiment for companies
    overall_sentiment = 0.0 # overall sentiment (may not be a company)
    for data in results:
	   # print document sentiment score
	   print("Document ", data["id"], " Sentiment score: ", data["sentiment_score"], "\r\n")
	   overall_sentiment += data["sentiment_score"]
	  # print document themes
	   if "themes" in data:
		  print("Document themes:", "\r\n")
		  for theme in data["themes"]:
			 print("     ", theme["title"], " (sentiment: ", theme["sentiment_score"], ")", "\r\n")

	  # print document entities
	   if "entities" in data:
		  print("Entities:", "\r\n")
		  for entity in data["entities"]:
			 print("\t", entity["title"], " : ", entity["entity_type"]," (sentiment: ", entity["sentiment_score"], ")", "\r\n")
    f = open('stats', 'a')
    print("search_term,time,count,sentiment_sum,sample_avg_sentiment")
    print("{0},{1},{2},{3},{4}".format(search_term, datetime.datetime.isoformat(datetime.datetime.now()), length, overall_sentiment, (overall_sentiment/length)), file=f)
    f.flush()
    f.close()

while 1 == 1 :
    serializer = semantria.JsonSerializer()
    session = semantria.Session("5ab2f346-4da0-4505-a3e1-5031ff095c92", "8bfeaa2f-dd55-4561-9443-19b633e54edc", serializer, use_compression=True)
    #for search_term in ["#sony"] : 
    for search_term in ["#sony","#staples","#panasonic", "#samsung", "#christmas", "officemax", "#officedepot"] :
	   results = make_queries(search_term,"100",session)
	   interperet_results(results, search_term, len(results))
    print("sleeeping for one hour");
    time.sleep(3600)
