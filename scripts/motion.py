"""Deterministic 3D scientific motion, projected and composited in software.

World coordinates and wave fields are evaluated for every frame. A rendered
Blender studio plate supplies the background. Geometry is rasterized with
shaded parcel sprites and depth-sorted paths; this is not a Cycles frame render.
"""
from pathlib import Path
from functools import lru_cache
import math,json,subprocess,sys,os
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
W,H=1920,1080;FPS=30
C=(62,185,239);G=(247,161,64);S=(136,162,188);WHITE=(231,240,247)
BG=None;BGHI=None;AA=2
font_paths=[os.environ.get('SOUND_FONT_PATH',''),'/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf','C:/Windows/Fonts/arial.ttf']
font=next((ImageFont.truetype(p,25) for p in font_paths if p and Path(p).is_file()),None)
if font is None:font=ImageFont.load_default(size=25)
def unit(a):return a/np.linalg.norm(a)
class View:
 def __init__(self,particle=False,wide=False):
  self.target=np.array([0.,0.,1.2]);eye=np.array([0,-14,5] if particle else [7,-12,8]);f=unit(self.target-eye);self.right=unit(np.cross(f,[0,0,1]));self.up=np.cross(self.right,f);self.f=f;self.scale=W/(11 if particle else 15 if wide else 13)
 def project(self,p):
  a=np.asarray(p)-self.target
  return np.stack((W/2+(a@self.right)*self.scale,H/2-(a@self.up)*self.scale),axis=-1)
 def depth(self,p):return (np.asarray(p)-self.target)@self.f

@lru_cache(maxsize=256)
def sprite(radius,color):
 r=max(2,int(radius));n=r*2+4;y,x=np.mgrid[:n,:n];xx=(x-(n-1)/2)/r;yy=(y-(n-1)/2)/r;rr=xx*xx+yy*yy
 z=np.sqrt(np.maximum(0,1-rr));light=np.clip(-.4*xx-.6*yy+.7*z,0,1)
 spec=np.exp(-((xx+.32)**2+(yy+.37)**2)/.045)*.7
 rgb=np.array(color)[None,None,:]*(.33+.67*light[:,:,None])+255*spec[:,:,None]
 a=np.clip((1-np.sqrt(rr))*r+1,0,1)*255
 out=np.dstack((np.clip(rgb,0,255).astype('uint8'),a.astype('uint8')))
 return Image.fromarray(out,'RGBA')

class Draw:
 def __init__(self,v):self.v=v;self.items=[]
 def line(self,pts,c=C,width=3,alpha=255):self.items.append(('line',np.array(pts,float),c,width,alpha))
 def ball(self,p,r=.06,c=C,alpha=255):self.items.append(('ball',np.array(p,float),c,r,alpha))
 def poly(self,pts,c):self.items.append(('poly',np.array(pts,float),c,0,255))
 def ring(self,center,r,c=C,plane='xy',a=0,b=2*math.pi,width=3):
  ang=np.linspace(a,b,100);base=np.zeros((100,3))
  if plane=='xy':base[:,0]=r*np.cos(ang);base[:,1]=r*np.sin(ang)
  else:base[:,1]=r*np.cos(ang);base[:,2]=r*np.sin(ang)
  self.line(base+center,c,width)
 def arrow(self,a,b,c=C):
  a=np.array(a,float);b=np.array(b,float);self.line([a,b],c,4)
  v=unit(a-b);side=unit(np.cross(v,[0,0,1])) if abs(v[2])<.99 else np.array([0,1,0])
  self.line([b+.25*v+.13*side,b,b+.25*v-.13*side],c,4)
 def wall(self,x,y0,y1,z=2.5):
  self.poly([(x,y0,.05),(x,y1,.05),(x,y1,z),(x,y0,z)],(54,77,103))
  self.line([(x,y0,.05),(x,y0,z),(x,y1,z),(x,y1,.05)],S,3)
 def render(self):
  im=BGHI.copy();dr=ImageDraw.Draw(im)
  for typ,p,c,size,alpha in sorted(self.items,key=lambda x:float(np.mean(self.v.depth(x[1]))),reverse=True):
   xy=self.v.project(p)*AA
   if typ=='ball':
    x,y=xy;sp=sprite(round(size*self.v.scale*AA),tuple(c));im.paste(sp,(round(x-sp.width/2),round(y-sp.height/2)),sp)
   elif typ=='poly':dr.polygon([tuple(x) for x in xy],fill=c)
   else:
    pts=[tuple(x) for x in xy];dr.line(pts,fill=tuple(int(v*.4) for v in c),width=(int(size)+3)*AA,joint='curve');dr.line(pts,fill=c,width=int(size)*AA,joint='curve')
  return im.resize((W,H),Image.Resampling.LANCZOS)

