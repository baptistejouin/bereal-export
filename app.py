from PIL import Image, ImageDraw, ImageFont
import json
import requests, certifi
from io import BytesIO
import argparse
import os

ANTI_ALIASING = 2

PARAM_FRONT_IMAGE = {
    "width": 1500 * ANTI_ALIASING,
    "height": 1000 * ANTI_ALIASING,
}

PARAM_BACK_IMAGE = {
    "offset_x": int(0.021 * PARAM_FRONT_IMAGE["height"]),
    "offset_y": int(0.021 * PARAM_FRONT_IMAGE["height"]),
    "width": 0.3995 * PARAM_FRONT_IMAGE["width"],
    "height": 0.3995 * PARAM_FRONT_IMAGE["height"],
    "radius": 0.0222 * PARAM_FRONT_IMAGE["width"],
    "strokeColor": "black",
    "strokeWidth": int(0.00282 * PARAM_FRONT_IMAGE["width"]),
}


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


def add_beareal_moment(im, moment, isLate):
    beareal_moment = moment
    if isLate:
        beareal_moment = beareal_moment + " (late)"
    else:
        beareal_moment = beareal_moment + " (real)"

    text = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(text)
    font = ImageFont.truetype("./assets/font/genera.ttf", im.width // 35)
    draw.text((0, 0), beareal_moment, fill=255, font=font)
    out = im.copy()
    out.paste(
        text,
        (
            im.width - PARAM_BACK_IMAGE["offset_x"] * 10,
            im.height - PARAM_BACK_IMAGE["offset_y"] * 2,
        ),
        text,
    )

    return out


def process_image_pair(item_1, item_2):
    front_image_1 = downloadImage(item_1["primary"]["url"])
    back_image_1 = downloadImage(item_1["secondary"]["url"])
    front_image_2 = downloadImage(item_2["primary"]["url"])
    back_image_2 = downloadImage(item_2["secondary"]["url"])

    front_image_1 = resizeWithRatio(
        front_image_1, PARAM_FRONT_IMAGE["width"], PARAM_FRONT_IMAGE["height"]
    )
    front_image_1 = add_beareal_moment(
        front_image_1, item_1["memoryDay"], item_1["isLate"]
    )

    back_image_1 = resizeWithRatio(
        back_image_1, PARAM_BACK_IMAGE["width"], PARAM_BACK_IMAGE["height"]
    )
    back_image_1 = make_rounded_mask(back_image_1)
    front_image_1.paste(
        back_image_1,
        (PARAM_BACK_IMAGE["offset_x"], PARAM_BACK_IMAGE["offset_y"]),
        back_image_1,
    )

    front_image_2 = resizeWithRatio(
        front_image_2, PARAM_FRONT_IMAGE["width"], PARAM_FRONT_IMAGE["height"]
    )
    front_image_2 = add_beareal_moment(
        front_image_2, item_2["memoryDay"], item_2["isLate"]
    )

    back_image_2 = resizeWithRatio(
        back_image_2, PARAM_BACK_IMAGE["width"], PARAM_BACK_IMAGE["height"]
    )
    back_image_2 = make_rounded_mask(back_image_2)
    front_image_2.paste(
        back_image_2,
        (PARAM_BACK_IMAGE["offset_x"], PARAM_BACK_IMAGE["offset_y"]),
        back_image_2,
    )

    return front_image_1, front_image_2


if __name__ == "__main__":
    # Create a parser
    parser = argparse.ArgumentParser()

    # Add a parameter
    parser.add_argument("-j", "--json", help="JSON input path", required=True)
    parser.add_argument("-o", "--output", help="Output directory path", required=True)

    # Parse the argument
    args = parser.parse_args()

    # load json file
    with open(args.json) as file:
        data = json.load(file)["data"]

    # check if data length is even (we draw 2 images at a time)
    if len(data) % 2 != 0:
        print("Error: data length is not even")
        exit()

    # for each item
    for i in range(0, len(data), 2):
        item_1 = data[i]
        item_2 = data[i + 1]

        front_image_1, front_image_2 = process_image_pair(item_1, item_2)

        newImage = Image.new(
            "RGB", (PARAM_FRONT_IMAGE["width"], PARAM_FRONT_IMAGE["height"])
        )
        newImage.paste(front_image_1, (0, 0), front_image_1)
        newImage.paste(front_image_2, (front_image_1.width, 0), front_image_2)

        # the only way to get something like anti-aliasing (for outline and text)
        newImage = newImage.resize(
            (newImage.width // ANTI_ALIASING, newImage.height // ANTI_ALIASING),
            Image.LANCZOS,
        )

        # get file path
        file_path = os.path.join(args.output, f"{i}.jpg")

        newImage.save(file_path, "JPEG", quality=100, optimize=True)
        print(f"Image {(i+2)//2}/{len(data)//2} saved")
    print(f"\nDone, {len(data)//2} images saved in {args.output}")
