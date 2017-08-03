import numpy as np
import pytest
from pytest import approx

from snavutils.coord_system import wgsecef2llh, wgsllh2ecef, wgsecef2ned


@pytest.mark.parametrize("ecef,expected",
                         [([-2666781.24337, 4267742.10516, 3905443.96842],
                           [38., 122., 0.]),
                          ])
def test_to_llh(ecef, expected):
    lla = wgsecef2llh(ecef)
    assert lla == approx(expected, abs=1e-4)


@pytest.mark.parametrize("llh,expected",
                         [([38., 122., 0.],
                           [-2666781.24337, 4267742.10516, 3905443.96842]),
                          ])
def test_to_ecef(llh, expected):
    # assert wgsllh2ecef(llh) == approx(expected, rel=1e-05, abs=1e-08)
    assert wgsllh2ecef(llh) == approx(expected)


def test_ecef2ned():
    assert wgsecef2ned((1,1,1), (2,2,2)) == approx([1.13204490e-01, 1.11022302e-16, -1.72834740e+00])
