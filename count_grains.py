#!/usr/bin/env python3
"""
Grain Segmentation and Counting Script for MEV Images
"""

import os
import sys
import math
import numpy as np
import pandas as pd
from skimage.io import imread, imsave
from skimage.draw import line as draw_line
import segmenteverygrain as seg
from segment_anything import sam_model_registry

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH          = os.path.join(BASE_DIR, "seg_model.keras")
SAM_CHECKPOINT_PATH = os.path.join(BASE_DIR, "sam_vit_b_01ec64.pth")


def _sample_intensity(gray, cy, cx, radius=5):
    """Amostra intensidade média num raio ao redor do centróide."""
    h, w = gray.shape
    r0 = max(0, cy - radius)
    r1 = min(h, cy + radius)
    c0 = max(0, cx - radius)
    c1 = min(w, cx + radius)
    patch = gray[r0:r1, c0:c1]
    return float(patch.mean()) if patch.size > 0 else 0.0


def _draw_cross(img, cy, cx, size=6, color=(255, 0, 0)):
    """Desenha uma cruz colorida na imagem."""
    h, w = img.shape[:2]
    for dy in range(-size, size + 1):
        r = cy + dy
        if 0 <= r < h and 0 <= cx < w:
            img[r, cx] = color
    for dx in range(-size, size + 1):
        c = cx + dx
        if 0 <= cy < h and 0 <= c < w:
            img[cy, c] = color


