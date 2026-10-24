import shutil

import pytest

from khetplan.data import DatasetError, load_dataset


def test_dataset_metadata_and_coverage(ds):
    assert ds.version == "1.1.0"
    assert set(ds.regions()) == {"buldhana"}
    assert ds.seasons() == ["kharif", "rabi"]
    assert len(ds.crops_for("buldhana", "kharif")) == 7
    assert len(ds.crops_for("buldhana", "rabi")) == 6
    assert set(ds.excluded) == {"sugarcane", "onion"}
    assert all(c.value_basis == "A1" for c in ds.crops.values())
    assert "SYNTHETIC" in ds.meta["status"]


def test_every_crop_has_three_language_names(ds):
    for c in ds.crops.values():
        assert c.name("en") and c.name("hi") and c.name("mr")


def test_pairs_only_reference_enabled_same_season_crops(ds):
    for season, pairs in ds.pairs.items():
        for pair in pairs:
            for cid in pair:
                assert ds.crops[cid].season == season


def _copy(tmp_path):
    src = load_dataset.__globals__["DATA_DIR"]
    dst = tmp_path / "data"
    shutil.copytree(src, dst)
    return dst


def test_invalid_numeric_value_is_rejected(tmp_path):
    d = _copy(tmp_path)
    p = d / "crops.csv"
    p.write_text(p.read_text(encoding="utf-8").replace(",0.25,0.15,0.6,0.05,", ",1.7,0.15,0.6,0.05,", 1), encoding="utf-8")
    with pytest.raises(DatasetError, match="yield_cv"):
        load_dataset(d)


def test_unknown_region_is_rejected(tmp_path):
    d = _copy(tmp_path)
    p = d / "crops.csv"
    p.write_text(p.read_text(encoding="utf-8").replace("soybean,Soybean,सोयाबीन,सोयाबीन,buldhana", "soybean,Soybean,सोयाबीन,सोयाबीन,pune"), encoding="utf-8")
    with pytest.raises(DatasetError, match="pune"):
        load_dataset(d)


def test_pair_with_unknown_crop_is_rejected(tmp_path):
    d = _copy(tmp_path)
    p = d / "compatibility.json"
    p.write_text(p.read_text(encoding="utf-8").replace('["pigeonpea", "sorghum"]', '["pigeonpea", "maize"]'), encoding="utf-8")
    with pytest.raises(DatasetError, match="maize"):
        load_dataset(d)