def wave_color(v):
 u=np.clip((v+1)/2,0,1)
 return tuple(int(a+(b-a)*u) for a,b in zip(C,G))

@lru_cache(maxsize=8)
def field(kind):
 xs=np.linspace(.12,4.3,35) if kind.startswith('diffraction') else np.linspace(-3.8,4,49)
 ys=np.linspace(-3,3,43);x,y=np.meshgrid(xs,ys);pts=np.stack([x.ravel(),y.ravel(),np.full(x.size,.65)],axis=1)
 if kind.startswith('diffraction'):
  half=1.7 if kind=='diffraction_wide' else .7
  ap=np.linspace(-half,half,81);dist=np.sqrt(x[:,:,None]**2+(y[:,:,None]-ap)**2);f=np.sum(np.exp(1j*2*math.pi/1.5*dist)/dist,axis=-1)/81
  return pts,f.ravel()/np.max(np.abs(f))
 fields=[]
 for i,sy in enumerate([-1.3,1.3]):
  wavelength=3.6/2.2 if kind=='beats' and i==1 else 1.8
  dist=np.maximum(.35,np.sqrt((x+3)**2+(y-sy)**2));fields.append((np.exp(1j*2*math.pi/wavelength*dist)/dist).ravel())
 norm=max(np.max(np.abs(fields[0])+np.abs(fields[1])),1)
 return pts,fields[0]/norm,fields[1]/norm

def along(points,distance):
 for a,b in zip(points,points[1:]):
  a=np.array(a,float);b=np.array(b,float);l=np.linalg.norm(b-a)
  if distance<=l:return a+(b-a)*max(0,distance)/l
  distance-=l
 return None

