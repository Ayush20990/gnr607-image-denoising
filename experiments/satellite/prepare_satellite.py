from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parent
URL='https://www.esa.int/ESA_Multimedia/Images/2019/10/The_Netherlands'
CREDIT='Contains modified Copernicus Sentinel data (2016), processed by ESA. Cropped and synthetically noised/filtered for this project.'
source=ROOT/'data/Netherlands_ESA_source.jpg'
if not source.exists():
    from urllib.request import urlopen
    manifest=json.loads((ROOT/'data/source_manifest.json').read_text(encoding='utf-8'))
    with urlopen(manifest['download'],timeout=120) as response:
        payload=response.read()
    if hashlib.sha256(payload).hexdigest()!=manifest['sha256']:
        raise ValueError('Downloaded source differs from the recorded image checksum.')
    source.write_bytes(payload)
Image.MAX_IMAGE_PIXELS=110_000_000
im=Image.open(source).convert('RGB')
regions={'farmland':(6000,800,6768,1568),'urban':(6400,3000,7168,3768)}
for name,box in regions.items():im.crop(box).save(ROOT/'data'/f'{name}.png')
(ROOT/'data/source_manifest.json').write_text(json.dumps({'source_page':URL,'download':'https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2019/10/the_netherlands/20813142-1-eng-GB/The_Netherlands.jpg','source_dimensions':im.size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'credit':CREDIT,'licence':'CC BY-SA 3.0 IGO','licence_url':'https://creativecommons.org/licenses/by-sa/3.0/igo/','crop_boxes_xyxy':regions,'processing':'Native decoded JPEG pixels cropped without resizing; saved losslessly as PNG. 8-bit RGB false-colour display composite, not calibrated reflectance. Exact output ground sampling distance is not established from this JPEG.'},indent=2),encoding='utf-8')
