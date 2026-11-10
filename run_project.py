"""Run the GNR 607 experiment. See README.md for definitions and commands."""
import argparse
import csv
from html import escape
import json
from pathlib import Path
from subprocess import list2cmdline

from core import add_uniform_noise, mean, moments, mse, smooth_both, summarize, validate_filter
from download_data import download, SOURCE


def load_bands(path, key, bands):
    # Libraries below are used only for image file reading and array conversion.
    if path.suffix.lower() == ".mat":
        from scipy.io import loadmat
        contents = loadmat(path)
        if key not in contents:
            raise ValueError("MAT variable not found: " + key)
        cube = contents[key]
    else:
        import numpy as np
        from PIL import Image
        with Image.open(path) as image:
            cube = np.asarray(image)
    if cube.ndim == 2:
        cube = cube[:, :, None]
    if cube.ndim != 3:
        raise ValueError("Require image with shape (height, width, bands).")
    if bands is None:
        bands = list(range(1, cube.shape[2] + 1))
    if len(set(bands)) != len(bands):
        raise ValueError("Band indices must be unique.")
    result = []
    for b in bands:
        if not 1 <= b <= cube.shape[2]:
            raise ValueError(f"Band {b} outside 1..{cube.shape[2]}.")
        result.append([[float(cube[y, x, b - 1]) for x in range(cube.shape[1])]
                       for y in range(cube.shape[0])])
    return bands, result, list(cube.shape)


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_figures(out, originals, band_ids, images, summary, window, k, interpretation):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for band, original in zip(band_ids, originals):
        low, high = original[0][0], original[0][0]
        for row in original:
            for value in row:
                if value < low:
                    low = value
                if value > high:
                    high = value
        fig, axes = plt.subplots(3, 4, figsize=(12, 9), constrained_layout=True)
        for row_index, percentage in enumerate((5, 10, 20)):
            noisy, knn, average = images[(percentage, band)]
            for column, (title, image) in enumerate(zip(
                    ("Original reference", f"Uniform noise: {percentage}%", f"KNN, k={k}", f"Mean, {window} x {window}"),
                    (original, noisy, knn, average))):
                axes[row_index, column].imshow(image, cmap="gray", vmin=low, vmax=high,
                                               interpolation="nearest")
                axes[row_index, column].set_title(title, fontsize=10)
                axes[row_index, column].set_axis_off()
        fig.suptitle(f"Band {band} | trial 1 | shared original intensity scale | noise parameter: {interpretation}")
        fig.savefig(out / f"comparison_band_{band}.png", dpi=140)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    for label, field, color in (("Noisy input", "noisy", "#737373"),
                                ("KNN", "knn", "#146bc4"), ("Averaging", "average", "#d55e00")):
        ax.errorbar([r["noise_percent"] for r in summary], [r[field + "_mse_mean"] for r in summary],
                    yerr=[r[field + "_mse_trial_sd"] for r in summary],
                    marker="o", capsize=4, label=label, color=color)
    ax.set_xlabel(f"Noise {'standard deviation' if interpretation == 'std' else 'half-width'} (% of band mean)")
    ax.set_ylabel("MSE against original image (native intensity units squared)")
    ax.set_xticks([5, 10, 20])
    ax.set_title(f"Equal-weight band average | k={k}, window={window} x {window}")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.savefig(out / "mse_comparison.png", dpi=160)
    plt.close(fig)


def make_report(out, args, metadata, rows):
    command = ["python", "run_project.py", "--image", str(args.image), "--mat-key", args.mat_key,
               "--bands", *[str(b) for b in metadata["bands_one_based"]], "--k", str(args.k),
               "--window", str(args.window), "--trials", str(args.trials), "--seed", str(args.seed),
               "--noise-parameter", args.noise_parameter, "--output", str(args.output)]
    table = ""
    conclusions = []
    for row in rows:
        cells = [str(row["noise_percent"]) + "%"]
        for method in ("noisy", "knn", "average"):
            cells.append(f'{row[method + "_mse_mean"]:.3f} ± {row[method + "_mse_trial_sd"]:.3f}')
        table += "<tr>" + "".join("<td>" + cell + "</td>" for cell in cells) + "</tr>"
        winner = "KNN" if row["knn_mse_mean"] < row["average_mse_mean"] else "averaging"
        if row["knn_mse_mean"] == row["average_mse_mean"]:
            winner = "neither (equal MSE)"
        conclusions.append(f'At {row["noise_percent"]}% noise, the lower aggregate MSE is obtained by {winner}.')
    band_images = "".join(f'<h3>Band {band}</h3><img src="comparison_band_{band}.png" alt="Original, noisy and filtered band {band}">' for band in metadata["bands_one_based"])
    mode = ("σ = p μ, a = √3 σ" if args.noise_parameter == "std" else "a = p μ, σ = a / √3")
    text = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>GNR 607 — Uniform noise and spatial smoothing</title>
