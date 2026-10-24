import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from khetplan.data import load_dataset  # noqa: E402
from khetplan.models import FarmInputs  # noqa: E402


@pytest.fixture(scope="session")
def ds():
    return load_dataset()


@pytest.fixture
def farm():
    def make(**kw):
        base = dict(region="buldhana", area_value=2.0, area_unit="acre", season="kharif", year=2027, water="rainfed", risk=50)
        base.update(kw)
        return FarmInputs(**base)
    return make
