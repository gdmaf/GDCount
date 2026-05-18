"""
pytest test suite for GDCount.

Unit tests run without model files. Integration tests are skipped
automatically when seg_model.keras or sam_vit_b_01ec64.pth are absent.

Usage:
    pytest test_gdcount.py -v
    pytest test_gdcount.py -v -m "not integration"   # unit tests only
"""

import math
import os

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT  = os.path.dirname(os.path.abspath(__file__))
SEG_MODEL  = os.path.join(REPO_ROOT, "seg_model.keras")
SAM_MODEL  = os.path.join(REPO_ROOT, "sam_vit_b_01ec64.pth")
TEST_IMAGE = os.path.join(REPO_ROOT, "MEV teste.jpg")

_models_present = os.path.isfile(SEG_MODEL) and os.path.isfile(SAM_MODEL)

requires_models = pytest.mark.skipif(
    not _models_present,
    reason=(
        "Model files not found. "
        "Download seg_model.keras and sam_vit_b_01ec64.pth — see README.md."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _first_csv(directory):
    """Return the path of the first *_grain_data.csv found in directory."""
    for name in os.listdir(directory):
        if name.endswith("_grain_data.csv"):
            return os.path.join(directory, name)
    return None


# ===========================================================================
# Unit tests  (no model files required)
# ===========================================================================

def test_import():
    """count_grains module must import without errors."""
    import count_grains  # noqa: F401


def test_test_image_present():
    """Bundled test SEM image must exist in the repository root."""
    assert os.path.isfile(TEST_IMAGE), f"Test image not found: {TEST_IMAGE}"


def test_equivalent_diameter_formula():
    """d = 2·√(A/π)  →  area recovered as  d²·π/4  == A  (within float tolerance)."""
    for area in [100.0, 500.0, 1000.0, 5000.0, 12345.6]:
        d = 2.0 * math.sqrt(area / math.pi)
        recovered = (d ** 2) * math.pi / 4.0
        assert abs(recovered - area) < 1e-6, (
            f"Formula mismatch for area={area}: got {recovered}"
        )


def test_function_signature():
    """count_grains() must expose every documented parameter."""
    import inspect

    import count_grains

    params = inspect.signature(count_grains.count_grains).parameters
    expected = {
        "image_path", "dbs_max_dist", "min_area", "px_per_um",
        "csv_format", "max_area", "max_length", "ar_min", "ar_max",
    }
    missing = expected - set(params)
    assert not missing, f"count_grains() is missing parameters: {missing}"


def test_cuda_disabled_on_import():
    """Importing count_grains must set CUDA_VISIBLE_DEVICES to '-1'."""
    import count_grains  # noqa: F401

    assert os.environ.get("CUDA_VISIBLE_DEVICES") == "-1", (
        "count_grains must disable GPU by setting CUDA_VISIBLE_DEVICES=-1"
    )


# ===========================================================================
# Integration tests  (require model files — skipped if absent)
# ===========================================================================

@requires_models
@pytest.mark.integration
def test_pipeline_completes(tmp_path):
    """Pipeline must run to completion on the bundled test image."""
    import count_grains

    result = count_grains.count_grains(
        TEST_IMAGE,
        output_dir=str(tmp_path),
        dbs_max_dist=8.5,
        min_area=11,
        px_per_um=13.8,
    )
    assert result is not None


@requires_models
@pytest.mark.integration
def test_grains_detected(tmp_path):
    """At least one grain must be detected in the bundled test image."""
    import count_grains

    result = count_grains.count_grains(
        TEST_IMAGE,
        output_dir=str(tmp_path),
        dbs_max_dist=8.5,
        min_area=11,
    )
    assert len(result["area"]) > 0, "Pipeline detected zero grains in test image"


@requires_models
@pytest.mark.integration
def test_output_files_created(tmp_path):
    """CSV, binary mask (.tif), and overlay (.png) must be written to output_dir."""
    import count_grains

    count_grains.count_grains(
        TEST_IMAGE,
        output_dir=str(tmp_path),
        dbs_max_dist=8.5,
        min_area=11,
    )
    files = os.listdir(tmp_path)
    assert any(f.endswith("_grain_data.csv")    for f in files), "CSV not created"
    assert any(f.endswith("_grain_mask_all.tif") for f in files), "Mask not created"
    assert any(f.endswith("_grain_overlay.png")  for f in files), "Overlay not created"


@requires_models
@pytest.mark.integration
def test_csv_en_format(tmp_path):
    """EN CSV must be parseable with comma delimiter and contain rows."""
    import count_grains
    import pandas as pd

    count_grains.count_grains(
        TEST_IMAGE,
        output_dir=str(tmp_path),
        dbs_max_dist=8.5,
        min_area=11,
        csv_format="en",
    )
    path = _first_csv(tmp_path)
    assert path is not None, "No CSV file was created"
    df = pd.read_csv(path, sep=",")
    assert len(df) > 0, "EN CSV is empty"


@requires_models
@pytest.mark.integration
def test_csv_br_format(tmp_path):
    """BR CSV must use semicolon as field delimiter."""
    import count_grains

    count_grains.count_grains(
        TEST_IMAGE,
        output_dir=str(tmp_path),
        dbs_max_dist=8.5,
        min_area=11,
        csv_format="br",
    )
    path = _first_csv(tmp_path)
    assert path is not None, "No CSV file was created"
    with open(path, encoding="utf-8") as fh:
        header = fh.readline()
    assert ";" in header, "BR format CSV must use semicolon as field delimiter"


@requires_models
@pytest.mark.integration
def test_diameter_column_present(tmp_path):
    """Output CSV must contain an equivalent diameter column."""
    import count_grains
    import pandas as pd

    count_grains.count_grains(
        TEST_IMAGE,
        output_dir=str(tmp_path),
        dbs_max_dist=8.5,
        min_area=11,
        csv_format="en",
    )
    path = _first_csv(tmp_path)
    df = pd.read_csv(path, sep=",")
    cols_lower = [c.lower() for c in df.columns]
    assert any("diam" in c for c in cols_lower), (
        f"No diameter column found. Columns: {list(df.columns)}"
    )


@requires_models
@pytest.mark.integration
def test_min_area_filter_reduces_count(tmp_path):
    """Increasing min_area must yield fewer or equal detected grains."""
    import count_grains

    d_low  = tmp_path / "low";  d_low.mkdir()
    d_high = tmp_path / "high"; d_high.mkdir()

    r_low  = count_grains.count_grains(
        TEST_IMAGE, output_dir=str(d_low),  dbs_max_dist=8.5, min_area=11)
    r_high = count_grains.count_grains(
        TEST_IMAGE, output_dir=str(d_high), dbs_max_dist=8.5, min_area=500)

    assert len(r_high["area"]) <= len(r_low["area"]), (
        f"min_area=500 gave {len(r_high['area'])} grains but "
        f"min_area=11 gave only {len(r_low['area'])}"
    )


@requires_models
@pytest.mark.integration
def test_px_per_um_scales_areas(tmp_path):
    """With px_per_um set, reported areas must be smaller than pixel areas."""
    import count_grains

    d_px = tmp_path / "px"; d_px.mkdir()
    d_um = tmp_path / "um"; d_um.mkdir()

    r_px = count_grains.count_grains(
        TEST_IMAGE, output_dir=str(d_px),
        dbs_max_dist=8.5, min_area=11, px_per_um=None)
    r_um = count_grains.count_grains(
        TEST_IMAGE, output_dir=str(d_um),
        dbs_max_dist=8.5, min_area=11, px_per_um=13.8)

    mean_px = r_px["area"].mean()
    mean_um = r_um["area"].mean()
    assert mean_um < mean_px, (
        f"Areas in µm² ({mean_um:.2f}) should be smaller than in px² ({mean_px:.2f})"
    )
