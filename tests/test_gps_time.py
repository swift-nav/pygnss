# Copyright (C) 2016 Swift Navigation Inc.
# Contact: engineering@swiftnav.com
#
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.

import pytest
import datetime
import numpy as np
import pandas as pd

from gnss import gps_time


def assert_time_equal(x, y):
    x = pd.to_datetime(x)
    y = pd.to_datetime(y)
    np.testing.assert_array_equal(x, y)


def assert_time_not_equal(x, y):
    try:
        assert_time_equal(x, y)
        assert False
    except AssertionError:
        pass


@pytest.mark.parametrize("t", [
        datetime.datetime(2000, 1, 1),
        datetime.datetime(2016, 1, 20),
        gps_time.GPS_WEEK_0,
        pd.date_range(
            start=datetime.datetime(2016, 1, 1),
            end=datetime.datetime(2016, 1, 20)),
        np.datetime64('2016-01-20T05:00:00.999999Z'),
])
def test_tow_datetime_roundtrip(t):
    wn_tow = gps_time.datetime_to_gps_format(t)
    actual = gps_time.gps_format_to_datetime(**wn_tow)
    # check that they are the same, the result will always be a np.datetime64
    # object, so we first need to convert the original value.
    assert_time_equal(t, actual)
    and_back = gps_time.datetime_to_gps_format(actual)
    np.testing.assert_array_equal(and_back['wn'], wn_tow['wn'])
    np.testing.assert_array_equal(and_back['tow'], wn_tow['tow'])


@pytest.mark.parametrize("utc,dt", [
        (np.datetime64('2012-06-30T23:59:59Z'), 15),
        (np.datetime64('2017-07-01T00:00:00Z'), 18),
])
def test_gps_minus_utc_seconds(utc, dt):
    np.testing.assert_array_equal(gps_time.gps_minus_utc_seconds(utc), dt)


@pytest.fixture(params=[
        (np.datetime64('2015-07-01T00:00:15Z'),
         np.datetime64('2015-06-30T23:59:59Z')),
        (np.datetime64('2015-07-01T00:00:15.9999Z'),
         np.datetime64('2015-06-30T23:59:59.9999Z')),
        (np.datetime64('2015-07-01T00:00:17Z'),
         np.datetime64('2015-07-01T00:00:00Z')),
        (np.datetime64('2017-01-01T00:00:16Z'),
         np.datetime64('2016-12-31T23:59:59Z')),
        (np.datetime64('2017-01-01T00:00:18Z'),
         np.datetime64('2017-01-01T00:00:00Z')),
    ])
def gpst_to_utc_testcase(request):
    # GPS time and corresponding UTC time
    # Unfortunately Python datetime64 cannot handle leap second
    # see http://bugs.python.org/issue23574
    return request.param


def test_gpst_to_utc(gpst_to_utc_testcase):
    gpst, expected_utc = gpst_to_utc_testcase
    utc = gps_time.gpst_to_utc(gpst)
    np.testing.assert_array_equal(utc, expected_utc)


def test_utc_to_gps(gpst_to_utc_testcase):
    # Test single timestamps
    expected_gpst, utc = gpst_to_utc_testcase
    gpst = gps_time.utc_to_gpst(utc)
    result_gpst = gps_time.gps_format_to_datetime(gpst['wn'], gpst['tow'])
    np.testing.assert_array_equal(result_gpst, expected_gpst)
