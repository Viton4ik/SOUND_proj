# SOUND / A FIELD IN MOTION - animated version v03

Seven minutes, 1920x1080, 30 fps, English titles, English male neural narration,
and licensed ambient music. Main titles remain for ten seconds.

## Changes from v02

- Processes now move frame by frame: longitudinal parcels, wavefronts,
  pressure graphs, aperture diffraction, interference, beats, standing waves,
  reflected pulses, Doppler fronts and a functional hearing schematic.
- The parcel chapter holds one enlarged parcel near a fixed cross for forty
  seconds. A blue travelling marker separately shows propagation.
- Narration is generated with Kokoro `am_michael`. It is synthetic speech,
  not a recording of a hired narrator or a clone of an identified person.
- Music: Cylinder Seven by Chris Zabriskie, CC BY 4.0, with credits in the
  movie and a ready-to-use attribution text in `docs/Music_Credits_EN.txt`.
- The script was shortened for natural pauses while preserving the topics.

## Repository contents

- `scripts/` contains the animation, narration, audio mix, export and validation code.
- `docs/` contains the English screen text and narration, the Russian script, the timeline, physics notes and media credits.
- `assets/studio_source.blend` contains the editable background scene from Blender.
- `output/` contains the English captions and title timing. The original archive also includes the finished MP4, narration tracks, final mix, poster and rendered background.

## Rendering method

This is a procedural scientific 3D composite. Python evaluates positions and
wave fields in three-dimensional world coordinates for every frame. An
orthographic camera projects them; the software rasterizer draws depth-sorted
geometry and shaded parcel sprites over the rendered Blender studio plate.
Geometry is supersampled at twice the output dimensions and downsampled.
It is not a full sequence rendered with Cycles. The 3D processes are
schematic, with explicit pressure-graph and scalar-field conventions.

Repeating analytical processes are rendered as complete periodic loops and
reused in the edit. Each ten-second shot is encoded to exactly 300 frames.
No generative video model or AI frame interpolation is used.

## Rebuild

Use Python 3.12, Blender 5.0 or a compatible bpy installation, Nimbus Sans and FFmpeg with libx264, AAC and libass. The two requirements files pin the Python packages for speech and image rendering. Set `SOUND_FONT_PATH` if Nimbus Sans is installed outside the standard Linux path.

From the repository root:

```sh
python3 scripts/fetch_assets.py
blender -b --python scripts/build_studio.py
python3 -m venv .venv-voice
.venv-voice/bin/pip install -r requirements_voice.txt
.venv-voice/bin/python scripts/narration.py
python3 -m venv .venv-motion
.venv-motion/bin/pip install -r requirements_motion.txt
.venv-motion/bin/python scripts/motion.py
.venv-motion/bin/python scripts/compose.py audio
.venv-motion/bin/python scripts/compose.py video
```

The export writes `output/Sound_Animated_v03_7min.mp4`. Keep `renders/` as a local cache. A changed scene needs its cached loop and assembled shots rebuilt.

For attribution and verified media sources, see [Music Credits](docs/Music_Credits_EN.txt) and [Voice Model Manifest](docs/Voice_Model_Manifest.json).