def geometry(name,t):
 v=View(name=='particle',name=='doppler');d=Draw(v);w=2*math.pi*.2
 note='Slow-motion scientific visualization / illustrative scale'
 if name in ['source','final']:
  for x in [-3.3,-2.95]:
   ang=np.linspace(0,2*math.pi,90);p=np.stack([np.full(90,x),np.cos(ang),1.5+np.sin(ang)],axis=1);d.poly(p,(38,53,73));d.line(p,S,4)
  xp=-2.9+.08*math.sin(w*t);d.ring((xp,0,1.5),.94,G,'yz',width=5)
  for i in range(5):
   x=-2.9+((i*1.25+.25*t)%6.25);d.ring((x,0,1.5),.83,C,'yz')
  d.arrow((-2,-1.5,.2),(3,-1.5,.2),G)
 elif name=='particle':
  d.line([(-1.1,0,1),(1.1,0,1)],S,2);d.line([(0,0,.45),(0,0,1.55)],WHITE,3)
  for x in [-.7,.7]:d.line([(x,0,.85),(x,0,1.15)],S,2)
  d.ball((.7*math.sin(w*t),-.08,1),.22,G)
  d.arrow((-3,0,2.35),(3,0,2.35),C)
  # A small travelling marker explicitly distinguishes propagation from parcel motion.
  d.ball((-3+((1.2*t)%6),0,2.35),.065,C)
  note='Gold: one air parcel / White cross: equilibrium / Blue: travelling disturbance / Displacement exaggerated'
 elif name=='pressure':
  k=2*math.pi/2.5
  for q in np.linspace(-4,4,45):
   ph=2*math.pi*.4*t-k*q;x=q+.09*math.sin(ph);col=wave_color(math.cos(ph))
   for y in [-.5,0,.5]:
    for z in [.7,1.2,1.7]:d.ball((x,y,z),.055,col)
  d.arrow((-3,-1.6,.15),(3,-1.6,.15),C)
  note='Amber: positive pressure / Blue: negative pressure / Air-parcel displacement exaggerated'
 elif name in ['frequency','harmonics']:
  x=np.linspace(-4,4,240)
  for j,(f,a) in enumerate([(1,.45),(2,.45),(2,.9)]):
   y=j*1.5-1.5;z=1+a*np.sin(f*x*1.5-2*math.pi*.2*f*t)
   if name=='harmonics' and j==2:
    ph=x*1.5-2*math.pi*.2*t;z=1+.45*np.sin(ph)+.25*np.sin(2*ph)+.12*np.sin(3*ph)
   d.line(np.stack([x,np.full(len(x),y),z],axis=1),G if j==2 else C,3);d.line([(-4,y,1),(4,y,1)],S,1)
  note='Pressure graphs / Graph height is not transverse motion of air'
 elif name=='vacuum':
  for x in [-3,3]:
   d.ring((x+(.08*math.sin(w*t) if x<0 else 0),0,1.4),.7,G if x<0 else S,'yz',width=5)
  for z in [.35,2.45]:
   d.line([(-4,-1,z),(4,-1,z),(4,1,z),(-4,1,z),(-4,-1,z)],S,2)
  for x in [-4,4]:
   for y in [-1,1]:d.line([(x,y,.35),(x,y,2.45)],S,2)
  note='Vacuum schematic / The source vibrates; no acoustic wave crosses the empty space'
 elif name=='media':
  for j,title in enumerate(['AIR','WATER','SOLID']):
   cx=-3+j*3;d.poly([(cx-1.1,-1.2,.2),(cx+1.1,-1.2,.2),(cx+1.1,1.2,.2),(cx-1.1,1.2,.2)],(37,57,78))
   for a in range(6):
    for b in range(3):
     q=cx-.85+a*.34;shift=.1*math.sin(w*t-a*.55);d.ball((q+shift,-.7+b*.7,.85),.07,[C,G,S][j])
  note='Air / Water / Solid - schematic local oscillation, not a quantitative speed comparison'
 elif name=='boundary':
  d.wall(0,-2,2)
  a=(-4,-2,.8);b=(0,0,.8);r=(-4,2,.8);tr=(3.5,1.75,.8);d.arrow(a,b,C);d.arrow(b,r,G);d.arrow(b,tr,C)
  period=10;u=t%period;speed=1.5;arrival=np.linalg.norm(np.array(b)-a)/speed
  p=along([a,b],speed*u)
  if p is not None:d.ball(p,.13,C)
  if u>=arrival:
   for path,col in [([b,r],G),([b,tr],C)]:
    p=along(path,speed*(u-arrival))
    if p is not None:d.ball(p,.11,col)
   d.ball((.02,0,1),.14*math.exp(-2*(u-arrival)),G)
  note='Schematic pulse paths / Arrows do not encode energy fractions'
 elif name in ['diffraction','diffraction_wide','interference','interference_opposite','beats']:
  if name.startswith('diffraction'):
   half=1.7 if name=='diffraction_wide' else .7
   d.wall(0,-3,-half);d.wall(0,half,3);pts,f=field(name);p=np.real(f*np.exp(-1j*2*math.pi*t/3))
   for i in range(4):
    x=-6+((i*1.5+.5*t)%6);d.line([(x,-3,.65),(x,3,.65)],C,2)
   note='Scalar aperture model / Signed pressure / Opening width: '+('2.27 wavelengths' if half>1 else '0.93 wavelengths')
  else:
   pts,f1,f2=field('beats' if name=='beats' else 'interference')
   fa,fb=(2,2.2) if name=='beats' else (.4,.4)
   shift=math.pi if name=='interference_opposite' else 0
   p=np.real(f1*np.exp(-1j*2*math.pi*fa*t)+f2*np.exp(-1j*2*math.pi*fb*t+1j*shift))
   d.ball((-3,-1.3,.65),.17,C);d.ball((-3,1.3,.65),.17,G)
   note='Two coherent spherical-wave contributions / Signed pressure is summed before intensity'
   if name=='beats':note='Two nearby frequencies / Slow-motion pressure field and beat envelope'
  # Constant grid positions sample pressure; these dots are not moving parcels.
  for q,value in zip(pts,p):d.ball(q,.027,wave_color(float(value)))
 elif name=='standing':
  x=np.linspace(-4,4,200);phase=math.cos(w*t);L=8
  for j in [0,1]:
   y=j*2-1;shape=np.sin(math.pi*(x+4)/L) if j==0 else -np.cos(math.pi*(x+4)/L)
   d.line([(-4,y,1),(4,y,1)],S,1);d.line(np.stack([x,np.full(len(x),y),1+.7*shape*phase],axis=1),C if j==0 else G,3)
  for xx in [-4,4]:d.wall(xx,-1.5,1.5,2)
  for q in [-4,-3,-2,-1,0,1,2,3,4]:d.ball((q+.12*math.sin(math.pi*(q+4)/L)*phase,-1,1),.055,WHITE)
  note='Blue: displacement graph / Amber: pressure graph / Rigid-end boundary conditions'
 elif name in ['room','room_treated']:
  d.wall(-4,-2,2,3);d.poly([(-4,2,0),(4,2,0),(4,2,3),(-4,2,3)],(47,69,92));d.line([(-4,2,3),(4,2,3),(4,2,0)],S,3)
  for x in [-2,0,2]:d.poly([(x-.45,1.96,.7),(x+.45,1.96,.7),(x+.45,1.96,2.5),(x-.45,1.96,2.5)],(22,38,55))
  a=(-2,-.8,.65);b=(2,-.8,.65);d.ball(a,.17,G);d.ball(b,.16,C)
  paths=[[a,b],[a,(0,1.9,.65),b],[a,(-3.9,.7,.65),(0,1.9,.65),b]]
  for n,path in enumerate(paths):
   d.line(path,S,1);p=along(path,1.6*(t%10))
   if p is not None:d.ball(p,.12*((.45 if name=='room_treated' else .8)**n),G)
  note='Illustrative ray paths / Treated reflections reduced' if name=='room_treated' else 'Direct arrival and reflected arrivals / Illustrative paths, not a measured room response'
 elif name=='doppler':
  c=1.4;A=1.3;omega=2*math.pi/10;xs=A*math.sin(omega*t);d.ball((xs,0,.65),.19,G)
  sign=1 if math.cos(omega*t)>0 else -1;d.arrow((xs+.25*sign,0,.65),(xs+sign*1.3,0,.65),G)
  for i in range(10):
   age=(t+i*.5)%5;te=t-age;center=(A*math.sin(omega*te),0,.65)
   d.ring(center,c*age,C,width=2)
  note='Front centres stay at emission positions / Subsonic source / Stationary uniform medium'
 elif name=='hearing':
  d.ring((-3+.05*math.sin(w*3*t),0,1.1),.8,C,'yz',width=5);d.line([(-2.8,0,1.1),(-1.5,0,1.1)],S,12)
  for i in range(3):d.ball((-1.3+i*.45+.05*math.sin(w*3*t),0,1.1),.15,G)
  th=np.linspace(0,8.4,160);rr=np.linspace(.05,1.5,160);p=np.stack([1+rr*np.cos(th),rr*np.sin(th),np.full(160,1.1)],axis=1);d.line(p,C,4)
  d.ball(p[int((t%5)/5*159)],.11,G);d.arrow((2.8,0,1.1),(4.2,0,1.1),G)
  d.ball((2.8+1.4*((t%2)/2),0,1.1),.09,C)
  note='Functional hearing schematic / Not an anatomical model or literal hair-cell motion'
 return d,note

