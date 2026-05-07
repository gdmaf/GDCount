# GDCount

**Automated grain size characterization tool for SEM images**

Developed by the **GDMAF — Grupo de Desenvolvimento de Materiais Funcionais, UNIFEI**

---

## Overview

GDCount is an open-source desktop tool for automated grain segmentation and size characterization in Scanning Electron Microscopy (SEM) images. It combines a U-Net convolutional neural network for initial segmentation with the Segment Anything Model (SAM) for boundary refinement, enabling fast, reproducible, and operator-independent granulometric analysis.

The tool provides a graphical user interface that requires no programming knowledge, making it accessible to researchers and engineers in materials science and related fields.

---

## Features

- Automated grain segmentation using U-Net + SAM pipeline
- Batch processing of multiple SEM images
- Configurable segmentation parameters (minimum grain distance and area)
- Pixel-to-micrometer scale calibration
- Equivalent diameter calculation (assuming circular grain cross-section)
- Statistical summary (mean and standard deviation of area and diameter)
- CSV output with decimal comma and semicolon separator (Brazilian Excel standard)
- Binary mask output (`.tif`) for each processed image
- Portable Windows executable (`.exe`) — no Python installation required

---

## Requirements

### Running from source
- Python 3.10
- Dependencies listed in `requirements.txt`
- Model files:
  - `seg_model.keras` — pre-trained U-Net model
  - `sam_vit_b_01ec64.pth` — SAM ViT-B checkpoint ([download from Meta AI](https://github.com/facebookresearch/segment-anything))

### Running the executable (Windows)
- Windows 10 or 11 (64-bit)
- Minimum 8 GB RAM
- Microsoft Visual C++ Redistributable 2015–2022 ([download here](https://aka.ms/vs/17/release/vc_redist.x64.exe))

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

Place `seg_model.keras` and `sam_vit_b_01ec64.pth` in the same folder as the scripts.

### Windows executable

Download the latest release from the [Releases](https://github.com/gdmaf/GDCount/releases) page, extract the `.zip` file, and run `GDCount.exe`. The model files must be placed in the same folder as the executable.

---

## Usage

1. Launch the application (`GDCount.exe` or `python app_contagem.py`)
2. Click **"Adicionar imagens"** to select one or more SEM images (`.jpg`, `.png`, `.tif`)
3. Optionally set an output folder
4. Configure segmentation parameters (see section below for how to determine them):
   - **dbs_max_dist** — minimum distance between grain centers (pixels)
   - **min_area** — minimum grain area to be counted (px²)
   - **Pixels per µm** — scale calibration for unit conversion (leave blank for pixel-only output)
5. Pre-process the image if necessary (see tips below)
6. Click **"Iniciar Contagem"** to start processing
7. Results are displayed in the interface and saved to the output folder

### Image pre-processing tips

- If your image has **low contrast or sharpness**, enhance it before processing to improve the distinction between grain boundaries and grain interiors
- If **grain boundaries are brighter than grain interiors**, invert the image colors before processing — otherwise the program may count pores or boundaries as grains. This is especially relevant for particle analysis
- Image enhancement and color inversion can be performed in [ImageJ/FIJI](https://imagej.net/software/fiji/downloads) before loading the image into GDCount

### Output files

For each input image (e.g., `sample01.tif`), the following files are generated:

| File | Description |
|---|---|
| `sample01_grain_data.csv` | Per-grain metrics (area, perimeter, equivalent diameter) |
| `sample01_grain_mask_all.tif` | Binary segmentation mask |

---

## Parameters

| Parameter | Description | Default |
|---|---|---|
| `dbs_max_dist` | Minimum distance between grain centroids (px) | 5.0 |
| `min_area` | Minimum grain area (px²) | 150 |
| `px_per_um` | Pixels per micrometer for unit conversion | — |

---

## Determining segmentation parameters from SEM images

The segmentation parameters (`dbs_max_dist`, `min_area`, and `px_per_um`) must be estimated from the SEM image before processing. This can be done using free software such as [ImageJ/FIJI](https://imagej.net/software/fiji/downloads). Below is a brief guide for each parameter.

### Scale calibration — `px_per_um` (pixels per µm)

1. Open the image in ImageJ
2. Select the **Straight Line** tool and draw a line over the scale bar present in the image
3. Go to **Analyze → Set Scale**
4. In "Distance in pixels", ImageJ will show the pixel length of your line
5. In "Known distance", enter the scale bar length (e.g., `20`)
6. In "Unit of length", enter `um`
7. The resulting pixels/unit value is your `px_per_um`

### Minimum grain distance — `dbs_max_dist`

This value should approximate the smallest expected grain diameter in pixels.

1. Open the image in ImageJ
2. Select the **Straight Line** tool and draw a line across the smallest visible grain
3. Go to **Analyze → Measure** (or press `M`)
4. The "Length" value in pixels is a good estimate for `dbs_max_dist`

### Minimum grain area — `min_area`

This value filters out objects smaller than a grain (noise, pores, artifacts).

1. In ImageJ, draw a line across the smallest grain you want to count and measure its length `d` in pixels
2. Estimate the minimum area as: `min_area ≈ π × (d/2)²`
3. Use a value slightly below this estimate to avoid discarding small but valid grains

> **Tip:** If pores are being counted as grains, increase `min_area` or enhance image contrast before processing. If grain boundaries are brighter than grain interiors, invert the image colors (**Image → Lookup Tables → Invert LUT** in ImageJ) before processing.

---

## Exemple of use

In Github page you can find a SEM exemple so you can use to check how the software works. consider 8.5 as dbs_max_dist, 11 as min_area and 13.8 as Pixels per µm.

## Building the executable

Requirements: Python 3.10, activated virtual environment with all dependencies installed.

```bash
pip install pyinstaller pyinstaller-hooks-contrib
pyinstaller contador_graos.spec --clean --noconfirm
```

Copy `seg_model.keras`, `sam_vit_b_01ec64.pth`, and `logo_gdmaf.png` into `dist/ContadorGraos/` after building.

---

## Citation

If you use GDCount in your research, please cite:

```bibtex
@software{gdcount2025,
  author  = {Freire, L.A. and Menezes, E.A.F.M. and Thomazini, D. and Gelfuso, M.V.},
  title   = {GDCount: Automated grain size characterization tool for SEM images},
  year    = {2025},
  url     = {https://github.com/YOUR_USERNAME/GDCount},
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