def count_grains(image_path, output_dir=None, dbs_max_dist=5.0, min_area=150.0,
                 px_per_um=None, csv_format="en", max_area=None, max_length=None,
                 ar_min=None, ar_max=None, min_intensity=None):

    if output_dir is None or not os.path.isdir(output_dir):
        output_dir = os.path.dirname(os.path.abspath(image_path))

    base_name = os.path.splitext(os.path.basename(image_path))[0]

    def out(suffix):
        return os.path.join(output_dir, f"{base_name}_{suffix}")

    # ── Verificar modelos ─────────────────────────────────────────────────────
    for path, desc in [
        (MODEL_PATH,          "Modelo U-Net (seg_model.keras)"),
        (SAM_CHECKPOINT_PATH, "Modelo SAM (sam_vit_b_01ec64.pth)"),
    ]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{desc} não encontrado em:\n{path}\n\n"
                "Certifique-se de que ambos os modelos estão na mesma pasta que o programa.")

    # ── 1. Carregar imagem ────────────────────────────────────────────────────
    print("[1/6] Carregando imagem...")
    image = imread(image_path)
    if image.ndim == 2:
        image = np.stack([image] * 3, axis=-1)
    elif image.ndim == 3 and image.shape[2] == 4:
        image = image[..., :3]
    elif image.ndim == 3 and image.shape[2] == 1:
        image = np.concatenate([image] * 3, axis=-1)
    elif image.ndim != 3 or image.shape[2] not in (1, 3):
        raise ValueError(f"Configuração de canais não suportada: shape={image.shape}")
    print(f"      Tamanho: {image.shape[1]}×{image.shape[0]} px")

    gray_image = image.mean(axis=2)

    # ── 2. U-Net ──────────────────────────────────────────────────────────────
    print("[2/6] Carregando modelo U-Net...")
    unet = seg.Unet()
    unet.load_weights(MODEL_PATH)

    # ── 3. Predição grosseira ─────────────────────────────────────────────────
    print("[3/6] Predizendo segmentação inicial (U-Net)...")
    mask_coarse = seg.predict_image(image, unet, I=256)

    # ── 4. Rotular grãos ─────────────────────────────────────────────────────
    print(f"[4/6] Rotulando grãos (dbs_max_dist={dbs_max_dist})...")
    labels, centroids = seg.label_grains(image, mask_coarse, dbs_max_dist=dbs_max_dist)
    print(f"      Centróides encontrados: {len(centroids)}")

    # ── 5. SAM ───────────────────────────────────────────────────────────────
    print("[5/6] Carregando e refinando com SAM...")
    sam = sam_model_registry["vit_b"](checkpoint=SAM_CHECKPOINT_PATH)
    all_grains, labels_sam, mask_all, grain_data, fig, ax = seg.sam_segmentation(
        sam, image, mask_coarse, centroids, labels,
        min_area=min_area, plot_image=True,
        remove_edge_grains=True, remove_large_objects=False)

    n_raw = len(all_grains)
    print(f"\n[INFO] Grãos detectados pelo SAM: {n_raw}")

    # ── 6. Filtros geométricos + filtro de poros por intensidade ──────────────
    print("[6/6] Aplicando filtros e salvando...")

    # Limiar automático de intensidade:
    # usa o percentil 25 da distribuição de intensidades da imagem
    # (poros ficam abaixo, grãos ficam acima)
    auto_threshold = float(np.percentile(gray_image, 25))
    print(f"      Limiar automático de intensidade: {auto_threshold:.1f}")

    keep = []
    for idx in range(len(all_grains)):
        if idx >= len(grain_data):
            continue
        row = grain_data.iloc[idx]

        # Filtros geométricos
        if max_area is not None and row.get("area", 0) > max_area:
            continue
        if max_length is not None and row.get("major_axis_length", 0) > max_length:
            continue
        minor = row.get("minor_axis_length", 0)
        ar = row.get("major_axis_length", 0) / minor if minor > 0 else 1.0
        if ar_min is not None and ar < ar_min:
            continue
        if ar_max is not None and ar > ar_max:
            continue

        # Filtro de poros por intensidade no centróide
        try:
            cy = int(row.get("centroid-0", row.get("y", 0)))
            cx = int(row.get("centroid-1", row.get("x", 0)))
        except Exception:
            cy, cx = 0, 0

        intensity = _sample_intensity(gray_image, cy, cx, radius=5)
        if intensity < auto_threshold:
            continue

        keep.append(idx)

    all_grains = [all_grains[i] for i in keep]
    grain_data = grain_data.iloc[keep].reset_index(drop=True)
    n = len(all_grains)
    print(f"      Grãos após filtros: {n} (removidos: {n_raw - n})")
    print(f"\n✅  RESULTADO: {n} grãos detectados.\n")

    # ── Máscara binária (do SAM original — referência completa) ───────────────
    mask_all_uint8 = (mask_all * 255).astype(np.uint8)
    imsave(out("grain_mask_all.tif"), mask_all_uint8)
    print(f"      Máscara binária → {out('grain_mask_all.tif')}")

    # ── Overlay: imagem original + cruzes vermelhas nos centróides válidos ────
    overlay = image.copy().astype(np.uint8)
    for idx in range(len(grain_data)):
        row = grain_data.iloc[idx]
        try:
            cy = int(row.get("centroid-0", row.get("y", 0)))
            cx = int(row.get("centroid-1", row.get("x", 0)))
            _draw_cross(overlay, cy, cx, size=6, color=(255, 0, 0))
        except Exception:
            pass

    imsave(out("grain_overlay.png"), overlay)
    print(f"      Overlay (cruzes) → {out('grain_overlay.png')}")

    # ── CSV ───────────────────────────────────────────────────────────────────
    df = grain_data.copy()

    if px_per_um is not None:
        um_per_px  = 1.0 / px_per_um
        fator_area = um_per_px ** 2
        df['area_um2']    = df['area'] * fator_area
        df['diametro_um'] = df['area_um2'].apply(lambda a: 2 * math.sqrt(a / math.pi))
    else:
        df['diametro_px'] = df['area'].apply(lambda a: 2 * math.sqrt(a / math.pi))

    if csv_format == "br":
        for col in df.select_dtypes(include="number").columns:
            df[col] = df[col].apply(lambda x: f"{x:.4f}".replace(".", ","))
        df.to_csv(out("grain_data.csv"), index=False, sep=";")
    else:
        df.to_csv(out("grain_data.csv"), index=False, sep=",")

    print(f"      CSV salvo      → {out('grain_data.csv')}")
    print("[INFO] Concluído com sucesso.")

    return grain_data


if __name__ == "__main__":
    if len(sys.argv) > 1:
        count_grains(sys.argv[1])
    else:
        print("Uso: python count_grains.py <caminho_da_imagem>")
