import os
import argparse
from pathlib import Path
import time
from datetime import datetime
import slack
from dotenv import load_dotenv

import band_crawler as bc


def searchDB(db_path, create_date):
    '''
    search the DB for the post with create_date
    '''
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    create_date_list = sorted(os.listdir(db_path))
    if create_date in create_date_list:
        print(f"{now} Already exists: {create_date} in DB ({db_path})")
        return True
    
    print(f"{now} {create_date} does not exists in DB ({db_path})")
    return False


def insertDB(db_path, create_date, content):
    '''
    insert create_date of the post into db
    '''
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = os.path.join(db_path, create_date)
    if not os.path.exists(file_name):
        with open(file_name, 'w') as f:
            f.write(content + '\n')
        return True
    
    print(f"{now} Already exists: {create_date} in DB ({db_path})")
    return False


def add_date_on_content(create_date, content):
    '''
    add date to content (ex. 2024년 10월 8일 화요일 점심 메뉴)
    '''
    dt = datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")
    day = ['월', '화', '수', '목', '금', '토', '일']
    
    new_content = ""
    # check if the content is about daily menu
    if 'COURSE' in content:
        new_content += f"*{dt.strftime('%Y년 %m월 %d일 ')} {day[dt.weekday()]}요일"
        # add lunch or dinner
        if dt.hour < 12:
            new_content += " 점심 메뉴*\n"
        elif dt.hour < 19:
            new_content += " 저녁 메뉴*\n"
        else:
            return content
    new_content += content
    
    return new_content
    

def sendMessage(client, channel, message):
    client.chat_postMessage(channel=channel, text=message)


def sendImageAttachments(client, channel, message, url):
    '''
    In order to send images, argument attachments is required. 
    attachments is a list of dictionaries, each dictionary contains title and image_url.
    '''
    attachments = []

    if len(url) == 4: # weekday lunch menu & dinner menu (Monday to Thursday)
        for i in range(2):
            if i == 0:
                attachment = {"title": "COURSE1/5", "image_url": url[i]}
            else:
                attachment = {"title": "COURSE2/4", "image_url": url[i]}
            attachments.append(attachment)
    elif len(url) == 2: # Friday dinner menu
        attachment = {"title": "COURSE1", "image_url": url[0]}
        attachments.append(attachment)
    else: # weekly menu table or others
        for i in range(len(url)):
            attachment = {"title": "", "image_url": url[i]}
            attachments.append(attachment)

    client.chat_postMessage(channel=channel, text=message, attachments=attachments)


def sendImageBlocks(client, channel, message, url):
    '''
    In order to send images, argument blocks is required. 
    blocks is a list of dictionaries, each dictionary contains type, image_url, and alt_text.
    '''
    blocks = []

    if len(url) == 4: # weekday lunch menu & dinner menu (Monday to Thursday)
        for i in range(2):
            block = {"type": "image", "image_url": url[i], "alt_text": url[i].split('/')[-1]}
            blocks.append(block)
    elif len(url) == 2: # Friday dinner menu
        block = {"type": "image", "image_url": url[0], "alt_text": url[0].split('/')[-1]}
        blocks.append(block)
    else: # weekly menu table or others
        for i in range(len(url)):
            block = {"type": "image", "image_url": url[i], "alt_text": url[i].split('/')[-1]}
            blocks.append(block)

    client.chat_postMessage(channel=channel, text=message, blocks=blocks)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_path', type=str, default='post_logs', help='DB path')
    parser.add_argument('--slack_channel_name', type=str, default='#naver-b1-menu', help='Slack channel name to upload posts')
    parser.add_argument('--sleep_time', type=int, default=10, help='sleep time in minute')
    args = parser.parse_args()
    
    # set up slack client
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path = env_path)

    slack_client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
    slack_channel_name = args.slack_channel_name

    # set up NAVER BAND API
    band_token = os.environ['BAND_ACCESS_TOKEN']
    band_id = bc.getBandInfo(band_token=band_token)

    # set up DB
    db_path = args.db_path
    sleep_time = args.sleep_time # in unit of minute
    
    # get posts from BAND per 10 minutes 
    while (1):
        band_post = bc.getBandPost(target_id=band_id, band_token=band_token) # get maximum 20 posts

        for i, item in enumerate(band_post['result_data']['items']):
            # check only 2 latest posts
            if i == 2:
                break

            # get processed data as dict
            temp = bc.makeData(item)  
            postkey = temp.get('postkey')
            create_date = temp.get('createdate')
            content = temp.get('content')
            photos = temp.get('photos')
                                    
            # check if the post already exists in DB
            if searchDB(db_path=db_path, create_date=create_date):
                continue

            # add date to content
            content = add_date_on_content(create_date, content)

            # send message to slack if the post is new and has photos            
            if len(photos) > 0:
                try :
                    sendImageAttachments(client=slack_client, channel=slack_channel_name, message=content, url=photos)
                    insertDB(db_path=db_path, create_date=create_date, content=content)
                except:
                    print("Timeout")

        time.sleep(sleep_time * 60)
