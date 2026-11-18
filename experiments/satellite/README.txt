GITHUB DISTRIBUTION NOTE
This folder includes code, input crops, reports, slides, PNGs and CSVs.
Large NPZ arrays and the full satellite source JPEG are not committed.
Run run_experiment.py to regenerate NPZ arrays before rebuilding slides.
All paths resolve relative to this folder; the D: paths below describe the
author's local workspace, not a required installation directory.

GNR607 — SATELLITE IMAGE DENOISING

Separate alternative project. Everything is in D:\GNR607\Satellite_Denoising.
The photograph project in Denoising_Retry remains intact.

OPEN
report.html: complete visual comparisons and measured results.
GNR607_Satellite_Presentation.pptx: presentation.

DATA
Two native 768x768 crops (farmland and urban area) of ESA's 9725x10223
Sentinel-2 Netherlands false-colour image. No resizing or upscaling.
The input is an 8-bit processed JPEG composite; extracted crops are lossless
PNGs. These are display channels, not raw spectral bands or reflectance.
The exact ground sampling distance of the processed JPEG is not established.
Larger pixel dimensions should not be confused with a verified improvement
in metres per pixel. The two crops are from one scene, not independent dates.
Vegetation appears red because near-infrared is included in the composite.

SOURCE AND LICENCE
https://www.esa.int/ESA_Multimedia/Images/2019/10/The_Netherlands
Contains modified Copernicus Sentinel data (2016), processed by ESA.
Cropping and synthetic noise/filtering are modifications made for this project.
Image derivatives licensed under CC BY-SA 3.0 IGO:
https://creativecommons.org/licenses/by-sa/3.0/igo/
Keep attribution and licence when sharing the image derivatives or slides.
data/source_manifest.json records original hash, download link and crop boxes.

REPRODUCE (PowerShell in this folder)
  $env:TEMP="$PWD\temp"
  $env:TMP=$env:TEMP
  $env:PYTHONDONTWRITEBYTECODE='1'
  python run_experiment.py
  python build_deliverables.py

USER-SPECIFIED PARAMETERS
  python run_experiment.py --window 5 --k 18
Writes a separate results_w5_k18 folder; does not replace default results.
The presentation builder reads the default results folder.

EXPERIMENT
Add zero-mean uniform noise with SD=5%,10%,20% of each original channel mean.
Uniform limits are +/-sqrt(3)*SD. No clipping before filtering or MSE.
KNN picks the k intensities nearest to the noisy centre within the window.
The centre is eligible. Stable row-major ties, replicated borders, separate
output buffers. Mean averages all entries of the SAME spatial window.
Each display channel is processed separately. MSE averages pixels/channels
against the original image before adding noise. PNGs alone are clipped to255.

SETTINGS
Validation seed60700. Windows3,5,7 and four k values per window.
Choose minimum average of KNN and mean MSE per crop/noise level.
Test on new noise seeds60701,60702,60703, retaining the selected settings.
This is clean-reference calibration on known scenes, not unseen-scene testing.
Same noise streams are scaled across levels for paired comparisons.
Baseline k9/window5 is rerun on exactly the same satellite test data.

OUTPUTS
results/parameter_sweep.csv: every validation configuration.
results/trials.csv: all18 test trials.
results/summary.csv: means and sample standard deviations.
results/*.npz: full-precision trial1 arrays (original,noisy,knn,mean).
results/*.png: full images and identical central192x192 detail crops.
results/manifest.json: input hashes, means and selected parameters.

IMPLEMENTATION
NumPy accelerated implementation uses sorting and reductions. Original manual
algorithm is preserved in core_manual.py. Nine equivalence checks execute
on every run, including k1 and full-window k. This runner is not library-free.
Dependencies: numpy, Pillow, python-pptx, scipy (presentation helper import).
No packages installed for this project. prepare_satellite.py is a one-time
setup script; run_experiment.py is the reproducible experiment entry point.
