import base64
import colorsys
import statistics
from pathlib import Path
from functools import lru_cache

import cv2
import hrml
import jinja2
import requests
import numpy as np

from flask import request

此处 = Path(__file__).absolute().parent


模板 = jinja2.Template(
    hrml.masturbate(
        open(此处/'模板/模板.hrml', encoding='utf8').read()
    )
)

MB = 1024*1024

def 中正(img):
    r, c = img.shape[:2]
    d = abs(r-c)//2
    if r > c:
        return img[d:d+c, :]
    else:
        return img[:, d:d+r]

def 主要颜色(img):
    img = img[:, :, :3]
    img = cv2.resize(img, (32, 32))
    img //= 16
    img *= 16
    r, c = img.shape[:2]
    img = img.reshape((r*c, 3))
    color = statistics.mode(map(tuple, img))
    return np.array(color, dtype=np.int32)


@lru_cache(maxsize=16)
def 下载(url, 大小限制):
    r = requests.get(url, stream=True)
    data = r.raw.read(大小限制)
    return data


@lru_cache(maxsize=4)
def 真源(url):
    img_data = 下载(url, 10*MB)
    if len(img_data) == 10*MB:
        raise Exception('太大了，不行！')
    img = cv2.imdecode(np.frombuffer(img_data, np.uint8), -1)   # 这里可能会被打爆2333
    img = 中正(img)
    return img


@lru_cache(maxsize=512)
def 源(url, limit):
    img = 真源(url)
    backcolor = 主要颜色(img)[::-1]
    if img.shape[0] > limit:
        img = cv2.resize(img, (limit, limit))
    good, data = cv2.imencode('.webp', img, [cv2.IMWRITE_WEBP_QUALITY, 75])
    if not good:
        raise Exception('imencode fail')
    data = base64.b64encode(data).decode()
    return data, backcolor


def color(h):
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return r, g, b

def 提取参数(req: request):
    form = dict(req.args)
    print(form)
    return form


@lru_cache(maxsize=1024)
def 生(ver: str = None, url: str = None, txt: str = 'Operater', size=32, border=3, barlen='auto', fontsize=15, barradius=5, scale=1, fontcolor: color = 'auto', shadow=0.5, backcolor: color = 'auto', anime=0.5):
    if barlen == 'auto':
        l = len(txt) + len([x for x in txt if ord(x) > 127])*0.84
        barlen = fontsize*l*0.55 + 2.6*border

    size, border, barlen, fontsize, barradius = [int(x*float(scale)) for x in (size, border, barlen, fontsize, barradius)]

    colors = []
    bb, b_color = 源(url, (size-2*border)*4)
    if backcolor == 'auto':
        backcolor = b_color
    elif isinstance(backcolor, str):
        colors = backcolor.split(',')
    else:
        backcolor = np.array(color(backcolor), dtype=float)

    if len(colors) == 2:
        color1 = list(color(colors[0]))
        color2 = list(color(colors[1]))
        backcolor = np.array(color2, dtype=float)
    else:
        backcolor = np.array(color(backcolor), dtype=float)
        h, l, s = colorsys.rgb_to_hls(*backcolor/255)
        color1 = np.array(colorsys.hls_to_rgb(h, l+0.02, s))*255
        color2 = np.array(colorsys.hls_to_rgb(h, l-0.06, s))*255

    if fontcolor == 'auto':
        if backcolor.mean() > 214:
            fontcolor = (33, 33, 33)
        else:
            fontcolor = (255, 255, 255)

    if txt == '':
        barlen = 0
    s = 模板.render(
        size=size,
        border=border,
        shadow=shadow,
        barradius=barradius,
        barlen=barlen,
        bartxt=txt,
        color1=color1,
        color2=color2,
        fontcolor=color(fontcolor),
        fontsize=fontsize,
        anime=anime,
        radius=99999,
        b64='data:image/webp;base64,'+bb,
    )
    return s
