from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import json
import sys

with open('text.txt','r') as hashtagsfile:
  hashtags = hashtagsfile.read()
hashtagsList = hashtags.split('\n') 
tagList = [tag[1:] for tag in hashtagsList]

tags_list = tagList
dict = {}
print(tags_list)

def get_link(tag):
      initial = "https://www.pexels.com/search/"
      page_link = initial  + tag + "?page=1"
      cnt = 0
      
      while True:
          page_response = requests.get(page_link)
          page_content = BeautifulSoup(page_response.content, "html.parser")
          
          if page_content.find('img', class_ = 'photo-item__img') and cnt <= 1000:
            for i in page_content.find_all('img', class_ = 'photo-item__img'):
              if tag in dict.keys():
                dict[tag].append(i["src"])
              else:
                dict[tag] = []
                dict[tag].append(i["src"])
            cnt += 30
            curr_page = int(page_link[-1:])
            curr_page += 1
            page_link = page_link[:-1]
            print(type(curr_page))
            pqr = str(curr_page)
            page_link = page_link + pqr
            print(page_link)
           
          else:
            break
