GITHUB DISTRIBUTION NOTE
This folder includes code, input crops, reports, slides, PNGs and CSVs.
Large NPZ arrays and the full satellite source JPEG are not committed.
Run run_experiment.py to regenerate NPZ arrays before rebuilding slides.
All paths resolve relative to this folder; the D: paths below describe the
author's local workspace, not a required installation directory.

GNR607 DENOISING PROJECT — REVISED EXPERIMENT

Start with report.html or GNR607_Photographs_Presentation.pptx.
All project files, data, outputs and project temporary files are on D:.
Original Indian Pines project and previous presentation are preserved.

REPRODUCE
Open PowerShell in this folder, then run:
  $env:TEMP="$PWD\temp"
  $env:TMP=$env:TEMP
  $env:PYTHONDONTWRITEBYTECODE='1'
  python run_experiment.py
  python build_deliverables.py

USER-SPECIFIED k AND WINDOW
  python run_experiment.py --window 5 --k 18
This writes separate results_w5_k18 outputs and leaves the selected-setting
results and presentation unchanged. Numerical CSVs, PNGs and NPZs are produced.
Rebuilding the presentation always uses the default results folder.

FILES
data/: camera.png and astronaut.png, both native 512x512 images.
run_experiment.py: complete experiment and parameter sweep.
core_manual.py: preserved original manual numerical implementation.
results/parameter_sweep.csv: all 72 validation configurations.
results/trials.csv: all 18 final trials.
results/summary.csv: mean and sample SD of all measured errors.
results/manifest.json: source image checksums, means, settings and conventions.
results/*.npz: full-precision trial-1 originals/noisy/KNN/mean arrays.
results/*.png: display-only outputs and identical fixed central crops.
build_deliverables.py and slide_helpers.py: editable presentation/report source.

METHOD
Uniform noise SD is 5%,10%,20% of the original channel mean.
Bounds are plus/minus sqrt(3) times SD. No clipping before filtering/scoring.
RGB channels are processed separately, including noise scaling by channel mean.
KNN uses intensity distance from the noisy centre, not a trained classifier.
Centre included; replicated borders; stable row-major ties; separate output.
Both filters always use the same noisy realization and the same window size.
MSE reference is the original photograph before synthetic noise is added.

PARAMETER SELECTION
3x3,5x5,7x7 windows; four k fractions per window, all below the full area.
Minimise the average of KNN and mean validation MSE per image/noise level.
Validation noise seed60700; fresh test noise seeds60701,60702,60703.
Same noise streams are scaled across levels. Three final repetitions.
Settings are calibrated with known clean images; this is not evaluation on
unseen scenes and not an automatic choice possible without a reference.
The previous k9/5x5 setting is also rerun on the same test data for comparison.

IMPLEMENTATION
NumPy vectorises window gathering, sorting and reductions for faster sweeps.
The original manual implementation is retained, and nine small equivalence
checks are executed on every run. Do not describe this revised runner as
library-free. k=1 returns noisy input; k=window squared returns mean filtering.

INTERPRETATION
At 5%, mean filtering increases MSE relative to the noisy image on both photos:
blur costs more than the small noise reduction. KNN improves only modestly.
At 10% and20%, both filters substantially reduce noise MSE. Residual grain,
colour speckling and blurred detail remain. No advanced denoiser or cosmetic
post-filtering is used. Photographs replace the previous satellite data; these
results do not establish satellite-image performance.

SOURCES
https://scikit-image.org/docs/stable/api/skimage.data.html
https://github.com/scikit-image/scikit-image/tree/v0.25.2/skimage/data
Camera: public-domain contribution by Lav Varshney.
Astronaut Eileen Collins: NASA, public domain.
Inputs are the repository PNGs, not AI-generated illustrations.

Dependencies already available in this environment: numpy, Pillow, python-pptx,
scipy (imported by presentation helpers). No packages installed for this rerun.
