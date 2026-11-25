import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from functools import lru_cache

@lru_cache(maxsize=32)
def font(size):
    for name in ('DejaVuSansMono.ttf','Consolas.ttf','Menlo.ttc'):
        try: return ImageFont.truetype(name,size)
        except OSError: pass
    return ImageFont.load_default(size=size)

def render(rgb, s, t=0, previous=None):
    W,H=s['width'],s['height']; cols=s['columns']; cw=W/cols; f=font(max(6,int(cw/0.61))); ch=max(1,int(cw*1.65)); rows=max(1,H//ch)
    h,w=rgb.shape[:2]; scale=min(cols/w,rows/h*ch/cw); nw=max(1,min(cols,round(w*scale))); nh=max(1,min(rows,round(h*scale*cw/ch)))
    small=cv2.resize(rgb,(nw,nh),interpolation=cv2.INTER_AREA).astype(np.float32)
    lum=small@np.array([.2126,.7152,.0722]); small=lum[:,:,None]+(small-lum[:,:,None])*s['saturation']; small=np.clip((small-127.5)*s['contrast']+127.5+s['brightness'],0,255)
    grid=np.zeros((rows,cols,3),np.float32); y=(rows-nh)//2;x=(cols-nw)//2;grid[y:y+nh,x:x+nw]=small
    if s['glitch']:
        for j in range(rows):
            if np.sin(j*17+t*13)>.96: grid[j]=np.roll(grid[j],int(4*np.sin(t*8+j)),axis=0)
    l=grid@np.array([.2126,.7152,.0722]); chars=s['chars'] or ' .:-=+*#%@'; idx=np.clip((l/255*(len(chars)-1)).astype(int),0,len(chars)-1)
    if s['palette']=='Monochrome': grid=np.repeat(l[:,:,None],3,axis=2)
    elif s['palette']=='Custom': grid=l[:,:,None]/255*np.array(s['color'])
    if s['flicker']: grid*=.85+.15*np.sin(t*18+np.arange(rows)[:,None,None]*.7)
    out=Image.new('RGB',(W,H)); d=ImageDraw.Draw(out)
    for j in range(rows):
        for i in range(cols):
            if l[j,i]>5 and chars[idx[j,i]]!=' ': d.text((int(i*cw),j*ch),chars[idx[j,i]],font=f,fill=tuple(np.clip(grid[j,i],0,255).astype(int)),anchor='lt')
    if s['trail'] and previous is not None and previous.size==out.size: out=Image.blend(out,previous,.28)
    return out
