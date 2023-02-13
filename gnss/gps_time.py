# type: ignore
# Copyright (C) 2018 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.

from datetime import datetime

import numpy as np
import pandas as pd

WEEK_SECS = 7 * 24 * 60 * 60
GPS_WEEK_0 = np.datetime64("1980-01-06T00:00:00", "ns")
LEAP_SECOND_DATES = [
    np.datetime64("1981-07-01T00:00:00", "ns"),
    np.datetime64("1982-07-01T00:00:00", "ns"),
    np.datetime64("1983-07-01T00:00:00", "ns"),
    np.datetime64("1985-07-01T00:00:00", "ns"),
    np.datetime64("1988-01-01T00:00:00", "ns"),
    np.datetime64("1990-01-01T00:00:00", "ns"),
    np.datetime64("1991-01-01T00:00:00", "ns"),
    np.datetime64("1992-07-01T00:00:00", "ns"),
    np.datetime64("1993-07-01T00:00:00", "ns"),
    np.datetime64("1994-07-01T00:00:00", "ns"),
    np.datetime64("1996-01-01T00:00:00", "ns"),
    np.datetime64("1997-07-01T00:00:00", "ns"),
    np.datetime64("1999-01-01T00:00:00", "ns"),
    np.datetime64("2006-01-01T00:00:00", "ns"),
    np.datetime64("2009-01-01T00:00:00", "ns"),
    np.datetime64("2012-07-01T00:00:00", "ns"),
    np.datetime64("2015-07-01T00:00:00", "ns"),
    np.datetime64("2017-01-01T00:00:00", "ns"),
]


def gps_format_to_datetime(wn, tow):
    """
    Converts a time using week number and time of week representation
    into a python datetime object.  Note that this does NOT convert
    into UTC.  The resulting datetime object is still in GPS time
    and will have been rounded to nanosecond precision (which is
    too coarse to accurately compute timedeltas such as time of
    flight).

    Parameters
    -----------
    wn : int
      An integer (or array) corresponding to the week number of a time.
    tow : float
      A float (or array) corresponding to the time of week (in seconds) from the
      beginning of the week number (wn).

    Returns
    -------
    utc : pd.Timestamp
      Returns a pd.Timestamp object (or an array of them) that holds
      the UTC representation of the corresponding gpst.

    See also: gpst_to_utc
    """
    seconds = pd.to_timedelta(tow, "s")
    weeks = pd.to_timedelta(np.array(wn) * WEEK_SECS, "s")
    return GPS_WEEK_0 + weeks + seconds


def datetime_to_gps_format(t):
    """
    Converts from a datetime to week number and time of week format.
    NOTE: This does NOT convert between utc and gps time.  The result
    will still be in gps time (so will be off by some number of
    leap seconds).

    Parameters
    ----------
    t : np.datetime64, pd.Timestamp, datetime.datetime
      A datetime object (possibly an array) that is convertable to
      datetime64 objects using pd.to_datetime (see the pandas docs
      for more details).

    Returns
    --------
    wn_tow : dict
      Dictionary with attributes 'wn' and 'tow' corresponding to the
      week number and time of week.
    """
    t = pd.to_datetime(t)
    delta = t - GPS_WEEK_0
    # compute week number
    wn = np.floor(delta.total_seconds() / WEEK_SECS).astype("int64")
    # subtract the whole weeks from timedelta and get the remaining seconds
    delta -= pd.to_timedelta(wn * WEEK_SECS, "s")
    seconds = delta.total_seconds()
    return {"wn": wn, "tow": seconds}


def gps_minus_utc_seconds(gpst):
    """
    Returns current number of leap seconds between GPS time and UTC time.

    UTC leap second is added between 23:59:59 and 00:00:00 in UTC time.
    This function's input is gps time so the time offset changes e.g.
    between 00:00:16 and 00:00:17 in GPS time.

    Parameters
    ----------
    gpst : np.datetime64, pd.Timestamp, datetime.datetime
      A datetime object (possibly an array) that is convertable to
      datetime64 objects using pd.to_datetime (see the pandas docs
      for more details) in GPS time.

    Returns
    -------
    utc : int
      Returns the number (or an array of them) of leap second values.
    """

    delta_utc = np.zeros_like(gpst, int)
    if isinstance(gpst, datetime):
        gpst = np.datetime64(gpst)

    for i, date in enumerate(LEAP_SECOND_DATES):
        delta_utc[gpst >= (date + np.timedelta64(i, "s"))] += 1

    return delta_utc


def gpst_to_utc(gpst):
    """
    Convert a GPS time either in datetime or week number, time of week
    format into UTC.
    Use leap second correction from hard-coded look-up table.

    Note that the output is incorrect during the leap second because of
    Python datetime64 bug (see http://bugs.python.org/issue23574)
    e.g. instead of 2015-06-30T23:59:60Z it returns 2015-07-01T00:00:00Z

    Parameters
    -----------
    gpst : dict-like (or datetime64)
      A dictionary like that has attributes 'wn' and 'tow' which
      correspond to week number and time of week (in seconds) from
      GPST week zero.

    Returns
    -------
    utc : np.datetime64
      Returns a np.datetime64 object (or an array of them) that holds
      the UTC representation of the corresponding gpst.

    """
    if isinstance(gpst, dict):
        gpst = gps_format_to_datetime(gpst["wn"], gpst["tow"])

    gpst = pd.to_datetime(gpst)
    delta_utc = gps_minus_utc_seconds(gpst)
    delta_utc = np.asarray(delta_utc)

    # now subtract out the delta_utc value (which is given in float seconds)
    return gpst - (delta_utc * 1e9).astype("timedelta64[ns]")


def utc_to_gpst(utc):
    """
    Converts from times in utc to the corresponding gps time in
    week number, time of week format.

    Note that the input datetime64 cannot represent the leap second value
    e.g. 2015-06-30T23:59:60Z
    (see http://bugs.python.org/issue23574)

    Parameters
    ----------
    utc : np.datetime64, pd.Timestamp, datetime.datetime
      A datetime object (possibly an array) that is convertable to
      datetime64 objects using pd.to_datetime (see the pandas docs
      for more details).  Take care the times are actually UTC.

    Returns
    -------
    gpst : dict
      A dictionary with attributes 'wn' and 'tow' holding the
      week number and time of week that correspond to the input utc times.

    See also: gpst_to_utc
    """
    # GPS-UTC offset is defined in GPS time, so some iteration is needed

    delta_utc_tmp = gps_minus_utc_seconds(utc)
    delta_utc_tmp = np.array(delta_utc_tmp)
    utc = pd.to_datetime(utc)
    gpst = utc + ((delta_utc_tmp) * 1e9).astype("timedelta64[ns]")

    delta_utc = gps_minus_utc_seconds(gpst)
    delta_utc = np.array(delta_utc)
    return datetime_to_gps_format(utc + (delta_utc * 1e9).astype("timedelta64[ns]"))
