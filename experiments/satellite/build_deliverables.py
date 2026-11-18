from slide_helpers import *
from html import escape
ROOT=Path(__file__).resolve().parent;R=ROOT/'results'
rows=list(csv.DictReader((R/'summary.csv').open()))
for r in rows:
    for key in r:
        if key!='image':r[key]=float(r[key])
SOURCE='https://www.esa.int/ESA_Multimedia/Images/2019/10/The_Netherlands'
def row(name,p):return next(r for r in rows if r['image']==name and r['noise_percent']==p)
def img(name,p,kind,crop=False):return R/f'{name}_{p}_{kind}{"_crop" if crop else ""}.png'
def note():return 'Source: results/summary.csv and trial-1 NPZ files. 768x768 original images; https://www.esa.int/ESA_Multimedia/Images/2019/10/The_Netherlands . Same noisy input and window for both filters. Noise SD per channel = percentage of original channel mean. Display scale fixed to 0..255; only exported images clipped. MSE uses unclipped float64 arrays. Settings selected with validation noise seed60700; test seeds60701–60703. Same scenes, independent noise; not unseen-scene testing.'
def four(s,name,p,crop=False):
    r=row(name,p)
    for i,(kind,title) in enumerate([('original','Original reference'),('noisy',f'Noisy: {p}%'),('knn',f'KNN: k = {int(r["k"])}'),('mean',f'Mean: {int(r["window"])} × {int(r["window"])}')]):
        x=.6+i*3.15;text(s,x,1.9,3,.4,title,19,True);photo(s,img(name,p,kind,crop),x,2.4,2.9)
    a=np.load(R/f'{name}_{p}.npz'); scores=[np.mean((a['original']-a[m])**2) for m in ('noisy','knn','mean')]
    text(s,.6,5.65,12,.55,'Trial 1 MSE:   noisy %.1f    ·    KNN %.1f    ·    mean %.1f'%tuple(scores),23,True)
    text(s,.6,6.4,12,.4,'Fixed 0–255 display scale. '+('Central 192 × 192 crop; scores refer to the full image.' if crop else 'Entire 768 × 768 image; same scene at every noise level.'),18,False,GRAY)

s=slide('Satellite-image denoising','GNR 607 course project',note())
text(s,.6,2,7,1.5,'K-nearest-neighbour smoothing\nversus simple averaging',32,True)
text(s,.6,4.1,6.8,1.4,'Two detailed Sentinel-2 crops, matched filters and independently tested settings.',25,False,GRAY)
text(s,.6,6.1,7,.5,'5%, 10% and 20% noise standard deviation',22,True,TEAL)
photo(s,ROOT/'data/urban.png',8.3,2,4.3)

s=slide('Two Sentinel-2 satellite crops','Input data',note()+' Contains modified Copernicus Sentinel data (2016), processed by ESA. Cropped and synthetically noised/filtered for this project. Source is a 9725x10223 processed JPEG. Both 768x768 crops retain source pixels. Near-infrared contributes to the false colour: vegetation appears red. CC BY-SA 3.0 IGO. Exact JPEG ground sampling distance not established.')
for i,name in enumerate(('farmland','urban')):
    x=.8+i*6.4;photo(s,ROOT/'data'/f'{name}.png',x,1.8,4.4)
    text(s,x,6.32,5.8,.5,'Farmland · false colour' if i==0 else 'Urban area · false colour',23,True)
text(s,5.35,2,1.7,3.2,'768 × 768\npixels\n\nSatellite\ncrops',21,False,GRAY)

s=slide('What the satellite colours represent','Reading the image',note())
text(s,.7,2,12,1,'Vegetation appears red because the composite includes near-infrared information.',28,True)
text(s,.7,3.5,12,1.2,'Two 768 × 768 crops from one 9725 × 10223 ESA image. Source pixels are retained without resizing.',26)
text(s,.7,5.1,12,1.3,'This tests an 8-bit display composite. The source is processed imagery, not raw calibrated spectral bands.',25)
text(s,.7,6.5,12,.4,'Contains modified Copernicus Sentinel data (2016), processed by ESA. CC BY-SA 3.0 IGO.',16,False,GRAY)

