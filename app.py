from PIL import Image, ImageDraw
import json
import requests, certifi
from io import BytesIO


PARAM_FRONT_IMAGE = {
    "width": 1772,
    "height": 1181,
}

PARAM_BACK_IMAGE = {
    "offset_x": int(0.021 * PARAM_FRONT_IMAGE["height"]),
    "offset_y": int(0.021 * PARAM_FRONT_IMAGE["height"]),
    "width": 0.3095 * PARAM_FRONT_IMAGE["width"],
    "height": 0.3095 * PARAM_FRONT_IMAGE["height"],
    "radius": 0.0222 * PARAM_FRONT_IMAGE["width"],
    "strokeColor": "black",
    "strokeWidth": 5,
}

# load json file
with open("data/memories.json") as file:
    data = json.load(file)


def convertURL(bucket, path):
    return f"https://{bucket}{path}"


def downloadImage(url):
    response = requests.get(url, verify=certifi.where())
    img = Image.open(BytesIO(response.content)).convert("RGBA")
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


def make_rounded_mask(im):
    # rounded the image
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), (im.width, im.height)], fill=255, radius=PARAM_BACK_IMAGE["radius"]
    )
    out = im.copy()
    out.putalpha(mask)

    # add black stroke
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [(0, 0), (im.width, im.height)],
        fill=0,
        radius=PARAM_BACK_IMAGE["radius"],
        outline=255,
        width=PARAM_BACK_IMAGE["strokeWidth"],
    )
    out.paste(PARAM_BACK_IMAGE["strokeColor"], mask=mask)
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
        "RGB", (PARAM_FRONT_IMAGE["width"], PARAM_FRONT_IMAGE["height"])
    )

    # first images (resize)
    front_image_1 = resizeWithRatio(
        front_image_1, PARAM_FRONT_IMAGE["width"], PARAM_FRONT_IMAGE["height"]
    )
    back_image_1 = resizeWithRatio(
        back_image_1, PARAM_BACK_IMAGE["width"], PARAM_BACK_IMAGE["height"]
    )

    # apply mask to back_image_1
    back_image_1 = make_rounded_mask(back_image_1)

    # newImage.paste(front_image_1, (0, 0), front_image_1)
    # newImage.show()
    # exit()

    # paste back_image_1 on front_image_1
    front_image_1.paste(
        back_image_1,
        (PARAM_BACK_IMAGE["offset_x"], PARAM_BACK_IMAGE["offset_y"]),
        back_image_1,
    )

    newImage.paste(front_image_1, (0, 0), front_image_1)

    # second images (resize)
    front_image_2 = resizeWithRatio(
        front_image_2, PARAM_FRONT_IMAGE["width"], PARAM_FRONT_IMAGE["height"]
    )
    back_image_2 = resizeWithRatio(
        back_image_2, PARAM_BACK_IMAGE["width"], PARAM_BACK_IMAGE["height"]
    )

    # apply mask to back_image_2
    back_image_2 = make_rounded_mask(back_image_2)

    # paste back_image_2 on front_image_2
    front_image_2.paste(
        back_image_2,
        (PARAM_BACK_IMAGE["offset_x"], PARAM_BACK_IMAGE["offset_y"]),
        back_image_2,
    )

    newImage.paste(front_image_2, (front_image_1.width, 0), front_image_2)

    # save new image
    newImage.show()
