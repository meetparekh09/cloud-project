from google.cloud import vision
import os

uri = "https://images.pexels.com/photos/414612/pexels-photo-414612.jpeg"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="iot-image-extraction-vision.json"

client = vision.ImageAnnotatorClient()
image = vision.types.Image()
image.source.image_uri = uri

response = client.label_detection(image=image)
labels = response.label_annotations
print('Labels:')

for label in labels:
    print(label.description)