s=slide('What the experiment must compare','Project objective',note())
para(s,.7,2,5.5,'Add controlled noise','Uniform noise with standard deviation equal to 5%, 10% and 20% of the original channel mean.',24)
para(s,7,2,5.5,'Compare two filters','KNN and simple averaging use the same noisy image and the same window size.',24)
text(s,.7,5,12,1,'MSE = average of (original − filtered)²',32,True,TEAL)
text(s,.7,6.2,12,.5,'For colour, filter R, G and B separately; average error across all pixels and channels.',20)

s=slide('Uniform noise: standard deviation and bounds','Noise model',note())
text(s,.7,2,6,2.8,'σ = p × original channel mean\n\nNoise ~ Uniform(−√3σ, +√3σ)\n\nNoisy = original + noise',26,True)
table(s,7.1,2,5.5,3.4,['If mean = 100','σ','Bounds'],[['5%','5','±8.66'],['10%','10','±17.32'],['20%','20','±34.64']],size=21)
text(s,.7,6.1,12,.65,'Compute with floating-point values. Clip only the displayed PNG images.',23,True,TEAL)

s=slide('KNN selects intensities; mean selects everything','Filter mechanics',note()+' Synthetic explanatory patch, not measured scene data. Patch sum720, mean80; nearest5 to50 are50,49,51,48,52 and average50.')
table(s,.7,2,4.4,3,['48','52','49'],[['51','50','180'],['47','53','190']],size=29)
text(s,5.9,2,6.7,1.1,'Centre = 50. With k = 5, choose\n50, 49, 51, 48 and 52.',25,True)
text(s,5.9,3.7,6.7,1.4,'KNN output = 50\nMean output = 720 / 9 = 80',30,True,TEAL)
text(s,.7,5.7,12,1,'Nearest means nearest in intensity within a local window. Both filters read an unchanged input and write a separate output.',23)

s=slide('Settings are selected before final testing','Experimental design',note())
table(s,.6,1.9,12.1,3.8,['Stage','Procedure'],[['Candidates','Windows 3 × 3, 5 × 5, 7 × 7; four k values in each'],['Selection','Minimise average of KNN and mean MSE on validation noise'],['Final test','Three fresh noise realizations, seeds 60701–60703'],['Fair comparison','Same input, window and replicated borders; centre eligible']],widths=[2.6,9.5],size=22)
text(s,.6,6.1,12,.75,'Settings vary by image and noise level. This tests new noise on known images, not new scenes.',22,True,TEAL)

s=slide('Selected window sizes and neighbour counts','Selected settings',note())
table(s,.7,1.9,11.9,4.3,['Image','Noise SD','Window','k'],[[r['image'].title(),f'{int(r["noise_percent"])}%',f'{int(r["window"])} × {int(r["window"])}',str(int(r['k']))] for r in rows],size=23)
text(s,.7,6.4,12,.4,'User override: python run_experiment.py --window 5 --k 18',19,False,GRAY)

for name in ('urban','farmland'):
    for p in (5,10,20):
        s=slide(f'{name.title()}: {p}% uniform noise','Visual comparison',note());four(s,name,p)
    if name=='urban':
        s=slide('Colour detail at 20% noise','Fixed crop',note()+' Central crop [288:480,288:480], identical across methods.');four(s,name,20,True)

s=slide('Mean-squared error across three fresh trials','Measured results',note()+' Values are trial means, in 8-bit intensity units squared; sample SD is available in results/summary.csv.')
table(s,.6,1.9,12.1,4.4,['Image','Noise','Noisy','KNN','Mean'],[[r['image'].title(),f'{int(r["noise_percent"])}%',*[f'{r[m+"_mse"]:.1f}' for m in ('noisy','knn','mean')]] for r in rows],size=22)
text(s,.6,6.5,12,.4,'Lower is better. Full precision and trial variability are included in the project report.',18,False,GRAY)

s=slide('Parameter improvements on the same images','Previous setting versus selected setting',note()+' Baseline is previous k9/window5 applied anew to the current data and same noise seeds. It is not an MSE comparison across different datasets.')
table(s,.6,1.9,12.1,4.4,['Image','Noise','Old KNN (5 × 5, k9)','New KNN','MSE reduction'],[[r['image'].title(),f'{int(r["noise_percent"])}%',f'{r["old_setting_knn_mse"]:.1f}',f'{r["knn_mse"]:.1f}',f'{100*(1-r["knn_mse"]/r["old_setting_knn_mse"]):.1f}%'] for r in rows],size=20)

