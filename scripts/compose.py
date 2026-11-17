from pathlib import Path
import json,subprocess,math,wave,sys
import numpy as np
from concurrent.futures import ThreadPoolExecutor
R=Path(__file__).resolve().parents[1];O=R/'output';T=R/'renders'
shots=json.loads((R/'docs/timeline.json').read_text());timings=json.loads((R/'docs/narration_timing.json').read_text())
def run(args):subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
def pcm(path,channels):
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-t','420','-ar','48000','-ac',str(channels),'-f','f32le','-'])
 return np.frombuffer(data,dtype='<f4').reshape((-1,channels)).copy()
def audio():
 sr=48000;n=420*sr;t=np.arange(n)/sr
 voice=pcm(O/'Narration_Michael_EN.wav',1)[:,0];music=pcm(R/'assets/Cylinder_Seven_Chris_Zabriskie.ogg',2)
 assert len(voice)==n and len(music)==n
 gate=np.zeros(n,dtype=np.float32)
 for v in timings:
  start=v['start'];end=start+v['duration'];lo=max(0,int((start-.15)*sr));hi=min(n,int((end+.3)*sr));tt=t[lo:hi]
  env=np.minimum(np.clip((tt-start+.15)/.15,0,1),np.clip((end+.3-tt)/.3,0,1));gate[lo:hi]=np.maximum(gate[lo:hi],env)
 gain=.20-.10*gate
 gain*=np.minimum(np.clip(t/4,0,1),np.clip((420-t)/10,0,1))
 fx=np.zeros(n,dtype=np.float32)
 def tone(start,end,freq,amp=.12):
  lo=int(start*sr);hi=int(end*sr);tt=t[lo:hi]-start;env=np.minimum(np.clip(tt/.04,0,1),np.clip((end-start-tt)/.08,0,1))
  signal=sum(np.sin(2*np.pi*f*tt) for f in freq)/len(freq)
  fx[lo:hi]+=amp*env*signal
 for index,freq in [(10,[330]),(12,[330,660,990])]:
  v=timings[index-1];start=max(v['start']+v['duration']+.08,index*10-1.6);end=index*10-.08
  if end>start:tone(start,end,freq)
 v=timings[10];start=max(v['start']+v['duration']+.05,108.5);end=109.9
 if end-start>.35:
  middle=(start+end)/2;tone(start,middle,[330],.06);tone(middle,end,[330],.12)
 tone(245.5,249.9,[400,403],.10)
 # Received phase for the same subsonic sinusoidal trajectory used by the Doppler view.
 lo=330*sr;hi=370*sr;tt=t[lo:hi]-330;te=tt-4/1.4
 for _ in range(24):te=tt-(4-1.3*np.sin(2*np.pi*te/10))/1.4
 env=np.minimum(np.clip(tt/1.5,0,1),np.clip((40-tt)/1.5,0,1))
 fx[lo:hi]+=.06*env*np.sin(2*np.pi*220*te)
 # Give the narration priority over all demonstration tones.
 fx*=1-.78*gate
 mask=np.abs(fx)>1e-6;gain[mask]*=.18
 mixed=music*gain[:,None]+voice[:,None]+fx[:,None]
 peak=float(np.max(np.abs(mixed)))
 if peak>.89:mixed*=.89/peak
 a=(mixed*32767).astype('<i2')
 with wave.open(str(O/'Full_Mix.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(a.tobytes())
 run(['ffmpeg','-y','-i',str(O/'Full_Mix.wav'),'-c:a','aac','-b:a','192k',str(O/'Full_Mix.m4a')])
 (R/'docs/Audio_QA.json').write_text(json.dumps({'duration_seconds':420,'sample_rate':sr,'channels':2,'peak_dBFS':20*math.log10(float(np.max(np.abs(a)))/32768),'clipped_samples':int(np.sum(np.abs(a.astype(np.int32))>=32767)),'voice':'Kokoro am_michael','music':'Cylinder Seven / Chris Zabriskie / CC BY 4.0','note':'The music is reduced under narration and demonstration tones. Sound examples are illustrative; animation time is slowed.'},indent=2))
 print('AUDIO MIX COMPLETE',flush=True)

def titles():
 src=(R/'assets/title_styles.ass').read_text();header=src.split('[Events]')[0]
 events='[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
 def tm(t):return f'{t//3600}:{t//60%60:02d}:{t%60:05.2f}'
 for sh in shots:
  for style,text in [('Title',sh['heading']),('Detail',sh['screen'])]:events+=f"Dialogue: 0,{tm(sh['start'])},{tm(sh['end'])},{style},,0,0,0,,{{\\fad(350,150)}}{text}\n"
 events+='Dialogue: 0,0:00:00.00,0:07:00.00,Counter,,0,0,0,,SOUND / A FIELD IN MOTION\n'
 events+='Dialogue: 0,0:06:50.00,0:07:00.00,Note,,0,0,150,,Music: Cylinder Seven by Chris Zabriskie / Album: Cylinders\n'
 events+='Dialogue: 0,0:06:50.00,0:07:00.00,Note,,0,0,115,,CC BY 4.0 / creativecommons.org/licenses/by/4.0/ / chriszabriskie.com\n'
 (O/'titles.ass').write_text(header+events)
 srt=''
 def st(t):return f'{int(t)//3600:02}:{int(t)//60%60:02}:{int(t)%60:02},{round(t%1*1000):03}'
 for sh,v in zip(shots,timings):srt+=f"{sh['index']}\n{st(v['start'])} --> {st(v['start']+v['duration'])}\n{sh['voice']}\n\n"
 (O/'English_Captions.srt').write_text(srt)

def film():
 def valid(path,frames):
  if not path.exists():return False
  q=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,duration','-of','json',str(path)],capture_output=True,text=True)
  if q.returncode:return False
  try:
   v=json.loads(q.stdout)['streams'][0]
   return int(v['nb_frames'])==frames and abs(float(v['duration'])-frames/30)<.04
  except (KeyError,IndexError,ValueError):return False
 def section(sh):
  name=sh['scene']
  name={12:'harmonics',13:'vacuum',20:'diffraction_wide',24:'interference_opposite',25:'beats',32:'room_treated'}.get(sh['index'],name)
  source=T/f'{name}_loop.mp4';dst=T/f'shot_{sh["index"]:02}_exact.mp4'
  if not valid(dst,300):
   temp=dst.with_name(dst.stem+'_part.mp4')
   run(['ffmpeg','-y','-stream_loop','-1','-i',str(source),'-frames:v','300','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','16','-pix_fmt','yuv420p',str(temp)])
   assert valid(temp,300),temp
   temp.replace(dst)
  return dst
 with ThreadPoolExecutor(max_workers=3) as pool:sections=list(pool.map(section,shots))
 (T/'concat.txt').write_text(''.join(f"file '{p}'\n" for p in sections))
 temp=O/'Sound_Animated_v03_7min_part.mp4'
 run(['ffmpeg','-y','-xerror','-f','concat','-safe','0','-i',str(T/'concat.txt'),'-i',str(O/'Full_Mix.wav'),'-vf',f'ass={O}/titles.ass','-c:v','libx264','-threads','6','-preset','slow','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','420','-movflags','+faststart',str(temp)])
 assert valid(temp,12600),'Final video must contain exactly 12600 frames'
 temp.replace(O/'Sound_Animated_v03_7min.mp4')
 print('FILM COMPLETE',flush=True)

if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in ['all','audio']:audio();titles()
 if mode in ['all','video']:film()
