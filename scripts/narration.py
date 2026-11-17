from pathlib import Path
import json,sys,subprocess
import numpy as np
import soundfile as sf
import onnxruntime as rt
from kokoro_onnx import Kokoro
R=Path(__file__).resolve().parents[1]
shots=json.loads((R/'docs/timeline.json').read_text())
VOICE_LINES=[
'Every sound begins with vibration. A whisper, a drumbeat and a passing train send different disturbances through their surroundings.',
'A vibrating surface pushes and pulls on nearby air. The disturbance travels outward, beyond the object that created it.',
'Follow one small parcel of air. The fixed cross marks its resting position. Watch the gold sphere.',
'The parcel moves forward, then backward. Its displacement is exaggerated so you can see this local motion clearly.',
'The parcel stays near its resting position. It passes the disturbance to its neighbours, rather than travelling across the room.',
'Matter oscillates locally. The travelling wave carries energy onward. These are different motions. Now let us examine the larger pattern.',
'Where neighbouring parcels crowd together, density and pressure rise above their resting values. This region is a compression.',
'Where parcels spread apart, density and pressure fall. This is a rarefaction. Both regions move with the wave.',
'In air, parcel motion is parallel to wave propagation. Sound is therefore longitudinal. The colours here represent pressure.',
'Frequency counts cycles per second. Higher frequency usually means higher pitch and, at constant speed, a shorter wavelength.',
'Pressure amplitude measures the size of the disturbance. Doubling it gives four times the intensity in the same medium.',
'A pure tone has one frequency. Instruments combine a fundamental with harmonics and changing envelopes. These features shape timbre.',
'Sound needs matter. In a vacuum, an object can keep vibrating, but ordinary sound cannot carry that vibration outward.',
'Wave speed depends on elasticity and density. Air, water and solids respond differently. Solids can also support shear waves.',
'Across a stationary boundary, frequency remains unchanged. When propagation speed changes, wavelength changes with it.',
'A boundary can reflect, transmit and absorb sound. The energy balance depends on the materials, their construction and the frequency.',
'A smooth surface can redirect a wave. A sufficiently delayed reflection is heard as a separate echo.',
'Absorption reduces reflections inside a room. Sound isolation addresses transmission between spaces, including paths around the barrier.',
'Sound spreads through openings and around edges. This diffraction explains why a doorway does not create a sharp acoustic shadow.',
'Compare the opening with the wavelength. Strong spreading occurs when their sizes are comparable. A much wider opening spreads less.',
'Contributions from different parts of the opening combine beyond it. Their path differences shape the outgoing pressure field.',
'Overlapping pressure variations add, with their positive and negative signs. In the linear regime, this is superposition.',
'Equal contributions reinforce when they arrive in phase. With coherent sources, path length and source phase determine the pattern.',
'Equal, opposite contributions can cancel at a point. Local cancellation does not make the entire surrounding region silent.',
'Nearby frequencies drift in and out of phase. Their combined level pulses in beats, at the frequency difference.',
'Equal waves travelling in opposite directions can form a standing wave. Its pattern stays in place while matter continues oscillating.',
'Displacement nodes remain still. Antinodes move most. Neighbouring nodes are half a wavelength apart.',
'Pressure and displacement nodes differ. At an ideal rigid end, displacement is zero, while the pressure variation is greatest.',
'Resonance strengthens the response near natural frequencies. Geometry selects the modes. Damping limits their strength and persistence.',
'A room adds reflected paths to the direct sound. Their timing shapes clarity, spaciousness and the character of a voice.',
'Overlapping reflections create reverberation: a decaying sound tail. Its behaviour depends on the room, the surfaces and the frequency.',
'Suitable absorption shortens that tail. Speech, recording and live music have different acoustic needs. Treatment should serve the purpose.',
'Room modes make bass uneven. Moving the source or listener changes the response, revealing strong peaks or deep cancellations.',
'Each wavefront expands from its emission position. A moving source leaves these positions behind as it continues along its path.',
'Ahead of an approaching subsonic source, fronts are closer together. They reach a stationary listener more frequently, raising the pitch.',
'Behind a receding source, fronts are farther apart. The received pitch falls, even when the emitted note stays the same.',
'In uniform, stationary air, source motion does not change propagation speed. It changes the spacing and timing of arriving fronts.',
'Pressure variations drive the eardrum. The middle ear transmits this motion onward, coupling airborne sound into the inner ear.',
'Different cochlear regions respond most strongly to different frequencies. Sensory hair cells help convert movement into neural signals.',
'The brain interprets timing, spectrum and context. These cues help us recognise voices, locate sources and understand a scene.',
'Vibration, propagation, interaction and perception connect the journey, from a moving surface to a complex sound field.',
'Matter oscillates. Energy travels. Geometry shapes the field. At the end of this physical journey, a listener hears a world.'
]
assert len(VOICE_LINES)==len(shots)
for sh,line in zip(shots,VOICE_LINES):sh['voice']=line
opts=rt.SessionOptions();opts.intra_op_num_threads=4;opts.inter_op_num_threads=1
sess=rt.InferenceSession(str(R/'assets/kokoro-v1.0.onnx'),sess_options=opts,providers=['CPUExecutionProvider'])
k=Kokoro.from_session(sess,str(R/'assets/voices-v1.0.bin'))
mix=np.zeros(420*24000,dtype=np.float32);timing=[]
for sh in shots:
 n=sh['index'];p=R/f'renders/final_voice_{n:02}.wav';speed=1.03
 if p.exists():a,sr=sf.read(p,dtype='float32')
 else:
  a,sr=k.create(sh['voice'],voice='am_michael',speed=speed,lang='en-us')
 for attempt in range(4):
  if len(a)/sr<=9.35:break
  speed=max(speed+.04,speed*len(a)/sr/8.8)
  a,sr=k.create(sh['voice'],voice='am_michael',speed=speed,lang='en-us')
 sf.write(p,a,sr,subtype='PCM_24')
 dur=len(a)/sr
 assert sr==24000 and dur<9.6,(n,dur)
 start=int((sh['start']+.25)*sr)
 mix[start:start+len(a)]=a
 timing.append({'index':n,'start':sh['start']+.25,'duration':dur,'voice':'am_michael','speed':speed})
 print('VOICE',n,round(dur,2),round(speed,3),flush=True)
peak=float(np.max(np.abs(mix)))
if peak>.88:mix*=.88/peak
sf.write(R/'output/Narration_Michael_EN.wav',mix,24000,subtype='PCM_24')
(R/'docs/timeline.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2))
(R/'docs/narration_timing.json').write_text(json.dumps(timing,indent=2))
text='# English narrator script - Michael / v03\n\nVoice: Kokoro am_michael; generated from the original script. No voice clone or impersonation.\n\n'
for sh in shots:text+=f"## {sh['start']//60:02}:{sh['start']%60:02}-{sh['end']//60:02}:{sh['end']%60:02}\n\n{sh['voice']}\n\n"
(R/'docs/02_Voiceover_EN.md').write_text(text)
subprocess.run(['ffmpeg','-y','-i',str(R/'output/Narration_Michael_EN.wav'),'-c:a','aac','-b:a','160k',str(R/'output/Narration_Michael_EN.m4a')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print('FULL NARRATION COMPLETE',flush=True)