s=slide('Noise strength and reconstruction error','Measured comparison',note())
for i,name in enumerate(('farmland','urban')):
    x=.65+i*6.35
    text(s,x,1.85,5.8,.4,name.title(),24,True)
    cd=CategoryChartData();cd.categories=['5%','10%','20%']
    for label,method in [('Noisy','noisy'),('KNN','knn'),('Mean','mean')]:
        cd.add_series(label,[row(name,p)[method+'_mse'] for p in (5,10,20)])
    chart=s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS,Inches(x),Inches(2.35),Inches(5.8),Inches(3.9),cd).chart
    chart.has_legend=True;chart.legend.position=XL_LEGEND_POSITION.BOTTOM;chart.legend.font.size=Pt(16)
    chart.value_axis.minimum_scale=0
    for axis in (chart.value_axis,chart.category_axis):axis.tick_labels.font.size=Pt(14)
    for series,clr in zip(chart.series,[GRAY,TEAL,ORANGE]):
        series.format.line.color.rgb=color(clr);series.format.line.width=Pt(2.5)
        series.marker.format.fill.solid();series.marker.format.fill.fore_color.rgb=color(clr)
        series.marker.format.line.color.rgb=color(clr)
text(s,.7,6.45,12,.4,'Mean MSE across three trials; y-axes use separate scales. Noise SD is a percentage of channel mean.',17,False,GRAY)

s=slide('Better images make the trade-off easier to see','Conclusions',note())
text(s,.7,2,12,1,'At 20% noise: mean filtering wins on farmland; KNN wins on the urban crop.',28,True)
text(s,.7,3.45,12,1,'At 5% and 10% on the urban crop, both filters increase MSE relative to the noisy input.',26)
text(s,.7,4.85,12,1,'Dense detail can be damaged more by smoothing than by weak added noise. Lower noise is not a reason to filter more.',26)
text(s,.7,6.25,12,.5,'Conclusions apply to these two satellite crops and tested parameter choices.',21,True,TEAL)

s=slide('Sources and reproducibility','Appendix',note())
text(s,.7,1.9,12,1.3,'Contains modified Copernicus Sentinel data (2016), processed by ESA. Crops and filtered derivatives: CC BY-SA 3.0 IGO.',24)
text(s,.7,3.45,12,1.3,'Run: python run_experiment.py\nCustom k: python run_experiment.py --window 5 --k 18',23,True)
text(s,.7,5,12,1.4,'CSV: every candidate and every test trial\nNPZ: original and processed floating-point images\nReport: complete comparisons, crops and measured errors',23)
from presentation_style import polish
polish(prs, ROOT)
prs.save(ROOT/'GNR607_Satellite_Presentation.pptx')

