import json
import urllib
from datetime import datetime


def getBandInfo(band_token):
    '''
    get id of target BAND
    '''
    band_list_url = "https://openapi.band.us/v2.1/bands?access_token=" + band_token
    list_req = urllib.request.Request(band_list_url)
    list_res = urllib.request.urlopen(list_req)

    decoded_list = list_res.read().decode("utf8")

    bandlist_json = json.loads(decoded_list)

    target_id = bandlist_json['result_data']['bands'][0]['band_key']

    return target_id


def getBandPost(target_id, band_token):
    '''
    get posts from Band ID (NAVER 1784 B1 Kitchen)
    max 20 posts
    '''
    post_list_url = "https://openapi.band.us/v2/band/posts?access_token=" + band_token + "&band_key=" + target_id + "&locale=ko_KR"
    post_req = urllib.request.Request(post_list_url)
    post_res = urllib.request.urlopen(post_req)

    decoded_post = post_res.read().decode("utf8")
    # print(decoded_post)
    postlist_json = json.loads(decoded_post)

    # print(postlist_json)

    return postlist_json


def getPhotoUrl(photo_json):
    return [photo['url'] for photo in photo_json]


def makeData(postlist_json):
    '''
    process data from postlist_json
    '''
    author = postlist_json['author']['name']
    postkey = postlist_json['post_key']
    content = postlist_json['content']
    createdate = mil_to_date(postlist_json['created_at'])  # milisecond, long
    photos = getPhotoUrl(postlist_json['photos'])  # return an array of photo url

    return {
        'author': author,
        'postkey': postkey,
        'content': content,
        'createdate': createdate,
        'photos': photos
    }


def mil_to_date(milliseconds):
    return str(datetime.fromtimestamp(milliseconds // 1000))

