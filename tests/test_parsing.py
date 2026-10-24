import json
from pathlib import Path

import pytest

from khetplan.parsing import normalize_numbers, parse_transcript

SAMPLES = json.loads((Path(__file__).resolve().parent.parent / "samples" / "sample_inputs.json").read_text(encoding="utf-8"))["examples"]


@pytest.mark.parametrize("sample", SAMPLES, ids=[s["label"] for s in SAMPLES])
def test_sample_transcripts(sample):
    r = parse_transcript(sample["text"])
    for key, value in sample["expected"].items():
        assert r.fields.get(key) == value, key
    if not sample["expected"]:
        assert r.fields == {}


def test_unsupported_inputs_are_reported_not_guessed():
    r = parse_transcript("5 bigha in Pune for summer")
    codes = {k for k, _ in r.issues}
    assert codes == {"parse_unit_unsupported", "parse_region_unsupported", "parse_season_unsupported"}
    assert set(r.missing) == {"region", "area_value", "season", "water", "risk"}


def test_two_plot_sizes_are_ambiguous():
    r = parse_transcript("२ एकड़ और ३ एकड़")
    assert "area_value" not in r.fields
    assert r.issues[0][0] == "parse_area_ambiguous"


def test_two_seasons_are_ambiguous():
    r = parse_transcript("kharif or rabi, 2 acres")
    assert "season" not in r.fields and r.issues[0][0] == "parse_season_ambiguous"


def test_number_words_and_devanagari_digits():
    assert "2.5" in normalize_numbers("ढाई एकड़")
    assert "1.5" in normalize_numbers("दीड एकर")
    assert "3.5" in normalize_numbers("साडे तीन एकर")
    assert "3.5" in normalize_numbers("साढ़े ३ एकड़")
    assert "1.5" in normalize_numbers("one and a half acres")


def test_no_irrigation_is_rainfed_not_irrigated():
    assert parse_transcript("2 acres, no irrigation").fields["water"] == "rainfed"


def test_empty_transcript():
    r = parse_transcript("   ")
    assert r.fields == {} and r.issues == [("parse_empty", "")]


def test_number_inside_word_is_not_a_number():
    # "दोन" (two) must not be split out of an unrelated longer word
    r = parse_transcript("दोनदा 2 एकर")
    assert r.fields["area_value"] == 2
