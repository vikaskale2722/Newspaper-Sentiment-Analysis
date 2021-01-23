from django.shortcuts import render

import lxml, urllib.request                                                 # lxml is a library for parsing, urllib is to open the page
from bs4 import BeautifulSoup as bs                                         # bs4 helps decode and search through page.
from textblob import TextBlob                                                   # the module that runs sentiment analysis             

news_contents = []
avg_sents = []
myLists = []
currentCategory = 0

def analyseAll(cat):
    # News fetching links
    mainCategories = ['https://www.thehindu.com/news/national/?page=','https://www.thehindu.com/news/international/?page=',
                    'https://www.thehindu.com/sci-tech/science/?page=','https://www.thehindu.com/business/?page=']

    # Read news
    def urlMaker(mainUrl,x):                                                    # For making individual page URLS
        url = mainUrl + str(x)
        return url

    def soupee(url):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})                                                            # Create Soup object with bs4
        sauce=urllib.request.urlopen(req)
        soup = bs(sauce, 'lxml')
        return soup

    def parser(soup):                                                           # Parse page and create two lists of the titles and link
        titles = []                                                               # to each news of title
        links = []
        for news in soup.find_all('div', class_='story-card-news'):
            title = news.text
            link = news.find_all('a')
            titles.append(title)
            links.append(link[2]['href'])
        return  titles, links

    def newsStoryGrabber(links):                                                # Use the Links list to goto the site and get the first two
        data=[]                                                                   # paragraphs of the new and return a story list.
        for i in range(len(links)):
            url = links[i]
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            sauce=urllib.request.urlopen(req)
            soup = bs(sauce, 'lxml')
            aa = soup.find('div', class_='article')
            bb = aa.find_all('p')
            cc = bb[1].text + bb[2].text
            data.append(cc)
        return data

    def seeNews(titles,links):                                                  # Show each story with title as the indices of each correspond 
        stories = newsStoryGrabber(links)                                         # correctly, i.e. index zero of both are for same News.
        # for i in range(len(titles)):
        #   print(titles[i] + '\n' + stories[i]+ ' \n')
        #   print('________________________________________\n')
        return titles, stories

    lists=[]
    mainUrl = mainCategories[cat]                                                # Just the National Page           

    for x in range(1, 6):                                                      # Iterate through first 6 pages
        newsPaper={}
        url = urlMaker(mainUrl, x)
        soup = soupee(url)
        titles, links = parser(soup)
        seeNews(titles,links)

    title, news = seeNews(titles, links)
    news_content = {}
    for i in range(len(title)):
        news_content.update({title[i]:news[i]})

    # sent analysis
    def newsAnalysis(dataDiX):                                                      # take the { title:story } dictionary and runs sentiment
        sent = []                                                                   # analysis on it and returns 
        sentVal = []
        for news in list(dataDiX.values()):
            analysis = TextBlob(news)
            sentiment = find_Sentiment(analysis.sentiment.polarity)
            qq = analysis.sentiment.polarity
            sentVal.append(qq)
            sent.append(sentiment)
        return sent, sentVal

    def find_Sentiment(val):                                                                                                               
        if val<=0.1 and val>-0.1:
            return 'Neutral'
        elif val>0.1:
            return 'Positive'
        else:
            return 'Negative'

    def listMaker(newsPaper, titles, sent, sentVal, lists):
        totalSent = 0
        for i in range(len(newsPaper)):
            sas = titles[i] + ' : ' + sent[i]+ ' : ' + str(sentVal[i])
            totalSent+=sentVal[i]
            lists.append(sas)
            lists= [x.replace('\n', '') for x in lists]
        return lists, totalSent
            
    def sentimentAnalysis(newsPaper, titles, links):
        lists = []
        stories = newsStoryGrabber(links)
        newsPaper=dict(zip(titles,stories))
        sent, sentVal = newsAnalysis(newsPaper)
        lists, totalSent = listMaker(newsPaper, titles, sent, sentVal, lists)
        return lists

    def avgSentiment(newsPaper, titles, links):
        lists = []
        stories = newsStoryGrabber(links)
        newsPaper=dict(zip(titles,stories))
        sent, sentVal = newsAnalysis(newsPaper)
        lists, totalSent = listMaker(newsPaper, titles, sent, sentVal, lists)

        avgSent = totalSent/len(titles)
        #print("Average Sentiment now , is : "+ str(avgSent))
        return avgSent

    # lists=[]

    newsPaper={}
    sentValue=[]
    for x in range(1,6):
        url = urlMaker(mainUrl, x)
        soup = soupee(url)
        titles, links = parser(soup)
        sentimentAnalysis(newsPaper, titles, links)
        avgSentVal = avgSentiment(newsPaper, titles, links)
        sentValue.append(avgSentVal)

    mylist = sentimentAnalysis(newsPaper, titles, links)
    avg_sent = avgSentiment(newsPaper, titles, links)

    return news_content, mylist, avg_sent

print("\n\n>>>>>Fetching data")

for i in range(4):
    print("\n\n>>>>>>> Entered " + str(i) + " loop")
    tempNews, tempML, tempAvg = analyseAll(i)
    print("fetched for current iteration")
    news_contents.append(tempNews)
    avg_sents.append(tempAvg)
    myLists.append(tempML)
    print("\n\n>>>>>>>>"+str(i)+" ready")

print("\n\n>>>>>Data fetched and processed!!!\n\n")
    
    

# Create your views here.
def home(request):
    return render(request, 'home/index.html')

def readNewsPage(request):
    global currentCategory
    try:
        currentCategory = int(request.GET["cat"])
    except:
        pass
        
    context = {'news_content':news_contents[currentCategory]}
    return render(request, 'home/news.html', context)

def sentimentNewsPage(request):
    finalList = []
    for item in myLists[currentCategory]:
        mylist1 = list(map(str, item.split(":")))
        finalList.append(mylist1)
    return render(request, 'home/sentimentNews.html', {'news_content':finalList})

def overallSentimentNewsPage(request):
    return render(request, 'home/overallSentimentNews.html', {'news_content':avg_sents[currentCategory]})