<style>body{{font:16px/1.6 system-ui,sans-serif;max-width:1050px;margin:40px auto;padding:0 24px;color:#17283b}}h1,h2{{line-height:1.2}}table{{border-collapse:collapse;width:100%}}td,th{{padding:12px;border-bottom:1px solid #cbd5e1;text-align:right}}th:first-child,td:first-child{{text-align:left}}img{{width:100%;height:auto}}code{{background:#eef2f6;padding:2px 5px}}.note{{background:#edf5fc;padding:16px;border-left:4px solid #146bc4}}@media print{{h2{{break-after:avoid}}img,table{{break-inside:avoid}}}}</style>
<h1>Uniform noise removal: KNN versus averaging</h1><p>GNR 607 · Reproducible computational experiment</p>
<h2>Objective and data</h2><p>Add uniform noise at three levels, filter with intensity-nearest neighbours and a simple local mean, and compare reconstruction error against the original image.</p>
<p>Input: <code>{escape(str(args.image))}</code>. Loaded shape: {metadata["source_shape"]}; one-based bands: {metadata["bands_one_based"]}. The supplied example uses the corrected Indian Pines AVIRIS cube, with visible and infrared coverage. The source also supplies a land-cover ground-truth map. Source: <a href="{SOURCE}">University of the Basque Country GIC dataset page</a>; original data reference: <a href="https://doi.org/10.4231/R7RX991C">Purdue Indian Pine Test Site 3 dataset</a>.</p>
<p class="note">The land-cover map is not a clean radiometric image and is not used in denoising MSE. The original downloaded image before synthetic corruption is the reference; it may already contain sensor noise. This experiment measures recovery from the added noise.</p>
<h2>Method</h2><ol>
<li>Process each selected band independently in native intensity units. Compute its mean μ manually.</li>
<li>For p = 0.05, 0.10, 0.20, draw n from U(−a, +a), with {mode}. Set Y = X + n. Do not clip, round, or rescale computational data.</li>
<li>For every noisy pixel, use a {args.window} × {args.window} spatial window. Replicate border pixels when the window extends outside the image.</li>
<li>KNN: choose the {args.k} entries with smallest squared intensity differences from the noisy centre, then average them. The centre is eligible; ties use row-major order. Selection uses a manually maintained ordered list.</li>
<li>Averaging: average all {args.window ** 2} entries in exactly the same window. Both methods use exactly the same noisy realization.</li>
<li>Compute MSE = (1/HW) Σ(X − X̂)², including borders. Report each band separately and the equal-weight mean across bands. Since band dimensions match, this equals MSE over all selected samples.</li></ol>
<p>Seed: {args.seed}. Repetitions: {args.trials}. Each trial and band has its own seeded noise stream; across noise levels, the same stream is scaled to the target standard deviation, providing a paired comparison. The table reports mean ± sample standard deviation of aggregate MSE across trials, not a confidence interval. Realized noise mean and population standard deviation are recorded in <code>per_band_results.csv</code>.</p>
<h2>Results</h2><table><tr><th>Noise level</th><th>Noisy input MSE</th><th>KNN MSE</th><th>Averaging MSE</th></tr>{table}</table>
<img src="mse_comparison.png" alt="MSE against noise level"><p>{' '.join(conclusions)}</p>
<h2>Interpretation</h2><p>Averaging can reduce independent noise strongly in uniform areas, but blurs boundaries and small structures. KNN preferentially uses similar intensities and may preserve boundaries, but the noisy centre also guides neighbour selection, so it can retain noise. Neither method is guaranteed to win. Results depend on k, window size, scene texture, spectral band and noise level.</p>
<p>k = 1 reproduces the noisy input, while k = window² reproduces averaging. A larger k generally increases smoothing; this is not a guarantee of lower MSE. Native-unit aggregate MSE gives more influence to bands with larger absolute errors; inspect the per-band results as well. The selected four-band example does not establish performance on all 200 bands.</p>
<h2>Visual comparisons</h2><p>Trial 1 is shown. Each band's panels use one shared display scale derived from the original band; display saturation does not change stored arrays or MSE.</p>{band_images}
<h2>Reproduce and inspect</h2><p>From the project directory run (adjust absolute paths if moving the project):</p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">{escape(list2cmdline(command))}</pre>
<p>The exact arguments and image dimensions for this run are in <code>run_metadata.json</code>. Source and download checksums are in <code>../data/source_manifest.json</code> for the supplied dataset. Trial-1 floating-point originals, noisy images and filtered images are in <code>trial1_images.mat</code>. CSV files contain all numerical results. Filters, selection, mean, noise generator and MSE are written manually in <code>core.py</code>; external libraries handle file I/O, storage and figures only.</p></html>'''
    (out / "report.html").write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, help="MAT cube or a grayscale/RGB image; defaults to downloaded Indian Pines")
    parser.add_argument("--mat-key", default="indian_pines_corrected")
    parser.add_argument("--bands", type=int, nargs="+", help="One-based indices; demo defaults to 20 50 100 180")
    parser.add_argument("--k", type=int, help="Number of intensity-nearest entries, including centre")
    parser.add_argument("--window", type=int, help="Odd spatial window width")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--seed", type=int, default=607)
    parser.add_argument("--noise-parameter", choices=("std", "half-width"), default="std")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    if args.window is None:
        args.window = int(input("Odd window size [5]: ") or "5")
    if args.k is None:
        args.k = int(input("k (1 to window squared) [9]: ") or "9")
    validate_filter(args.window, args.k)
    if args.trials < 1:
        parser.error("--trials must be at least 1")
    if args.image is None:
        args.image = download(Path(__file__).parent / "data")
        if args.bands is None:
            args.bands = [20, 50, 100, 180]
    bands, originals, source_shape = load_bands(args.image, args.mat_key, args.bands)
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    detail, aggregate, snapshots = [], [], {}
    stored_images = {}
    for percentage in (5, 10, 20):
        for trial in range(args.trials):
            trial_scores = {"noisy": [], "knn": [], "average": []}
            for band, original in zip(bands, originals):
                seed = args.seed + trial * 1000003 + band * 1009
                noisy, noise, sigma = add_uniform_noise(original, percentage / 100.0, seed, args.noise_parameter)
                knn, average = smooth_both(noisy, args.window, args.k)
                noise_mean, noise_sd = moments(noise)
                row = {"noise_percent": percentage, "trial": trial + 1, "band": band,
                       "band_mean": mean(original), "target_noise_sd": sigma,
                       "realized_noise_mean": noise_mean, "realized_noise_sd": noise_sd}
                for name, image in (("noisy", noisy), ("knn", knn), ("average", average)):
                    error = mse(original, image)
                    row[name + "_mse"] = error
                    trial_scores[name].append(error)
                detail.append(row)
                if trial == 0:
                    snapshots[(percentage, band)] = (noisy, knn, average)
                    stored_images[f"original_band_{band}"] = original
                    for name, image in (("noisy", noisy), ("knn", knn), ("average", average)):
                        stored_images[f"{name}_p{percentage}_band_{band}"] = image
            record = {"noise_percent": percentage, "trial": trial + 1}
            for name, scores in trial_scores.items():
                record[name + "_mse"] = summarize(scores)[0]
            aggregate.append(record)
            print(f'Noise {percentage:2d}%, trial {trial + 1}: KNN MSE={record["knn_mse"]:.3f}, averaging MSE={record["average_mse"]:.3f}', flush=True)
    summary = []
    for percentage in (5, 10, 20):
        row = {"noise_percent": percentage}
        for name in ("noisy", "knn", "average"):
            mu, sd = summarize([r[name + "_mse"] for r in aggregate if r["noise_percent"] == percentage])
            row[name + "_mse_mean"] = mu
            row[name + "_mse_trial_sd"] = sd
        summary.append(row)
    write_csv(out / "per_band_results.csv", detail)
    write_csv(out / "per_trial_results.csv", aggregate)
    write_csv(out / "summary.csv", summary)
    metadata = {"arguments": {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()},
                "source_shape": source_shape, "bands_one_based": bands,
                "noise_levels_percent": [5, 10, 20], "boundary": "replicate", "center_included": True,
                "mse_reference": "original before adding noise", "clipping": False,
                "rng": "Park-Miller 16807", "seed_formula": "seed + zero_based_trial*1000003 + one_based_band*1009"}
    (out / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    from scipy.io import savemat
    savemat(out / "trial1_images.mat", stored_images, do_compression=True)
    save_figures(out, originals, bands, snapshots, summary, args.window, args.k, args.noise_parameter)
    make_report(out, args, metadata, summary)
    print("Report:", (out / "report.html").resolve())


if __name__ == "__main__":
    main()