style='body{font:17px/1.6 system-ui;max-width:1300px;margin:40px auto;padding:0 24px;color:#14243d}h1,h2{line-height:1.2}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}.images{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}img{width:100%;image-rendering:auto}figure{margin:0}figcaption{font-weight:bold}section{margin:45px 0}code{background:#eee}a{color:#007f86}'
html=f'<!doctype html><html lang="en"><meta charset="utf-8"><title>GNR607 revised denoising experiment</title><style>{style}</style><h1>Uniform-noise removal: revised experiment</h1><p>Two 768 × 768 satellite crops. All results, source files and image data are stored in this folder on D:.</p><p><a href="GNR607_Satellite_Presentation.pptx">Download presentation</a> · <a href="results/summary.csv">Summary CSV</a> · <a href="results/parameter_sweep.csv">Every parameter candidate</a> · <a href="results/trials.csv">Every test trial</a></p>'
html+='<h2>Satellite data</h2><p>Sentinel-2, Netherlands: contains modified Copernicus Sentinel data (2016), processed by ESA. Near-infrared contributes to the false colour; vegetation appears red. Two 768 × 768 crops from a 9725 × 10223 JPEG; no resizing or artificial upscaling. The exact ground sampling distance of this processed JPEG is not asserted. These are display channels, not calibrated spectral bands. Source, licence and crop coordinates are in data/source_manifest.json.</p>'
html+='<h2>Method and fair selection</h2><p>For each original channel with mean μ, set σ = pμ and add independent Uniform(−√3σ,+√3σ) samples. p is 5%, 10%, or 20%. RGB channels are processed independently. KNN selects the k intensities nearest to the noisy centre within an odd spatial window, including the centre. Mean filtering averages every entry. Both read an unchanged noisy image; borders are replicated. No clipping or rounding before MSE.</p><p>Candidate windows: 3, 5, 7. Candidate k values: rounded 35%, 55%, 75%, 90% of window area. For each image/noise level, choose the pair minimising the average of KNN MSE and mean MSE on validation seed 60700. Hold the pair fixed for test seeds 60701–60703. This uses clean-reference calibration on the same images; it does not demonstrate generalisation to unseen scenes. Noise streams are paired across levels.</p><p>The accelerated NumPy implementation was checked against the original manual algorithm on nine cases, including k=1 and k=window area. The original manual implementation is retained as core_manual.py. This version uses NumPy sorting/reductions for speed; it is not a claim of library-free computation.</p>'
html+='<h2>Measured results</h2><p>MSE in intensity units squared, mean ± sample standard deviation across three trials. Baseline means the old k=9/window5 setting run on these same satellite crops, not the old Indian Pines MSE.</p><table><tr><th>Image</th><th>Noise</th><th>Window / k</th><th>Noisy</th><th>KNN</th><th>Mean</th><th>Old KNN</th></tr>'
for r in rows:
    html+='<tr>'+''.join('<td>'+v+'</td>' for v in [r['image'],f'{int(r["noise_percent"])}%',f'{int(r["window"])} / {int(r["k"])}',*[f'{r[m+"_mse"]:.2f} ± {r[m+"_sd"]:.2f}' for m in ('noisy','knn','mean','old_setting_knn')]])+'</tr>'
html+='</table><h2>Full images and fixed detail crops</h2><p>Trial 1 is shown consistently, not selected by appearance. Click any image for its PNG. Every panel uses the fixed 0–255 scale; displayed values outside that range saturate. NPZ files preserve the unclipped values used for scoring.</p>'
for name in ('urban','farmland'):
    for p in (5,10,20):
        r=row(name,p);html+=f'<section><h2>{name.title()} — {p}% noise · {int(r["window"])} × {int(r["window"])} window · k={int(r["k"])}</h2>'
        for crop in (False,True):
            if crop:html+='<h3>Same central 192 × 192 region</h3>'
            html+='<div class="images">'
            for kind in ('original','noisy','knn','mean'):
                path=img(name,p,kind,crop).relative_to(ROOT).as_posix();html+=f'<figure><figcaption>{kind.title()}</figcaption><a href="{path}"><img src="{path}" alt="{name} {p}% {kind}"></a></figure>'
            html+='</div>'
        html+='</section>'
html+=f'<h2>Interpretation and sources</h2><p>These 768 × 768 crops preserve source pixels without enlargement. They are from one ESA Sentinel-2 false-colour display composite, not independent satellite acquisitions. Parameter selection cannot eliminate noisy-centre bias or blur. This experiment measures recovery of an 8-bit processed JPEG-derived image from added noise, not recovery of calibrated reflectance or raw sensor noise. RGB processing is channel-wise intensity KNN, not vector-colour or patch-distance KNN.</p><p><a href="{SOURCE}">ESA source image and description</a>. Contains modified Copernicus Sentinel data (2016), processed by ESA. Cropped and synthetically noised/filtered for this project. Licensed under <a href="https://creativecommons.org/licenses/by-sa/3.0/igo/">CC BY-SA 3.0 IGO</a>. Source image hash, crop coordinates and processing are in data/source_manifest.json. SHA256 hashes and original channel means are recorded in results/manifest.json.</p></html>'
html=html.replace('<h2>Measured results</h2>','<h2>Measured results</h2><p><strong>Important outcome:</strong> At 20% noise, averaging wins on farmland and KNN wins on the urban crop. At 5% and 10% in the urban crop, both tested filters increase MSE relative to the noisy input. Small-scale structure is harmed by smoothing. This result must be retained when presenting the experiment.</p>')
(ROOT/'report.html').write_text(html,encoding='utf-8')
print('Saved presentation:',len(prs.slides),'slides; report.html')
