"""Download image and land-cover labels; no executable content is loaded."""
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError
import hashlib
import json

SOURCE = "https://www.ehu.eus/ccwintco/index.php/Hyperspectral_Remote_Sensing_Scenes"
FILES = {
    "Indian_pines_corrected.mat": "https://www.ehu.eus/ccwintco/uploads/6/67/Indian_pines_corrected.mat",
    "Indian_pines_gt.mat": "https://www.ehu.eus/ccwintco/uploads/c/c4/Indian_pines_gt.mat",
}
MIRROR = "https://huggingface.co/datasets/danaroth/indian_pines/resolve/b96c10a/"
EXPECTED_SHA256 = {
    "Indian_pines_corrected.mat": "ec2f8808710919d566f70f0d4aa885aae1ddfd42b734aba71c5e12ca65450939",
    "Indian_pines_gt.mat": "65c4687a8ab04f6da4789799bc3bc4f6e88bccac3ed6a2e6ae367e5e6b9e429c",
}


def download(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {"source_page": SOURCE, "files": []}
    manifest_path = destination / "source_manifest.json"
    previous = {}
    if manifest_path.exists():
        previous = {entry["name"]: entry for entry in json.loads(manifest_path.read_text(encoding="utf-8"))["files"]}
    for name, url in FILES.items():
        path = destination / name
        actual_url = previous.get(name, {}).get("download_url", "existing local file; origin not recorded")
        if not path.exists():
            print("Downloading", name, flush=True)
            try:
                with urlopen(url, timeout=20) as response:
                    content = response.read()
                actual_url = url
            except (URLError, TimeoutError):
                actual_url = MIRROR + name
                print("Primary server unavailable; using pinned public mirror.", flush=True)
                with urlopen(actual_url, timeout=60) as response:
                    content = response.read()
            if not content.startswith(b"MATLAB 5.0 MAT-file"):
                raise ValueError("Server did not return a MATLAB image file: " + url)
            if hashlib.sha256(content).hexdigest() != EXPECTED_SHA256[name]:
                raise ValueError("Downloaded image does not match the recorded checksum.")
            path.write_bytes(content)
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        if checksum != EXPECTED_SHA256[name]:
            raise ValueError("Existing image does not match the recorded checksum: " + str(path))
        manifest["files"].append({"name": name, "original_url": url,
            "download_url": actual_url, "sha256": checksum})
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return destination / "Indian_pines_corrected.mat"


if __name__ == "__main__":
    download(Path(__file__).parent / "data")
