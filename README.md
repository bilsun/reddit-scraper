# reddit-scraper
Using PRAW (Python Reddit API Wrapper) and Pushshift to scrape Reddit for research purposes (e.g. content analysis, thematic analysis)--originally intended for qualitative researchers since scraped data is formatted for readability (doesn't prioritize efficiency or scalability)

### Walkthrough Slide Deck 
*Software to download, overview of files, suggested workflow, ethics of web scraping* 
https://docs.google.com/presentation/d/1oKUzeonnlYPOOWw2h7wXjVkEbgDPNqM5g7IGPoCoETQ/edit?usp=sharing 

### Analyzing Reddit Posts
- **posts_to_csv.py** outputs to **data > scraped_posts** 

### Analyzing Reddit Comments
- **comments_to_csv.py** outputs to **data > scraped_comments**
- **comments_to_txt.py** outputs to **data > qual_comment_analysis** 
  - *Requires hand coding scraped Reddit posts prior to running*

Email me at bs676@cornell.edu if you have any questions or feedback!
