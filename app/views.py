#!/Users/gurmehrsohi/Desktop/.venv2/bin/python
# -*- coding: utf-8 -*-
import json, requests, random, re
from pprint import pprint

from django.shortcuts import render
from django.http.response import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import requests
import unicodedata
from unidecode import unidecode
from bs4 import BeautifulSoup
mainurl="http://www.imdb.com"
mainurl_rotten="https://www.rottentomatoes.com"
Rating_movies={}
movie_summary={}
movies_name={}
def getmoviedetails(string,user_name):
    try:
        r=requests.get("http://www.imdb.com/find?q="+string)
        soup =BeautifulSoup(r.text,"html.parser")
        section=soup.find('div',{'class':'findSection'})
        big_list=section.find('table',{'class':'findList'})
        list=big_list.find_all('tr')
        name_movie_uni=list[0].text
        name_movie=unidecode(name_movie_uni)
        movies_name[user_name]=name_movie
        cururl=mainurl+list[0].find('a').get('href')
        return func_movie(cururl,user_name)
    except:
        return movie_rotten(string,user_name)

def func_movie(cururl,user_name):
    r1=requests.get(cururl)
    soup =BeautifulSoup(r1.text,"html.parser")
    Summary1 = soup.find('div',{'class':'summary_text'})
    Summary2=Summary1.text
    Summary3=Summary2.replace("\n","")
    Summary=Summary3.replace("          ","")
    movie_summary[user_name]=Summary
    poster=soup.find('div',{'class':'poster'})
    rate=soup.find('span',{'itemprop':'ratingValue'})
    rating=unidecode(rate.text)
    Rating_movies[user_name]=rating
    poster_image=poster.find('img').get('src')
    url_poster=repr(poster_image)
    img=url_poster.replace("'","")
    url_poster=img.replace("u","")
    
    #i=unicodedata.normalize('NFKD', poster_image).encode('ascii','ignore')
    return url_poster

def movie_rotten(string,user_name):
    r=requests.get("https://www.rottentomatoes.com/search/?search="+string.lower())
    soup =BeautifulSoup(r.text,"html.parser")
    all_movies1=soup.find('section',{'id':'SummaryResults'})
    movie=all_movies1.find('li',{'class':'clearfix'})
    link=movie.find('a',{'class':'articleLink'}).get('href')
    act_link=unidecode(link)
    rotten_url=mainurl_rotten+act_link
    r1=requests.get(rotten_url)
    soup =BeautifulSoup(r1.text,"html.parser")
    bigpart=soup.find('div',{'id':'mainColumn'})
    movies_name[user_name]=soup.find('h1',{'id':'movie-title'}).text
    movie_summary[user_name]=soup.find('div',{'id':'movieSynopsis'}).text
    Rating_movies[user_name]=soup.find('span',{'class':'meter-value'}).text
    poster_link=bigpart.find('img',{'class':'posterImage'}).get('src')
    return unidecode(poster_link)

    
    
    
def gettrailer(string):
    r=requests.get("https://www.rottentomatoes.com/search/?search="+string.lower())
    soup =BeautifulSoup(r.text,"html.parser")
    all_movies1=soup.find('section',{'id':'SummaryResults'})
    movie=all_movies1.find('li',{'class':'clearfix'})
    link=movie.find('a',{'class':'articleLink'}).get('href')
    act_link=unidecode(link)
    rotten_url=mainurl_rotten+act_link
    r1=requests.get(rotten_url)
    soup =BeautifulSoup(r1.text,"html.parser")
    video=soup.find('div',{'class':'movie'})
    #try:
    video_link_ran=video.find('a').get('data-mp4-url')
    video_link=unidecode(video_link_ran)
    return video_link
    
    #video_link_ran=soup.find('a',{'class':'trailer_play_action_button'})
    #video_link=unidecode(video_link_ran)
    #return video_link

PAGE_ACCESS_TOKEN ='EAAHDBPLJRvABAPSuvIruaqscc9s64L0yZBBIAdlszx60wlz1OQy3Qle6rF0nEumBqgDnACTKDsogyqGsybqCW0R9zAaWytWabYAMc0QVNeVyJZBTX16217N4f8Yhin0tSydtBRR4I8U8TPG1P38ZAoDCR5cy1LQq8tH82bZCLwZDZD'

num="123456789"
dict_trailer={}
def new_movie(fbid,recevied_message):
    
    user_details_url= "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic','access_token':PAGE_ACCESS_TOKEN}
    user_details = requests.get(user_details_url,user_details_params).json()
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    name=getmoviedetails(recevied_message,fbid)
  
    trailer=gettrailer(recevied_message)
    
    dict_trailer[fbid]=trailer

    message_object2 = {
        "attachment":{
            "type":"template",
                "payload":{
                    "template_type":"generic",
                    "elements":[
                        {
                            "title":movies_name[fbid],
                            "image_url":name,
                            "subtitle":movie_summary[fbid],
                            "buttons":[
                                {
                                    "type":"postback",
                                    "title":"IMDB Rating",
                                    "payload":"RATING",
                                },
                                {
                                    "type":"postback",
                                    "title":"Trailer",
                                    "payload":"TRAILER",
                                }
                            ]
                        }
                    ]
                }
            }
        }

    
        
    response_message2 = json.dumps({"recipient":{"id":fbid},"message":message_object2})
    status = requests.post(post_message_url,headers={"Content-Type": "application/json"},data=response_message2)
    pprint(status.json())

def render_postback(fbid,payload):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    if payload == 'RATING':
        text=Rating_movies[fbid]
        try:
            response_message = json.dumps({"recipient":{"id":fbid},"message":{"text":text}})
            status = requests.post(post_message_url,headers={"Content-Type": "application/json"},data=response_message)
        except:
            pprint('error')
    if payload == 'TRAILER':
        message_object = {
            "attachment":{
                "type":"video",
                    "payload":{
                        "url":dict_trailer[fbid]
                            }
                        }
                }

        try:
            response_message = json.dumps({"recipient":{"id":fbid},"message":message_object})
            status = requests.post(post_message_url,headers={"Content-Type": "application/json"},data=response_message)
        except:
            pprint('error')




class findmovie(generic.View):
    def get(self,request,*args,**kwargs):
        if self.request.GET['hub.verify_token'] == '8130405332':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse("sorry")

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self,request,*args,**kwargs):

        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    pprint(message)
                    try:
                        new_movie(message['sender']['id'],message['message']['text'])
                    except:
                        return HttpResponse("sorry")
                if 'postback' in message:
                    pprint(message)
                    try:
                        render_postback(message['sender']['id'],message['postback']['payload'])
                    except:
                        return HttpResponse("sorry")
            break
        return HttpResponse()


