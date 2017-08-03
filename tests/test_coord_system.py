from functools import partial

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
    ((38, 122, 0), (-2666781.2433701, 4267742.1051642, 3905443.968419)),
]

approx_dist = partial(approx, abs=1e-6)
approx_deg = partial(approx, abs=1e-7/3600)


def llh_isclose(a, b):
    assert a[:2] == approx_deg(a[:2])
    assert a[2] == approx_dist(a[2])


@pytest.mark.parametrize("ecef, expected", [(l, e) for e, l in test_data])
def test_to_llh(ecef, expected):
    llh_isclose(cs.wgsecef2llh(ecef), expected)


@pytest.mark.parametrize("llh, expected", [(e, l) for e, l in test_data])
def test_to_ecef(llh, expected):
    assert cs.wgsllh2ecef(llh) == approx_dist(expected)


lat_deg = st.floats(min_value=-90, max_value=90)
lon_deg = st.floats(min_value=-180, max_value=180)
alt_m = st.floats(min_value=-0.5 * EARTH_A, max_value=4 * EARTH_A)


@given(st.tuples(lat_deg, lon_deg, alt_m))
def test_llh_ecef_roundtrip(x):
    llh_isclose(cs.wgsecef2llh(cs.wgsllh2ecef(x)), x)


st_ecef = st.floats(min_value=-4*EARTH_A, max_value=4*EARTH_A)


@given(st.tuples(st_ecef, st_ecef, st_ecef))
def test_ecef_llh_roundtrip(x):
    assert cs.wgsllh2ecef(cs.wgsecef2llh(x)) == approx_dist(x)


def test_ecef2ned():
    assert cs.wgsecef2ned((1, 1, 1), (2, 2, 2)) == approx(
        [1.13204490e-01, 1.11022302e-16, -1.72834740e+00])
