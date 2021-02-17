from PIL import Image, ImageFont, ImageDraw, ImageColor
from cv2 import cv2
import numpy as np
import json, re, random

config = json.load(open('config.json'))
fonts = {}
for font in config['fonts']:
    fonts[font] = ImageFont.truetype(config['fonts'][font], size=config['defaults']['size'])

size = (1366,768)
fps = 60
fourcc = cv2.VideoWriter_fourcc(*"XVID")
video = cv2.VideoWriter("output.avi", fourcc, fps, size)

curfont = fonts[config['defaults']['font']]
curshake = 0
curcolor = (255,255,255)
curmargin = 0

def irandom(intensity):
    return int((random.random() * (intensity * 2)) - (intensity / 2))

pat = re.compile('<(.*?)>')

script = open('script.txt', 'r').read().split("\n")
for line in script:

    brack, nbLINE = list(filter(None, pat.split(line)))
    print(nbLINE)
    brack = brack.split(";")
    writeSpeed, pauseTime = float(brack[0]), float(brack[1])
    ext = brack[2:]
    for LINE in ext:
        cmd = LINE.split(":")
        if cmd[0] == "shake":
            curshake = float(cmd[1])
        if cmd[0] == "color":
            curcolor = ImageColor.getrgb(f"#{cmd[1]}")
        if cmd[0] == "fnt":
            curfont = fonts[cmd[1]]
        if cmd[0] == "mar":
            curmargin = int(cmd[1])
    #print(curshake, curcolor, curfont)
    
    #framedraw.text((0,0), nbLINE, fill=curcolor, font=curfont)

    charlen = len(nbLINE)
    charPerSeconds = writeSpeed / charlen
    CPF = max(1,int(fps * charPerSeconds))

    pauseFrames = int(pauseTime * fps)
    
    draws = [nbLINE[:n+1] for n,b in enumerate(nbLINE)]
    for I, c in enumerate(draws):
        if I == len(draws)-1:
            cpfo = pauseFrames
        else:
            cpfo = 0
        for _ in range(CPF+cpfo):
            frame = Image.new("RGB", size)
            framedraw = ImageDraw.Draw(frame)

            x,y = 0,0

            for char in c:
                xo, yo = irandom(curshake), irandom(curshake)
                charw, charh = framedraw.textsize(char, font=curfont)
                framedraw.text((x+xo, y+yo), char, fill=curcolor, font=curfont)
                x += charw + curmargin
                if x+charw+curmargin >= size[0]:
                    x = 0
                    y += charh
        
            video.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
    # for _ in range(pauseFrames):
    #     video.write(cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR))
video.release()