def frame(name,t):
 d,note=geometry(name,t);im=d.render();dr=ImageDraw.Draw(im)
 dr.text((100,1005),note,font=font,fill=(185,202,216),stroke_width=1,stroke_fill=(12,20,31))
 return im

def clip(name,duration):
 dest=R/f'renders/{name}_loop.mp4'
 if dest.exists():
  check=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(dest)],capture_output=True,text=True)
  if check.returncode==0 and abs(float(check.stdout)-duration)<.04:return
  dest.unlink()
 p=subprocess.Popen(['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(dest)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=open(R/f'renders/{name}_encode.log','w'))
 for f in range(int(duration*FPS)):
  im=frame(name,f/FPS);p.stdin.write(im.tobytes())
  if f==0:im.save(R/f'renders/{name}_check.png')
 p.stdin.close();assert p.wait()==0
 print('CLIP COMPLETE',name,duration,flush=True)

def init_worker():
 global BG,BGHI
 BG=Image.open(R/'assets/studio.png').convert('RGB')
 BGHI=BG.resize((W*AA,H*AA),Image.Resampling.LANCZOS)

def work(job):clip(*job)

if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='preview':
  init_worker()
  for n in ['source','particle','pressure','diffraction','interference','standing','doppler']:frame(n,1.25).save(R/f'renders/{n}_check.png')
 else:
  jobs=[('source',10),('particle',10),('pressure',5),('frequency',5),('harmonics',5),('vacuum',5),('media',5),('boundary',10),('diffraction',6),('diffraction_wide',6),('interference',5),('interference_opposite',5),('beats',5),('standing',5),('room',10),('room_treated',10),('doppler',10),('hearing',10),('final',10)]
  with ProcessPoolExecutor(max_workers=3,initializer=init_worker) as pool:list(pool.map(work,jobs))
