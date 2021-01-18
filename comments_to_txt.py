# EXPORTS TXT FILE WITH COMMENT DATA FOR MANUALLY SPECIFIED REDDIT POSTS
# outputs to data > qual_comment_analysis > selected_reddit_comments.txt

import json
import praw
import pandas as pd
import datetime as dt
import requests
import textwrap
import time
import re 

start_time = time.time()

# [INPUT NEEDED] -------------------------------
# replace these variables according to your qualitative research needs:

# Load Reddit authentication for PRAW
# reference: https://www.storybench.org/how-to-scrape-reddit-with-python/
reddit = praw.Reddit(client_id='PERSONAL_USE_SCRIPT_14_CHARS', 
                     client_secret='SECRET_KEY_27_CHARS',
                     user_agent='YOUR_APP_NAME')

post_data = pd.read_csv('./data/qual_comment_analysis/manually_coded_posts.csv') 
filter_criteria = post_data['relevance-reconciled'] == 1 # dictates the content of selected_reddit_comments.txt

sort_by = 'top' # options: best, top, new, controversial

# -----------------------------------------------

# preparing data 

relevant_posts = post_data[filter_criteria]
relevant_posts = relevant_posts.sort_values(['score', 'comment_score'], ascending=False)

relevant_post_ids = relevant_posts['id'].tolist()
sub_list = relevant_posts["subreddit"].unique()
subs = ", ".join(sub_list)
keyword_list = relevant_posts["post keywords"].unique()
keywords = ", ".join(keyword_list)

# -----------------------------------------------

# functions styling for readability 

wrapper = textwrap.TextWrapper(initial_indent='\t', subsequent_indent='\t')

def clean_text(text):
    text = text.strip()
    text = re.sub('\n+', '\n', text)
    text = re.sub('&amp;', '&', text)
    text = re.sub('&lt;', '<', text)
    text = re.sub('&gt;', '>', text)
    text = re.sub('&#x200B;', '', text)
    text = re.sub('&nbsp;', ' ', text)
    return text

def indicate_op(is_op):
    if is_op:
        return " (OP)"
    else:
        return ""

# -----------------------------------------------

print(f"exporting comments for {len(relevant_posts.index)} manually specified posts...")

with open('./data/qual_comment_analysis/selected_reddit_comments.txt', 'w', encoding="utf-8") as file:
    file.write("SUBREDDITS REPRESENTED: "+ subs +" | KEYWORDS: "+ keywords +"\n")
    file.write(f"showing {str(len(relevant_posts.index))} manually specified posts | comments are sorted by '{sort_by}' \n\n")
    file.write("-----------------------------------------\n\n")

    for id in relevant_post_ids:

        submission = reddit.submission(id=id)
        submission.comment_sort = sort_by
        
        # TXT FILE
        file.write("post score: "+str(submission.score)+" | r/"+str(submission.subreddit.display_name)+" | u/"+str(submission.author)+" | "+str(submission.num_comments)+" comments | "+str(dt.datetime.fromtimestamp(submission.created_utc).date())+" | "+submission.shortlink+"\n")
        file.write("POST TITLE: "+ submission.title +"\n")
        file.write(clean_text(submission.selftext) + "\n\n")

        # DISPLAYING COMMENTS -----------------------------------------
        comm_list = []
        info_list = []
        tab_list = []

        # may become slow/inaccurate if dealing with thousands of comments since this is purely for qual analysis
        submission.comments.replace_more(limit=None) 
        comment_queue = submission.comments[:] # top-level comments
        while comment_queue:
            comment = comment_queue.pop(0)
            comm_list.append(clean_text(comment.body))
            info_list.append("comment score: "+str(comment.score)+" | u/"+str(comment.author)+indicate_op(comment.is_submitter))
            
            # formatting indents to simulate Reddit's nested comment structure
            if comment.parent_id[:3] == "t3_": # top-level comment
                tab_list.append("")
            else:
                tab_list.append(comment.depth*"\t")

            comment_queue[0:0] = comment.replies # push comment replies to the top of the queue

        assert(len(comm_list)==len(info_list)==len(tab_list)) # make sure lists match up before writing to txt file

        for i in range(len(comm_list)):
            wrapper = textwrap.TextWrapper(initial_indent="\t"+tab_list[i], subsequent_indent="\t"+tab_list[i])
            file.write(wrapper.fill(info_list[i]) +"\n") 
            file.write(wrapper.fill(comm_list[i]) + "\n\n") 

        file.write("-----------------------------------------\n\n")

# -----------------------------------------------

runtime = '{:.0f}'.format(time.time() - start_time)
print(f"--- DONE! runtime: {runtime} seconds ---")
print("see data > qual_comment_analysis for exported txt file \n")