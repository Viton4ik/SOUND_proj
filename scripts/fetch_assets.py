"""Download and verify the published music and voice model files."""
import hashlib
import json
import shutil
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

def download(name, url, algorithm, expected, headers):
    path = ROOT / "assets" / name
    def matches(file):
        with file.open("rb") as source:
            return hashlib.file_digest(source, algorithm).hexdigest() == expected
    if path.exists() and matches(path):
        print(f"Verified {name}")
        return
    temporary = path.with_suffix(path.suffix + ".part")
    try:
        with urlopen(Request(url, headers=headers), timeout=120) as source, temporary.open("wb") as dest:
            shutil.copyfileobj(source, dest)
        if not matches(temporary):
            raise ValueError(f"Checksum mismatch for {name}")
        temporary.replace(path)
        print(f"Downloaded {name}")
    finally:
        temporary.unlink(missing_ok=True)

def main():
    (ROOT / "renders").mkdir(exist_ok=True)
    music = json.loads((ROOT / "docs/Music_manifest.json").read_text())
    voice = json.loads((ROOT / "docs/Voice_Model_Manifest.json").read_text())
    download("Cylinder_Seven_Chris_Zabriskie.ogg", music["source_url"], "sha1", music["sha1"],
             {"User-Agent": "Mozilla/5.0", "Referer": "https://commons.wikimedia.org/"})
    base = voice["model_source"].replace("/tag/", "/download/") + "/"
    for model in voice["files"]:
        download(model["name"], base + model["name"], "sha256", model["sha256"],
                 {"User-Agent": "SOUND_proj/1.0"})

if __name__ == "__main__":
    main()
