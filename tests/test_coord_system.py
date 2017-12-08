import pytest
import numpy as np

import hypothesis.strategies as st

from pytest import approx
from hypothesis import given
from functools import partial

import gnss.coord_system as cs

EARTH_A = 6378137.0
EARTH_B = 6356752.31424517929553985595703125
SAT_ALTITUDE = 20000000

# (lat_deg, lon_deg, alt_m), (x_m, y_m, z_m)
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
approx_deg = partial(approx, abs=np.deg2rad(1e-7/3600))


def llh_isclose(a, b):
    assert a[:2] == approx_deg(a[:2])
    assert a[2] == approx_dist(a[2])


@pytest.mark.parametrize("ecef, expected", [(l, e) for e, l in test_data])
def test_to_llh(ecef, expected):
    llh_isclose(cs.llh_from_ecef(ecef), expected)


@pytest.mark.parametrize("llh, expected", [(e, l) for e, l in test_data])
def test_to_ecef(llh, expected):
    assert cs.ecef_from_llh(llh) == approx_dist(expected)


lat_rad = st.floats(min_value=np.deg2rad(-90), max_value=np.deg2rad(90))
lon_rad = st.floats(min_value=np.deg2rad(-180), max_value=np.deg2rad(180))
alt_m = st.floats(min_value=-0.5 * EARTH_A, max_value=4 * EARTH_A)


@given(st.tuples(lat_rad, lon_rad, alt_m))
def test_llh_ecef_roundtrip(x):
    llh_isclose(cs.llh_from_ecef(cs.ecef_from_llh(x)), x)


# generate coordinates outside a 800km sphere from the center of the earth
st_ecef = st.floats(min_value=800*1000, max_value=4*EARTH_A) | st.floats(
    min_value=-4*EARTH_A, max_value=-800*1000)


@given(st.tuples(st_ecef, st_ecef, st_ecef))
def test_ecef_llh_roundtrip(x):
    assert cs.ecef_from_llh(cs.llh_from_ecef(x)) == approx_dist(x)


@pytest.mark.parametrize("vector,reference,expected",
                         # this vector should be directly above the reference point so
                         # we expect the north and east components to be zero and the down
                         # component to be -1.
                         [((1., 0, 0), (EARTH_A, 0, 0), (0., 0., -1.)),
                          # Here the vector should be pointing due east, there may be
                          # some second order error which translate into the down
                          # component, hence the small magnitude.
                          ((0., 0.01, 0.), (EARTH_A, 0, 0), (0., 0.01, 0)),
                          # Here the vector should be pointing due east, there may be
                          # some second order error which translate into the down
                          # component, hence the small magnitude.
                          ((0., 0., 0.01), (EARTH_A, 0, 0), (0.01, 0., 0.)),
                          # Now try a spot check with angles
                          ((1, 1, 1), (2, 2, 2), (1.13204490e-01, 1.11022302e-16, -1.72834740e+00))
                         ])
def test_ned_from_ecef(vector, reference, expected):
    actual = cs.ned_from_ecef(vector, reference)
    assert actual == approx(expected)


@pytest.mark.parametrize("target,reference,expected",
                         # Here we place a target directly above the reference in
                         # which case the elevation should be 90
                         [((EARTH_A + SAT_ALTITUDE, 0, 0), (EARTH_A, 0, 0), (0., 90.)),
                          # Satellite is directly East of the reference
                          ((EARTH_A, SAT_ALTITUDE, 0), (EARTH_A, 0, 0), (90., 0.)),
                          # Satellite is directly North of the reference
                          ((EARTH_A, 0, SAT_ALTITUDE), (EARTH_A, 0, 0), (0., 0.)),
                          # Satellite is east at elevation angle of 45.
                          ((EARTH_A + SAT_ALTITUDE, 0, SAT_ALTITUDE), (EARTH_A, 0, 0), (0., 45.)),
                          # Satellite is north east at elevation angle of tan^-1(1, sqrt(2))
                          ((EARTH_A + SAT_ALTITUDE, SAT_ALTITUDE, SAT_ALTITUDE),
                           (EARTH_A, 0, 0),
                           (45., np.rad2deg(np.arctan2(1., np.sqrt(2))))),
                         ])
def test_azimuth_elevation_from_ecef(target, reference, expected):
    azimuth, elevation = cs.azimuth_elevation_from_ecef(target, reference)
    assert azimuth == approx(expected[0])
    assert elevation == approx(expected[1])
    
