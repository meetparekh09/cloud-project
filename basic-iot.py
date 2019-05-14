#!/usr/bin/python

import datetime
import time
import jwt
import paho.mqtt.client as mqtt


# Define some project-based variables to be used below. This should be the only
# block of variables that you need to edit in order to run this script
# topic image-links
# registry name: image-extracters

ssl_private_key_filepath = './rsa_private.pem'
ssl_algorithm = 'RS256' # Either RS256 or ES256
root_cert_filepath = './roots.pem'
project_id = 'iot-image-extraction'
gcp_location = 'us-central1'
registry_id = 'image-extracters'
device_id = 'image-extracter-1'
topic_id = 'image-links'
# projects/iot-image-extraction/topics/image-links

# end of user-variables

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
# # authorization is handled purely with JWT, no user/pass, so username can be whatever
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

# Could set this granularity to whatever we want based on device, monitoring needs, etc

for i in range(1, 11):


    payload = '{{"message": "hello-world-{}"}}'.format(i)

    client.publish(_MQTT_TOPIC, payload, qos=1)

    print("{}\n".format(payload))

    time.sleep(1)

client.loop_stop()
