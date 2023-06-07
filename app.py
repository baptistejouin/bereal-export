from PIL import Image

image = Image.open("./data/primary.jpg")
print(image.format, image.size, image.mode)