# -*- coding: utf-8 -*-
"""
Spyder Editor
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests

rs = requests.session()

header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

mainURL = 'https://www.eprice.com.tw'
        
def getpages(URL):
    res = rs.get(URL,headers = header)
    res.encoding = 'big-5'
    soup = BeautifulSoup(res.text, "html.parser")
    page = soup.find_all("a" , {"data-name" : "page"})
    pages = page[-2].text.replace(".", "")
    return(int(pages))
    
def get_mainpage(mainURL,totalpages):   
    areply = []
    alist =[]
    atitle = []
    ahyperlinks = []
    apopul = []
    alastreply = []
    aposttime = []
    for i in range(1,totalpages): 
        URL = mainURL + '/mobile/talk/4543/0/'+str(i)+'/'
        res = rs.get(URL,headers = header)
        res.encoding = 'big-5'
        soup = BeautifulSoup(res.text, "html.parser")
        commercial = len(soup.find_all("a",{"class" : "title text-wrap highlight"}))
        title = soup.find_all("a" , {"class" : "title text-wrap"})#space included
        popul = soup.find_all("span",{"class" : "num"})
        popul = popul[commercial:]
        reply = soup.find_all("span" , {"class" : "count"})
        reply = reply[commercial:]
        posttime = soup.find_all("li",{"class" : "author"})
        lastreply = soup.find_all("a",{"class" : "last-respond"})
        for tag in posttime:
            atime = tag.find("span")
            if (atime != None):
                aposttime.append(atime.text)
        aposttime = aposttime[commercial*2:]
        for i in range(len(title)):
            areply.append(reply[i].text.replace(",", ""))
            atitle.append('<a href="https://www.eprice.com.tw'+str(title[i].get('href')+'">'+str(title[i].text)+'</a>'))
            ahyperlinks.append('https://www.eprice.com.tw'+str(title[i].get('href')))
            apopul.append(popul[i].text)
            alastreply.append(lastreply[i].text)
            
    alist = [atitle,ahyperlinks,apopul,aposttime,alastreply]
    return alist

def deldatesbyrecentreply(df,date):
    dates = df['Final Date'].tolist()
    start = 0
    startnum = 0
    endnum = 0
    for i in range(len(dates)):
        if dates[i].split(' ')[0].replace("-", "") == str(date) and start == 0:
            startnum = i
            start = 1
        elif dates[i].split(' ')[0].replace("-", "") != str(date) and start == 1:
            endnum = i
            break
    df = df.iloc[startnum:endnum]
    return df

def deldatesbyposttime(df,date):
    dates = df['Original Date'].tolist()
    newdates = []
    for i in range(len(dates)):
        newdates.append(dates[i].split(' ')[0].replace("-", ""))
    df['date'] = newdates
    #print(df)
    df = df.loc[df['date'] == str(date)]
    df = df.drop(['date'],axis=1) 
    return df     

def getlastcomment(URL,lastpage):
    lastpage = lastpage[-2].text.replace('.','')
    URL = URL.replace('/1/','/'+str(lastpage)+'/')
    res = rs.get(URL,headers = header)
    res.encoding = 'big-5'
    soup = BeautifulSoup(res.text, "html.parser")
    comment = soup.find_all('div',{'class':'user-comment-block'})
    comment = comment[-3].text.replace('\t','').replace('\r','')
    return comment
    
def getarticle(df):
    hyperlink = df['Titlelink']
    aarticle = [] 
    lastcomment = []
    for URL in hyperlink:
        res = rs.get(URL,headers = header)
        res.encoding = 'big-5'
        soup = BeautifulSoup(res.text, "html.parser")
        article = soup.find("div" , {"class" : "user-comment-block"})
        aarticle.append(article.text.replace('\t','').replace('\r',''))
        lastpage = soup.find_all('a' ,{'data-name': 'page'})
        lastcomment.append(getlastcomment(URL,lastpage))
    df['Final'] = lastcomment
    df['Original'] = aarticle
    return df 
    
def geteprice(inputdate):
    datalist = []
    URL = mainURL+'/mobile/talk/4543/0/1/'
    totalpages = getpages(URL) 
    maindata = get_mainpage(mainURL,totalpages)
    for i in range(len(maindata[0])):
        datalist.append([maindata[0][i],maindata[1][i],maindata[2][i],maindata[3][i],maindata[4][i]])
    output = pd.DataFrame(datalist, columns = ['title','Titlelink','hot','Original Date','Final Date'])
    output = deldatesbyrecentreply(output,inputdate)
    output = getarticle(output)
    output = output[['title','Titlelink','hot','Original','Original Date','Final','Final Date']]
    output = output.drop(['Titlelink'], axis=1)
    return output

a=geteprice(20190604)
print(a)
