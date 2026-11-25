import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import cv2, numpy as np, threading, subprocess, shutil, os, tempfile, time
from engine import render

class Studio:
    def __init__(self,root):
        self.root=root; root.title('ASCII Studio'); root.geometry('1100x780'); self.path=None; self.cap=None; self.rgb=None; self.previous=None; self.start=time.monotonic(); self.color=(90,220,255); self.busy=False
        root.configure(bg='#111111'); style=ttk.Style(); style.theme_use('clam'); style.configure('.',background='#222222',foreground='white'); style.configure('TScale',background='#222222'); style.configure('TCombobox',foreground='black')
        panel=ttk.Frame(root,padding=16); panel.pack(side='left',fill='y'); self.view=tk.Label(root,bg='black'); self.view.pack(side='right',fill='both',expand=True)
        ttk.Label(panel,text='ASCII STUDIO',font=('Arial',20,'bold')).pack(pady=8); ttk.Button(panel,text='Open image or video',command=self.open).pack(fill='x'); self.vars={}
        for key,lo,hi,val in [('columns',30,240,100),('brightness',-100,100,15),('contrast',.3,2.5,1.2),('saturation',0,2.5,1.2)]:
            v=tk.DoubleVar(value=val); self.vars[key]=v; ttk.Label(panel,text=key.title()).pack(anchor='w',pady=(10,0)); ttk.Scale(panel,from_=lo,to=hi,variable=v).pack(fill='x')
        self.chars=tk.StringVar(value=' .,:;irsXA253hMHGS#9B&@'); ttk.Label(panel,text='Characters (dark to light)').pack(anchor='w'); ttk.Entry(panel,textvariable=self.chars).pack(fill='x'); self.palette=tk.StringVar(value='Original'); ttk.Combobox(panel,textvariable=self.palette,values=['Original','Monochrome','Custom'],state='readonly').pack(fill='x',pady=6); ttk.Button(panel,text='Custom color',command=self.pick).pack(fill='x')
        self.flags={}
        for k in ['glitch','flicker','trail','loop']:
            self.flags[k]=tk.BooleanVar(value=k=='loop'); ttk.Checkbutton(panel,text=k.title(),variable=self.flags[k]).pack(anchor='w')
        self.format=tk.StringVar(value='Vertical 1080 × 1920'); ttk.Combobox(panel,textvariable=self.format,values=['Vertical 1080 × 1920','Square 1080 × 1080','Landscape 1920 × 1080'],state='readonly').pack(fill='x',pady=8)
        self.seconds=tk.StringVar(value='5'); ttk.Label(panel,text='Still animation duration (seconds)').pack(); ttk.Entry(panel,textvariable=self.seconds).pack(fill='x');
        for ext in ['png','gif','mp4']: ttk.Button(panel,text='Export '+ext.upper(),command=lambda e=ext:self.export(e)).pack(fill='x',pady=3)
        self.status=ttk.Label(panel,text='Open a file to begin',wraplength=230); self.status.pack(pady=8); self.tick()
    def pick(self):
        c,_=colorchooser.askcolor();
        if c: self.color=tuple(map(int,c)); self.palette.set('Custom')
    def settings(self):
        dims={'Vertical 1080 × 1920':(1080,1920),'Square 1080 × 1080':(1080,1080),'Landscape 1920 × 1080':(1920,1080)}; w,h=dims[self.format.get()]; s={k:v.get() for k,v in self.vars.items()}; s.update({k:v.get() for k,v in self.flags.items()}); s.update(width=w,height=h,columns=int(s['columns']),chars=self.chars.get(),palette=self.palette.get(),color=self.color); return s
    def open(self):
        p=filedialog.askopenfilename(filetypes=[('Media','*.png *.jpg *.jpeg *.webp *.bmp *.mp4 *.mov *.avi *.mkv *.webm *.gif'),('All files','*')]);
        if not p:return
        try:
            im=Image.open(p)
            if getattr(im,'n_frames',1)>1: raise ValueError('animated')
            rgb=np.array(im.convert('RGB')); cap=None
        except Exception:
            cap=cv2.VideoCapture(p); ok,bgr=cap.read()
            if not ok: cap.release(); messagebox.showerror('Error','Cannot decode this file'); return
            rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
        if self.cap:self.cap.release()
        self.path=p; self.cap=cap; self.rgb=rgb; self.previous=None; self.start=time.monotonic(); self.status.config(text=os.path.basename(p))
    def tick(self):
        delay=80
        if self.rgb is not None:
            begin=time.monotonic()
            if self.cap:
                fps=self.cap.get(cv2.CAP_PROP_FPS) or 24; delay=max(20,int(1000/fps)); ok,bgr=self.cap.read()
                if not ok and self.flags['loop'].get(): self.cap.set(cv2.CAP_PROP_POS_FRAMES,0); ok,bgr=self.cap.read()
                if ok:self.rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
            s=self.settings(); s['width']//=2;s['height']//=2;s['columns']=min(s['columns'],120); im=render(self.rgb,s,time.monotonic()-self.start,self.previous); self.previous=im; im=im.copy(); im.thumbnail((max(200,self.view.winfo_width()),max(200,self.view.winfo_height()))); self.photo=ImageTk.PhotoImage(im); self.view.config(image=self.photo); delay=max(10,delay-int((time.monotonic()-begin)*1000))
        self.root.after(delay,self.tick)
    def export(self,ext):
        if self.rgb is None or self.busy:return
        p=filedialog.asksaveasfilename(defaultextension='.'+ext,filetypes=[(ext.upper(),'*.'+ext)]);
        if not p:return
        s=self.settings(); rgb=self.rgb.copy(); source=self.path; video=self.cap is not None
        try: seconds=max(.1,min(60,float(self.seconds.get())))
        except ValueError: messagebox.showerror('Error','Enter a valid duration');return
        self.busy=True; self.status.config(text='Exporting…'); threading.Thread(target=self.worker,args=(p,ext,s,rgb,source,video,seconds),daemon=True).start()
    def worker(self,p,ext,s,rgb,source,video,seconds):
        try:
            if ext=='png':render(rgb,s).save(p)
            else:
                ff=shutil.which('ffmpeg')
                if not ff:raise RuntimeError('Install FFmpeg and add it to PATH.')
                cap=cv2.VideoCapture(source) if video else None; fps=(cap.get(cv2.CAP_PROP_FPS) or 24) if cap else 24; prev=None
                with tempfile.TemporaryDirectory() as tmp:
                    i=0
                    try:
                        while True:
                            if cap:
                                ok,bgr=cap.read()
                                if not ok:break
                                rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
                            elif i>=round(seconds*fps):break
                            t=i/fps
                            if not video and s['loop']: t=2*np.pi*i/max(1,round(seconds*fps))
                            im=render(rgb,s,t,prev);prev=im;im.save(os.path.join(tmp,f'{i:08d}.png'));i+=1
                    finally:
                        if cap:cap.release()
                    if not i:raise RuntimeError('No frames decoded')
                    # Ping-pong video avoids a hard cut between end and beginning.
                    if video and s['loop'] and i>2:
                        for j,k in enumerate(range(i-2,0,-1),i): shutil.copyfile(os.path.join(tmp,f'{k:08d}.png'),os.path.join(tmp,f'{j:08d}.png'))
                    cmd=[ff,'-y','-framerate',str(fps),'-i',os.path.join(tmp,'%08d.png')]
                    cmd+=['-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart'] if ext=='mp4' else ['-filter_complex','[0:v]split[a][b];[a]palettegen[p];[b][p]paletteuse','-loop','0' if s['loop'] else '-1']
                    subprocess.run(cmd+[p],check=True,capture_output=True)
            msg='Saved: '+os.path.basename(p)
        except Exception as e:msg='Export failed: '+str(e)
        self.root.after(0,lambda:self.done(msg))
    def done(self,msg):self.busy=False;self.status.config(text=msg)

if __name__=='__main__':
    root=tk.Tk(); Studio(root);root.mainloop()
