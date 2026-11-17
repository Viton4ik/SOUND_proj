from pathlib import Path
import subprocess,json,zipfile,hashlib
R=Path(__file__).resolve().parents[1];movie=R/'output/Sound_Animated_v03_7min.mp4'
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
p=probe(movie);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',12600)
assert abs(float(v['duration'])-420)<.04 and abs(float(p['format']['duration'])-420)<.04
assert a['channels']==2 and a['sample_rate']=='48000'
for n in range(1,43):
 x=probe(R/f'renders/shot_{n:02}_exact.mp4')['streams'][0]
 assert int(x['nb_frames'])==300 and abs(float(x['duration'])-10)<.04
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
# A frame hash change proves each rendered process is moving, rather than a still board.
loop_checks={}
for path in sorted((R/'renders').glob('*_loop.mp4')):
 out=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf','select=eq(n\\,0)+eq(n\\,15)','-fps_mode','passthrough','-f','framemd5','-']).decode()
 hashes=[line.rsplit(',',1)[-1].strip() for line in out.splitlines() if not line.startswith('#')]
 assert len(hashes)==2 and hashes[0]!=hashes[1],path
 loop_checks[path.stem]='moving'
timings=json.loads((R/'docs/narration_timing.json').read_text());shots=json.loads((R/'docs/timeline.json').read_text())
assert all(s['start']<=q['start'] and q['start']+q['duration']<=s['end'] for s,q in zip(shots,timings))
audio=json.loads((R/'docs/Audio_QA.json').read_text());assert audio['clipped_samples']==0
music=R/'assets/Cylinder_Seven_Chris_Zabriskie.ogg';assert hashlib.sha1(music.read_bytes()).hexdigest()=='b7a8b2dc3952e3ef1618fc23c9b0531212ff1b56'
report={'version':'v03','seconds':420,'video_frames':12600,'fps':30,'resolution':[1920,1080],'complete_decode':'passed','all_42_shots_exact':'passed','narration':'Kokoro am_michael','narration_overruns':0,'music':'Cylinder Seven by Chris Zabriskie / CC BY 4.0','music_hash_verified':True,'rendered_motion':loop_checks,'models':json.loads((R/'docs/Model_QA.json').read_text()),'visual_review':'Selected rendered frames and the final chapter contact sheet; voice naturalness remains a listener judgement.'}
(R/'docs/QA_Report.json').write_text(json.dumps(report,indent=2))
files=[R/'README.md',R/'requirements_voice.txt',R/'requirements_motion.txt']
files+=sorted((R/'scripts').glob('*.py'))+sorted((R/'docs').glob('*'))
files += [R/'assets'/n for n in ['Cylinder_Seven_Chris_Zabriskie.ogg','studio.png','studio_source.blend','title_styles.ass']]
files += [R/'output'/n for n in ['Sound_Animated_v03_7min.mp4','Narration_Michael_EN.wav','Narration_Michael_EN.m4a','Full_Mix.m4a','English_Captions.srt','titles.ass','poster.png']]
dest=R.parent/'Sound_Animated_v03_Project.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for path in files:z.write(path,Path('Sound_Animated_v03_Project')/path.relative_to(R))
with zipfile.ZipFile(dest) as z:assert z.testzip() is None
print(json.dumps(report));print('ARCHIVE',str(dest),dest.stat().st_size)
