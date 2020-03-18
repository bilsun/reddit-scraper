import json
import praw
import psaw
import pandas as pd
import numpy as np
import datetime as dt
import requests
import textwrap
import time

start_time = time.time()

# Load Reddit authentication from credentials.json for PRAW
with open(r'C:\Users\billi\OneDrive\Documents\school\RESEARCH\credentials.json') as f:
    params = json.load(f)

reddit = praw.Reddit(client_id=params['client_id'], 
                     client_secret=params['api_key'],
                     password=params['password'], 
                     user_agent='privacy_gigwork_project',
                     username=params['username'])

keywords = 'data' # 'sketchy|privacy|private|security|risk|risky|data|tracking|track|surveillance|monitoring|camera'
subs = 'couriersofreddit' # 'couriersofreddit,instacartshoppers,shiptshoppers,shipt,amazonflex,amazonflexdrivers,lyftdrivers,lyft,uberdrivers,ubereats,uber,taskrabbit,upwork,mturk,doordash,doordash_drivers,postmates,grubhubdrivers'
submission_fields = 'id,score,permalink,subreddit,title,selftext,created_utc,author,num_comments' 
comment_fields = 'id,parent_id,score,body,is_submitter,author' # not being used rn
posts_shown = 3

# SEARCH SUBMISSIONS - default size=25, up to 500, can also restrict by score (e.g. score=>100)
url = f"https://api.pushshift.io/reddit/search/submission/?q={keywords}&subreddit={subs}&fields={submission_fields}&size={posts_shown}&sort_type=score&num_comments=>1&metadata=true"
request = requests.get(url)
posts = request.json()
data = posts["data"]
metadata = posts["metadata"]

print(metadata["shards"]) # make sure pushshift is working correctly

wrapper = textwrap.TextWrapper(initial_indent='\t', subsequent_indent='\t')

with open('reddit_comments.txt', 'w', encoding="utf-8") as file:
    file.write("SUBREDDITS: "+ subs +" | KEYWORDS: "+ keywords +" | showing "+ str(metadata["results_returned"]) +" out of "+ str(metadata["total_results"]) +" posts \n")
    file.write("posts are sorted by score and all contain at least 1 comment \n\n")
    file.write("-----------------------------------------\n\n")

    # adding comment data
    for d in data:
        # accessing PRAW
        submission = reddit.submission(id=d['id']) # filter out irrelevant posts here
        submission.comment_sort = 'top'
        d.update({'score': submission.score})

        d.update({'post keywords': keywords}) # for reference in csv
        d.update({'created_utc': dt.datetime.fromtimestamp(d['created_utc']).date()}) # fix date formatting
        
        # accurate top comment scores from PRAW
        d.update({'comment_score': submission.comments[0].score})
        d.update({'top_comment': submission.comments[0].body})


        # TXT FILE
        file.write("post score: "+str(submission.score)+" | r/"+d['subreddit']+" | u/"+d['author']+" | "+str(d['num_comments'])+" comments | "+str(d['created_utc'])+"\n")
        file.write(submission.url + "\n")
        file.write("POST TITLE: "+ d['title'] +"\n")
        file.write(d['selftext'] + "\n\n")

        # checking which comments are by OP
        op = ""
        if d['author'] == str(submission.comments[0].author):
            op = " (OP)"

        file.write("\tcomment score: " + str(submission.comments[0].score) + " | u/"+ str(submission.comments[0].author) + op +"\n")
        file.write(wrapper.fill(submission.comments[0].body) + "\n\n")
        file.write("-----------------------------------------\n\n")

        # submission.comments.replace_more(limit=None)
        # print(submission.title)
        # for comment in submission.comments.list():
        #     print(comment.body)

        # get all comment IDs for each post
        # urlComments = f"https://api.pushshift.io/reddit/submission/comment_ids/{d['id']}"
        # request = requests.get(urlComments)
        # json_response = request.json()
        # comment_ids = ",".join(json_response["data"]) # turn json into a comma-separated string for next query

        # urlID = f"https://api.pushshift.io/reddit/comment/search?ids={comment_ids}&fields={comment_fields}&sort_type=score"
        # request = requests.get(urlID)
        # comments = request.json()
        # commentData = comments["data"]

        # add comment data to post data in csv
        # i = 1
        # for c in commentData:
        #     print(c['parent_id'])
        #     if c['parent_id'][0:3] == "t3_":
        #         d.update({'comment'+str(i): "Score: " + str(c.get("score","N/A")) + " | ID: " + str(c.get("id","N/A")) + " | Parent ID: " + str(c.get("parent_id","N/A")) + " | Body: " + c.get("body","N/A")})
        #         i = i + 1
        #         print(i)
        #         break
        #     print("else; id: " + c['id'])

df = pd.DataFrame.from_records(data, columns= ['permalink', 'subreddit', 'post keywords', 'created_utc', 'score', 'title', 'selftext', 'top_comment', 'comment_score'])
df['permalink'] = "https://reddit.com" + df['permalink'].astype(str)
df.to_csv('reddit_overview.csv', index=False, header=True)

print("---runtime: %s seconds ---" % (time.time() - start_time))