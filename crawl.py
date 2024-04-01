import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import re

def get_response(url):
    '''
        return the response of getting url of a specific page
    '''
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    return requests.get(url, headers=headers)

def get_next_day(date):
    '''
        get the next day for preparing the next url to get 
        input : date -> which is in yyyy/mm/dd format
        output: next day
    '''
    input_datetime = datetime.strptime(date, '%Y/%m/%d')
    next_day = input_datetime + timedelta(days=1)
    next_day_str = next_day.strftime('%Y/%m/%d')
    return next_day_str

def extract_date_from_url(url):
    '''
        extracting the date from web url
        input : url
        output : date (string)
    '''
    pattern = r'/(\d{4})/(\d{2})/(\d{2})$'
    match = re.search(pattern, url)
    if match:
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
        return year + '/' + month + '/' + day
    else:
        return None
    
def get_next_url(curr_url):
    '''
        getting the url for tomorrow
        input : curr_url
        output : next_url
    '''
    today = extract_date_from_url(curr_url)
    if today:
        tomorrow = get_next_day(today)
        next_url = 'https://www.wsj.com/news/archive/' + tomorrow
        return next_url
    return None

def get_soup(url):
    '''
        get the soup of a page
        input : url
        output : soap object
    '''
    try:
        response = get_response(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        else:
            print(f"failed to fetch the page with status code : {response.status_code}")
            return None
    except:
        print("Error fetching the page")
        return None
    
def get_headline_articles(soup):
    '''
        get the headline articles from the soup of the page
    '''
    try:
        articles = soup.find_all('article', class_='WSJTheme--story--XB4V2mLz WSJTheme--padding-top-large--2v7uyj-o styles--padding-top-large--3rrHKJPO WSJTheme--padding-bottom-large--2lt6ga_1 styles--padding-bottom-large--2vWCTk2s WSJTheme--border-bottom--s4hYCt0s')
        return articles
    except Exception as e:
        print(f"Error retrieving the articles: {e}")
        return None
    
def get_article_type(article):
    '''
        get the article type (Genre)
    '''
    try:
        article_type_div = article.find('div', class_='WSJTheme--articleType--34Gt-vdG')
        if article_type_div:
            article_type = article_type_div.text
            return article_type
        else:
            return None
    except Exception as e:
        print(f"Error retrieving article type: {e}")
        return None
def get_headline(article):
    '''
        get the headline title itself
    '''
    try:
        article_headline_span = article.find('span', class_='WSJTheme--headlineText--He1ANr9C')
        if article_headline_span:
            headline = article_headline_span.text
            return headline
        else:
            return None
    except Exception as e:
        print(f"Error retrieving the headline: {e}")
        return None
def get_news_time_release(article):
    '''
        get the time of release of an news article
    '''
    try:
        article_time_paragraph = article.find('p', class_='WSJTheme--timestamp--22sfkNDv')
        if article_time_paragraph:
            time = article_time_paragraph.text
            return time
        else:
            return None
    except Exception as e:
        print(f"Error retrieving the release time : {e}")
        return None
def get_number_of_pages_today(soup):
    '''
        get the number of pages for today's headlines
    '''
    try:
        num_pages_span = soup.find('span', class_='WSJTheme--pagepicker-total--Kl350I1l')
        if num_pages_span:
            number_of_pages_text = num_pages_span.text
            return extract_number(number_of_pages_text)
        else:
            return None
    except Exception as e:
        print(f"Error retrieving the number of pages : {e}")
        return None
def extract_number(text):
    '''
        extracting the number of the pages from the string
        input strings are in the shape of ---> 'of {number}'
    '''
    try:
        match = re.search(r'of\s+(\d+)', text)
        if match:
            number = int(match.group(1))
            return number
        else:
            return None
    except Exception as e:
        print(f"Error extracting the number {e}")
        return None
def get_headline_dict(article):
    '''
        creates a headline dictionary
        input : an article component
    '''
    headline_dict = {}
    headline_dict['headline title'] = get_headline(article)
    headline_dict['type'] = get_article_type(article)
    headline_dict['release time'] = get_news_time_release(article)
    return headline_dict

def crawling(starting_date):
    '''
    The main Logic of the crawling
    which gets a starting date as input and crawls all headlines for each day up to today
    And stores them in crawled array
    '''
    current_date = starting_date
    while current_date <= datetime.today().strftime('%Y/%m/%d'):
        base_url = f'https://www.wsj.com/news/archive/{current_date}'
        soup = get_soup(base_url)
        if soup:
            number_of_pages = get_number_of_pages_today(soup)
        if number_of_pages == None:
            number_of_pages = 1
        for page_num in range(number_of_pages):
            url = f'https://www.wsj.com/news/archive/{current_date}/?page={page_num+1}'
            page_soup = get_soup(url)
            if page_soup:
                articles = get_headline_articles(page_soup)
                todays_news = {}
                todays_news['date'] = current_date
                if articles:
                    headlines = []
                    for article in articles:
                        headline_dict = get_headline_dict(article)
                        headlines.append(headline_dict)
                    todays_news['headlines'] = headlines
                    crawled.append(todays_news)
                    print(f"Headlines for {current_date} crawled successfully! (page {page_num + 1})")
        current_date = get_next_day(current_date)

def write_crawled_files(crawled):
    '''
        writes crawled content into .json format
    '''
    with open('unprocessed/WSJ_headlines.json', 'w') as f:
        json.dump(crawled, f, indent=2)


crawled = []
start_date = '2023/03/01'
crawling(start_date)
write_crawled_files(crawled)
print("Finished Crawling")



