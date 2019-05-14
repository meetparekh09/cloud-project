#!/usr/bin/python

import datetime
import time
import jwt
import paho.mqtt.client as mqtt
from lxml import html
import requests
from bs4 import BeautifulSoup
import re
import sys
import json
from multiprocessing import Process


def main(device_number, tagsList, numImageTag = 50, limit = 250):
    ssl_private_key_filepath = './rsa_private.pem'
    ssl_algorithm = 'RS256' # Either RS256 or ES256
    root_cert_filepath = './roots.pem'
    project_id = 'iot-image-extraction'
    gcp_location = 'us-central1'
    registry_id = 'image-extracters'
    device_id = 'image-extracter-'+str(device_number)


    cur_time = datetime.datetime.utcnow()

    def create_jwt():
        token = {
        'iat': cur_time,
        'exp': cur_time + datetime.timedelta(minutes=60),
        'aud': project_id
        }

        with open(ssl_private_key_filepath, 'r') as f:
            private_key = f.read()

        return jwt.encode(token, private_key, ssl_algorithm)

    _CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, gcp_location, registry_id, device_id)
    _MQTT_TOPIC = '/devices/{}/events'.format(device_id)

    client = mqtt.Client(client_id=_CLIENT_ID)

    client.username_pw_set(
        username='unused',
        password=create_jwt())

    def error_str(rc):
        return '{}: {}'.format(rc, mqtt.error_string(rc))

    def on_connect(unusued_client, unused_userdata, unused_flags, rc):
        print('on_connect', error_str(rc))

    def on_publish(unused_client, unused_userdata, unused_mid):
        print('on_publish')

    client.on_connect = on_connect
    client.on_publish = on_publish

    client.tls_set(ca_certs=root_cert_filepath, tls_version=2) # Replace this with 3rd party cert if that was used when creating registry
    client.connect('mqtt.googleapis.com', 8883)
    client.loop_start()


    ###################################################################################################################

    instagram_url="https://www.instagram.com/explore/tags/"
    dataframe = []
    # allDescriptionTuple = []

    print(tagsList)

    for tag in tagsList:
        page=requests.get(instagram_url + tag[1:] + '/')
        tree=html.fromstring(page.content)


        soup = BeautifulSoup(page.content, "lxml")
        script_tag = soup.find('script', text=re.compile('window\._sharedData'))
        json_data = script_tag.string.partition('=')[-1].strip(' ;')
        try:
            json_string = json.loads(json_data)
        except NameError as e:
            print('error has occured tag name:', tag)
            print(e)
            continue
        except:
            continue

        nodeList = json_string["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]
        count = 0
        for index, node in enumerate(nodeList):

            textList = []
            edgesList = node["node"]["edge_media_to_caption"]["edges"]
            for edges in edgesList:
                textList.append(edges["node"]["text"])

            url = node["node"]["display_url"]

            if len(textList) > 0:
                hashtagList = [ t for t in textList[0].split() if t.startswith('#') ]
                if len(hashtagList) > 0 :
                    dataframe.append({"hash-tag": tag, "url": url, "hash-tag-list": hashtagList})
                    count += 1
            if count >= numImageTag:
                break


    # print(dataframe)

    send_count = 0
    for data in dataframe:
        payload = json.dumps(data)
        client.publish(_MQTT_TOPIC, payload, qos=1)
        send_count += 1
        if send_count >= limit:
            break

    ###################################################################################################################


    client.loop_stop()


# reading hashtags from file
with open('text.txt','r') as tagsfile:
  tags = tagsfile.read()
tagsList = tags.split('\n')


if __name__ == '__main__':
    process_list = []
    for i in range(10):
        p = Process(target=main, args=(i+1, tagsList[0+i*5:i*5+5], 5, 1))
        process_list.append(p)
        p.start()

    for p in process_list:
        p.join()
