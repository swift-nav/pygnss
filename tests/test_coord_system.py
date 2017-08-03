from hypothesis import given
import hypothesis.strategies as st
import pytest
from pytest import approx

import snavutils.coord_system as cs

EARTH_A = 6378137.0
EARTH_B = 6356752.31424517929553985595703125

test_data = [
    ((0, 0, 0), (EARTH_A, 0, 0)),  # On the Equator and Prime Meridian
    ((0, 180, 0), (-EARTH_A, 0, 0)),  # On the Equator
    ((0, 90, 0), (0, EARTH_A, 0)),  # On the Equator
    ((0, -90, 0), (0, -EARTH_A, 0)),  # On the Equator
    ((90, 0, 0), (0, 0, EARTH_B)),  # North Pole
    ((-90, 0, 0), (0, 0, -EARTH_B)),  # South Pole
    ((90, 0, 22), (0, 0, EARTH_B + 22)),  # 22m above north pole
    ((-90, 0, 22), (0, 0, -(EARTH_B + 22))),  # 22m above south pole
    ((0, 0, 22), (EARTH_A + 22, 0, 0)),  # 22m above the equator end prime meridian
    ((0, 180, 22), (-(EARTH_A + 22), 0, 0)),  # 22m above the equator
    ((38, 122, 0), (-2666781.24337, 4267742.10516, 3905443.96842)),
]


@pytest.mark.parametrize("ecef, expected", [(l, e) for e, l in test_data])
def test_to_llh(ecef, expected):
    lla = cs.wgsecef2llh(ecef)
    assert lla == approx(expected, abs=1e-4)


@pytest.mark.parametrize("llh, expected", [(e, l) for e, l in test_data])
def test_to_ecef(llh, expected):
    assert cs.wgsllh2ecef(llh) == approx(expected, abs=1e-04)


lat_deg = st.floats(min_value=-90, max_value=90)
lon_deg = st.floats(min_value=-180, max_value=180)
alt_m = st.floats(min_value=-0.5 * EARTH_A, max_value=4 * EARTH_A)


@given(st.tuples(lat_deg, lon_deg, alt_m))
def test_llh_ecef_roundtrip(x):
    assert cs.wgsecef2llh(cs.wgsllh2ecef(x)) == approx(x, abs=1e-04)


def test_ecef2ned():
    assert cs.wgsecef2ned((1, 1, 1), (2, 2, 2)) == approx(
        [1.13204490e-01, 1.11022302e-16, -1.72834740e+00])
