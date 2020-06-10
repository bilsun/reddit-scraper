# EXPORTS BOTH CSV AND TXT FILE FOR MANUALLY SPECIFIED POSTS

import json
import praw
import pandas as pd
import datetime as dt
import requests
import textwrap
import time
import re 

start_time = time.time()

# Load Reddit authentication from credentials.json for PRAW
reddit = praw.Reddit(client_id='PERSONAL_USE_SCRIPT_14_CHARS', 
                     client_secret='SECRET_KEY_27_CHARS',
                     user_agent='YOUR_APP_NAME')

# styling for readability -----------------------
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

# PROCESSING CSV --------------------------------
post_data = pd.read_csv('./filtered_files/reddit_overview.csv')
is_relevant = post_data['relevance-reconciled']==1
relevant_posts = post_data[is_relevant]
relevant_posts = relevant_posts.sort_values(['score', 'comment_score'], ascending=False)
relevant_posts.to_csv('./filtered_files/relevant_post_overview.csv', index=False, header=True)

relevant_post_ids = relevant_posts['id'].tolist()

sub_list = relevant_posts["subreddit"].unique()
subs = ", ".join(sub_list)
keyword_list = relevant_posts["post keywords"].unique()
keywords = ", ".join(keyword_list)

# -----------------------------------------------

with open('./filtered_files/relevant_post_comments.txt', 'w', encoding="utf-8") as file:
    file.write("SUBREDDITS REPRESENTED: "+ subs +" | KEYWORDS: "+ keywords +" | showing "+ str(len(relevant_posts.index)) +" relevant posts\n")
    file.write("relevant posts are sorted by score and all contain at least 1 comment \n\n")
    file.write("-----------------------------------------\n\n")

    for id in relevant_post_ids:

        submission = reddit.submission(id=id)
        submission.comment_sort = 'top'
        
        # TXT FILE
        file.write("post score: "+str(submission.score)+" | r/"+str(submission.subreddit.display_name)+" | u/"+str(submission.author)+" | "+str(submission.num_comments)+" comments | "+str(dt.datetime.fromtimestamp(submission.created_utc).date())+" | "+submission.shortlink+"\n")
        file.write("POST TITLE: "+ submission.title +"\n")
        file.write(clean_text(submission.selftext) + "\n\n")

        # DISPLAYING COMMENTS -----------------------------------------
        comm_list = []
        info_list = []
        tab_list = []
        submission.comments.replace_more(limit=None) # may become slow/inaccurate if dealing with thousands of comments -- opt for Pushshift in those cases
        comment_queue = submission.comments[:] # top-level comments
        while comment_queue:
            comment = comment_queue.pop(0)
            comm_list.append(clean_text(comment.body))
            info_list.append("comment score: "+str(comment.score)+" | u/"+str(comment.author)+indicate_op(comment.is_submitter))
            
            # formatting to simulate Reddit's nested comment structure
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

print("---runtime: %s seconds ---" % (time.time() - start_time))
