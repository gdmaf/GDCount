# GDCount

**Automated grain size characterization tool for SEM images**

Developed by the **GDMAF — Grupo de Desenvolvimento de Materiais Funcionais, UNIFEI**

---

## Overview

GDCount is an open-source desktop tool for automated grain segmentation and size characterization in Scanning Electron Microscopy (SEM) images. It combines a U-Net convolutional neural network for initial segmentation with the Segment Anything Model (SAM) for boundary refinement, enabling fast, reproducible, and operator-independent granulometric analysis.

The tool provides a graphical user interface that requires no programming knowledge, making it accessible to researchers and engineers in materials science and related fields.

> ⚠️ **Model scope:** The pre-trained U-Net model (`seg_model.keras`) was trained primarily for SEM images of **equiaxial (rounded/spherical) grains and particles**. Performance on elongated morphologies (needles, plates, rods) may be limited. New morphologies will be adressed in future versions of the software.

---

## Features

- Automated grain segmentation using U-Net + SAM pipeline
- Batch processing of multiple SEM images
- Interactive calibration tool — measure scale, grain distance and minimum area directly on the image
- Pixel-to-micrometer scale calibration
- Equivalent diameter calculation (assuming circular grain cross-section)
- Statistical summary (mean and standard deviation of area and diameter) displayed after processing
- Post-segmentation filters: maximum grain area, maximum grain length, minimum and maximum aspect ratio
- Automatic pore rejection based on centroid intensity
- Overlay image with red crosses marking each counted grain centroid
- CSV output configurable for EN (`.` decimal, `,` separator) or BR (`,` decimal, `;` separator)
- Binary mask output (`.tif`) for each processed image
- Bilingual interface: English and Portuguese
- Portable Windows executable (`.exe`) — no Python installation required

---

## Requirements

