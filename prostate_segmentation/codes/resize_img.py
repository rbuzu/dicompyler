from PIL import Image

basewidth = 400
img = Image.open('my-0.png')
img = img.convert("RGBA")
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize))

pixdata = img.load()
width, height = img.size

for y in range(height):
    for x in range(width):
        if pixdata[x, y] == (0, 0, 0, 255):
            pixdata[x, y] = (255, 255, 255, 0)

img.save('sompic.png', "PNG")
