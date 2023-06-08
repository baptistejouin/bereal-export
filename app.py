from PIL import Image, ImageDraw
import json
import requests, certifi
from io import BytesIO

# load json file
with open("data/memories.json") as file:
    data = json.load(file)

def convertURL(bucket, path):
    return f"https://{bucket}{path}"

def downloadImage(url):
	response = requests.get(url, verify=certifi.where())
	img = Image.open(BytesIO(response.content))
	return img

# convert url to merge bucket and path to obtain the full url
dataFormatted = []
for item in data:
    frontImage = item['frontImage']
    backImage = item['backImage']

    frontImage['path'] = convertURL(frontImage['bucket'], frontImage['path'])
    backImage['path'] = convertURL(backImage['bucket'], backImage['path'])

    item.update({'frontImage': frontImage, 'backImage': backImage})
    dataFormatted.append(item)

# for each item
for item in dataFormatted:
	# download front image
	frontImage = downloadImage(item['frontImage']['path'])
	# download back image
	backImage = downloadImage(item['backImage']['path'])

	# create new image
	newImage = Image.new('RGB', (frontImage.width + backImage.width, frontImage.height))
	# paste front image
	newImage.paste(frontImage, (0, 0))
	# paste back image
	newImage.paste(backImage, (frontImage.width, 0))

	# save new image
	newImage.show()