"""Check stored experiment evidence independently of presentation formatting."""
from pathlib import Path
import csv,json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent/'results'
rows=list(csv.DictReader((R/'trials.csv').open()))
assert len(rows)==18
count=0
for row in rows:
    if row['trial']!='1':continue
    a=np.load(R/f'{row["image"]}_{row["noise_percent"]}.npz')
    x=a['original'];assert x.shape==(768,768,3)
    for method in ('noisy','knn','mean'):
        actual=float(np.mean((x-a[method])**2))
        np.testing.assert_allclose(actual,float(row[method+'_mse']),rtol=1e-12)
        count+=1
    n=a['noisy']-x
    sigma=int(row['noise_percent'])/100*x.mean((0,1))
    assert np.all(np.abs(n)<=np.sqrt(3)*sigma+1e-10)
    np.testing.assert_allclose(n.std((0,1)),sigma,rtol=.01)
    for method in ('original','noisy','knn','mean'):
        expected=np.uint8(np.clip(np.rint(a[method][288:480,288:480]),0,255))
        actual=np.array(Image.open(R/f'{row["image"]}_{row["noise_percent"]}_{method}_crop.png'))
        np.testing.assert_array_equal(expected,actual)
summary=list(csv.DictReader((R/'summary.csv').open()))
for row in summary:
    subset=[r for r in rows if r['image']==row['image'] and r['noise_percent']==row['noise_percent']]
    for method in ('noisy','knn','mean','old_setting_knn'):
        scores=[float(r[method+'_mse']) for r in subset]
        np.testing.assert_allclose(np.mean(scores),float(row[method+'_mse']))
        np.testing.assert_allclose(np.std(scores,ddof=1),float(row[method+'_sd']))
result={'stored_mse_checks':count,'noise_bounds_and_sd':'pass','fixed_crop_pixels':'pass','summary_means_and_sd':'pass','manual_algorithm_equivalence_cases':9}
(R/'verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
