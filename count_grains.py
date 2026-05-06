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
import segmenteverygrain as seg
from segment_anything import sam_model_registry

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH          = os.path.join(BASE_DIR, "seg_model.keras")
SAM_CHECKPOINT_PATH = os.path.join(BASE_DIR, "sam_vit_b_01ec64.pth")


def count_grains(image_path, output_dir=None, dbs_max_dist=5.0, min_area=150.0, px_per_um=None):
    """
    px_per_um : float – quantos pixels equivalem a 1 µm (ex: 10 significa 10px = 1µm)
                        None = resultados apenas em pixels
    """

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

    n = len(all_grains)
    print(f"\n✅  RESULTADO: {n} grãos detectados.\n")

    # ── 6. Salvar arquivos ────────────────────────────────────────────────────
    print("[6/6] Salvando arquivos...")

    # Máscara binária (grain_mask_all.tif) — mantida pois é útil
    mask_all_uint8 = (mask_all * 255).astype(np.uint8)
    imsave(out("grain_mask_all.tif"), mask_all_uint8)
    print(f"      Máscara binária → {out('grain_mask_all.tif')}")

    # ── Preparar CSV ──────────────────────────────────────────────────────────
    df = grain_data.copy()

    if px_per_um is not None:
        um_per_px   = 1.0 / px_per_um
        fator_area  = um_per_px ** 2
        df['area_um2']    = df['area'] * fator_area
        df['diametro_um'] = df['area_um2'].apply(lambda a: 2 * math.sqrt(a / math.pi))
    else:
        df['diametro_px'] = df['area'].apply(lambda a: 2 * math.sqrt(a / math.pi))

    # Formata com vírgula decimal e salva com separador ponto e vírgula
    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].apply(lambda x: f"{x:.4f}".replace(".", ","))

    df.to_csv(out("grain_data.csv"), index=False, sep=";")
    print(f"      CSV salvo      → {out('grain_data.csv')}")
    print("[INFO] Concluído com sucesso.")

    return grain_data  # retorna floats originais para cálculos na interface


if __name__ == "__main__":
    if len(sys.argv) > 1:
        count_grains(sys.argv[1])
    else:
        print("Uso: python count_grains.py <caminho_da_imagem>")
