from PIL import Image, ImageDraw
import json
import requests, certifi
from io import BytesIO

PARAM_BACK_IMAGE = {
    "offset_x": 52,
    "offset_y": 52,
    "width": 450,
    "height": 604,
    "radius": 60.0,
    "strokeColor": "black",
    "strokeWidth": 15,
}

PARAM_FRONT_IMAGE = {
    "width": 1772,
    "height": 1181,
}

# load json file
with open("data/memories.json") as file:
    data = json.load(file)


def convertURL(bucket, path):
    return f"https://{bucket}{path}"


def downloadImage(url):
    response = requests.get(url, verify=certifi.where())
    img = Image.open(BytesIO(response.content))
    return img


def resizeWithRatio(image, resizeWidth, resizeHeight):
    if image.width > image.height:
        ratio = resizeWidth / image.width
    else:
        ratio = resizeHeight / image.height

    new_width = int(image.width * ratio)
    new_height = int(image.height * ratio)

    print(new_width, new_height)

    return image.resize((new_width, new_height))


def back_image_mask(im):
    mask = Image.new("L", im.size, "black")
    draw = ImageDraw.Draw(mask)
    x1 = PARAM_BACK_IMAGE["offset_x"]
    y1 = PARAM_BACK_IMAGE["offset_y"]
    x2 = im.width + PARAM_BACK_IMAGE["offset_x"]
    y2 = im.height + PARAM_BACK_IMAGE["offset_y"]
    radius = PARAM_BACK_IMAGE["radius"]
    draw.rounded_rectangle([(x1, y1), (x2, y2)], fill=255, radius=radius)
    out = im.copy().convert("RGBA")
    out.putalpha(mask)
    return out


# convert url to merge bucket and path to obtain the full url
dataFormatted = []
for item in data:
    frontImage = item["frontImage"]
    backImage = item["backImage"]

    frontImage["path"] = convertURL(frontImage["bucket"], frontImage["path"])
    backImage["path"] = convertURL(backImage["bucket"], backImage["path"])

    item.update({"frontImage": frontImage, "backImage": backImage})
    dataFormatted.append(item)

# check if data length is even (we draw 2 images at a time)
if len(dataFormatted) % 2 != 0:
    print("Error: data length is not even")
    exit()

# for each item
for i in range(0, len(dataFormatted), 2):
    item_1 = dataFormatted[i]
    item_2 = dataFormatted[i + 1]

    # download front and back image
    front_image_1 = downloadImage(item_1["frontImage"]["path"])
    back_image_1 = downloadImage(item_1["backImage"]["path"])

    front_image_2 = downloadImage(item_2["frontImage"]["path"])
    back_image_2 = downloadImage(item_2["backImage"]["path"])

    # create new image
    newImage = Image.new(
        "RGBA", (PARAM_FRONT_IMAGE["width"], PARAM_FRONT_IMAGE["height"])
    )

    # first images (resize)
    front_image_1 = resizeWithRatio(
        front_image_1, PARAM_FRONT_IMAGE["width"], PARAM_FRONT_IMAGE["height"]
    )
    back_image_1 = resizeWithRatio(
        back_image_1, PARAM_BACK_IMAGE["width"], PARAM_BACK_IMAGE["height"]
    )

    # apply mask to back_image_1
    back_image_1 = back_image_mask(back_image_1)

    # paste back_image_1 on front_image_1
    front_image_1.paste(
        back_image_1, (PARAM_BACK_IMAGE["offset_x"], PARAM_BACK_IMAGE["offset_y"])
    )

    front_image_1 = front_image_1.convert("RGBA")
    newImage.paste(front_image_1, (0, 0))

    # second images (resize)
    front_image_2 = resizeWithRatio(
        front_image_2, PARAM_FRONT_IMAGE["width"], PARAM_FRONT_IMAGE["height"]
    )
    back_image_2 = resizeWithRatio(
        back_image_2, PARAM_BACK_IMAGE["width"], PARAM_BACK_IMAGE["height"]
    )

    # apply mask to back_image_2
    back_image_2 = back_image_mask(back_image_2)

    # paste back_image_2 on front_image_2
    front_image_2.paste(
        back_image_2, (PARAM_BACK_IMAGE["offset_x"], PARAM_BACK_IMAGE["offset_y"])
    )

    # Convert front_image_2 to RGBA mode
    front_image_2 = front_image_2.convert("RGBA")

    newImage.paste(front_image_2, (front_image_1.width, 0))

    # save new image
    newImage.show()