### Running from source
- Python 3.10
- Dependencies listed in `requirements.txt`
- Model files (not included in repository due to size — see [Downloading the model files](#downloading-the-model-files)):
  - `seg_model.keras` — pre-trained U-Net model
  - `sam_vit_b_01ec64.pth` — SAM ViT-B checkpoint

### Running the executable (Windows)
- Windows 10 or 11 (64-bit)
- Minimum 8 GB RAM
- Microsoft Visual C++ Redistributable 2015–2022 ([download here](https://aka.ms/vs/17/release/vc_redist.x64.exe))

---

## Downloading the model files

The two model files must be downloaded separately and placed in the same folder as the scripts (or alongside `GDCount.exe` for the Windows executable).

| File | Source | Size |
|------|--------|------|
| `sam_vit_b_01ec64.pth` | [Meta AI — direct download](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth) | ~375 MB |
| `seg_model.keras` | [GDCount Releases page](https://github.com/gdmaf/GDCount/releases) | ~90 MB |

> The `seg_model.keras` file is also available from the [segmenteverygrain repository](https://github.com/zsylvester/segmenteverygrain).

---

## Installation

### From source

```bash
git clone https://github.com/gdmaf/GDCount
cd GDCount
pip install -r requirements.txt
pip install torch torchvision torchaudio
python app_contagem.py
```

Download `seg_model.keras` and `sam_vit_b_01ec64.pth` (see [Downloading the model files](#downloading-the-model-files)) and place them in the same folder as the scripts.

### Windows executable

Download the latest release from the [Releases](https://github.com/gdmaf/GDCount/releases) page, extract the `.zip` file, and run `GDCount.exe`. Download `seg_model.keras` and `sam_vit_b_01ec64.pth` (see [Downloading the model files](#downloading-the-model-files)) and place them in the same folder as the executable.

---

## Usage

1. Launch the application (`GDCount.exe` or `python app_contagem.py`)
2. Click **"Add images"** to select one or more SEM images (`.jpg`, `.png`, `.tif`)
3. Optionally set an output folder
4. Configure segmentation parameters manually or use the **📐 Calibrate from image** tool (recommended)
5. Pre-process the image if necessary (see tips below)
6. Click **"Start Count"** to start processing
7. A progress window opens automatically showing the log and results

### Calibration tool

Click **"📐 Calibrate from image"** to open the interactive calibration wizard:

- **Step 1 — Scale:** draw a line over the image scale bar and enter the real length in µm
- **Step 2 — dbs_max_dist:** click on two neighboring grain centers to measure the minimum distance
- **Step 3 — min_area:** draw a free outline around the smallest grain to measure its area

Use **scroll** to zoom in/out and **right-click drag** to pan. Values are filled automatically after calibration and can still be edited manually.

### Image pre-processing tips

- If your image has **low contrast or sharpness**, enhance it before processing
- If **grain boundaries are brighter than grain interiors**, invert the image colors before processing — otherwise the program may count pores or boundaries as grains. This is especially relevant for particle analysis
- Image enhancement and color inversion can be performed in [ImageJ/FIJI](https://imagej.net/software/fiji/downloads)

### Output files

For each input image (e.g., `sample01.tif`), the following files are generated:

| File | Description |
|---|---|
| `sample01_grain_data.csv` | Per-grain metrics (area, perimeter, equivalent diameter, orientation, etc.) |
| `sample01_grain_mask_all.tif` | Binary segmentation mask (all SAM detections) |
| `sample01_grain_overlay.png` | Original image with red crosses at each counted grain centroid |

---

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `dbs_max_dist` | Minimum distance between grain centroids (px) | 5.0 |
| `min_area` | Minimum grain area (px²) | 150 |
| `px_per_um` | Pixels per micrometer for unit conversion | — |
| `max_area` | Maximum grain area — filters oversized objects (px²) | — |
| `max_length` | Maximum major axis length — filters elongated outliers (px) | — |
| `min_aspect_ratio` | Minimum aspect ratio (major/minor axis) — selects elongated grains | — |
| `max_aspect_ratio` | Maximum aspect ratio — selects rounded grains | — |

> All filter fields are optional. Leave blank for no limit.

---

## Determining segmentation parameters from SEM images

Parameters can be measured directly using the built-in **Calibration Tool** 

---

## Example of use

A sample SEM image (`MEV teste.jpg`) is included in the repository root. Suggested parameters for this image:

- `dbs_max_dist` = 8.5
- `min_area` = 11
- `px_per_um` = 13.8

---

## Known limitations

- The pre-trained U-Net model was optimized for **equiaxial (rounded) grain morphologies**. Results on elongated particles (needles, plates, rods) may be poor.
- Post-segmentation filters (aspect ratio, max area, max length) can help isolate specific grain populations after detection, but cannot compensate for poor initial segmentation of non-equiaxial grains.
- For other morphologies, retraining the U-Net with annotated images of your material is recommended.

---

## Running the tests

A pytest test suite is included in `test_gdcount.py`. Unit tests run without model files; integration tests are skipped automatically when model files are absent.

```bash
pip install pytest pandas
pytest test_gdcount.py -v                       # all tests (integration skipped if no models)
pytest test_gdcount.py -v -m "not integration"  # unit tests only
```

Unit tests verify that the module imports correctly, the test image is present, the equivalent diameter formula is accurate, all documented parameters are exposed, and GPU is disabled on import. Integration tests run the full pipeline on the bundled SEM image (`MEV teste.jpg`) and validate CSV output, binary mask, overlay image, filtering behaviour, and unit conversion.

---

## Building the executable

Requirements: Python 3.10, activated virtual environment with all dependencies installed.

```bash
pip install pyinstaller pyinstaller-hooks-contrib
pyinstaller contador_graos.spec --clean --noconfirm
```

Copy `seg_model.keras`, `sam_vit_b_01ec64.pth`, `logo_gdmaf.png`, `instagram.png`, `linkedin.png`, and `facebook.png` into `dist/ContadorGraos/` after building.

---

## Citation

If you use GDCount in your research, please cite:

```bibtex
@software{gdcount2025,
  author  = {Freire, L.A. and Menezes, E.A.F.M. and Thomazini, D. and Gelfuso, M.V.},
  title   = {GDCount: Automated grain size characterization tool for SEM images},
  year    = {2025},
  url     = {https://github.com/gdmaf/GDCount},
  license = {MIT}
}
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

This tool uses the following open-source projects:

- [segmenteverygrain](https://github.com/zsylvester/segmenteverygrain) — Zoltan Sylvester
- [Segment Anything Model (SAM)](https://github.com/facebookresearch/segment-anything) — Meta AI Research
- [TensorFlow](https://www.tensorflow.org/)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

---

*GDMAF — Grupo de Desenvolvimento de Materiais Funcionais, UNIFEI*  
*Freire, L.A; Menezes, E.A.F.M; Thomazini, D; Gelfuso, M.V*
