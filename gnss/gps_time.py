# Copyright (C) 2018 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com>
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.

import numpy as np
import pandas as pd

WEEK_SECS = 7 * 24 * 60 * 60
GPS_WEEK_0 = np.datetime64('1980-01-06T00:00:00Z', 'ns')


def timedelta_from_seconds(seconds):
    """
    Converts from floating point number of seconds to a np.timedelta64.
    The number of seconds will be rounded to the nearest nanosecond.

    Note that nanosecond precision is not sufficient for some GPS
    applications.  For example, computing a range from time of
    flight with nanosecond precision would result in +/- 30 cm of
    error which is likely unsatisfactory.

    Parameters
    ----------
    sec : float
      A floating point representation of the number of seconds

    Returns
    -----------
    td : np.timedelta64
      A timedelta64[ns] object (or array like of them)
    """
    seconds = np.array(seconds)
    return np.round(seconds * 1e9).astype('timedelta64[ns]')


def seconds_from_timedelta(td):
    """
    Converts a np.timedelta64 object into a float number of seconds.
    The resulting number of seconds will be accurate to nanoseconds.

    Note that nanosecond precision is not sufficient for some GPS
    applications.  For example, computing a range from time of
    flight with nanosecond precision would result in +/- 30 cm of
    error which is likely unsatisfactory.

    Parameters
    ----------
    td : np.timedelta64
      A timedelta64 object (or array like of them)

    Returns
    -----------
    sec : float
      The floating point representation of the number of seconds
      in the time delta.
    """
    # make sure td is a np.timdelta64 object
    assert td.dtype.kind == 'm'
    seconds = td / np.timedelta64(1, 's')
    # This may seem out of order, but we first create
    # the seconds variable so it preserves the type of td,
    # then we convert td to a numpy array for the NaT
    # comparison.
    #
    # We have to do the conversion because datetime handling in
    # pandas/numpy is totally whack, and very inconsistent.
    # For example:
    #
    #   > tmp
    #   sid
    #   0   NaT
    #   2   NaT
    #   Name: time, dtype: timedelta64[ns]
    #
    #   > tmp == np.timedelta64('NaT', 'ns')
    #   sid
    #   0    False
    #   2    False
    #   Name: time, dtype: bool
    #
    #   > tmp.values == np.timedelta64('NaT', 'ns')
    #   array([ True,  True], dtype=bool)
    #   tmp.values == np.timedelta64('NaT')
    #   False

    # As shown above comparison only works if tmp is
    # a numpy array, this will convert things like pandas
    # Series to numpy arrays
    td = np.asarray(td)
    # now do the NaT comparison
    is_nat = td == np.timedelta64('NaT', 'ns')
    # and fill in the NaT values with NaN values.
    if td.size == 1 and is_nat:
        seconds = np.nan
    elif np.any(is_nat):
        seconds[is_nat] = np.nan
    return seconds


def gps_format_to_datetime(wn, tow):
    """
    Converts a time using week number and time of week representation
    into a python datetime object.  Note that this does NOT convert
    into UTC.  The resulting datetime object is still in GPS time
    and will have been rounded to nanosecond precision (which is
    too coarse to accurately compute timedeltas such as time of
    flight.

    Parameters
    -----------
    wn : int
      An integer corresponding to the week number of a time.
    tow : float
      A float corresponding to the time of week (in seconds) from
      the beginning of the week number (wn).

    Returns
    -------
    utc : np.datetime64
      Returns a np.datetime64 object (or an array of them) that holds
      the UTC representation of the corresponding gpst.

    See also: gpst_to_utc, datetime_to_tow
    """
    seconds = np.array(tow)
    weeks = np.array(wn)
    return GPS_WEEK_0 + (weeks * WEEK_SECS * 1.e9).astype('timedelta64[ns]') \
      + (seconds * 1.e9).astype('timedelta64[ns]')


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

    See also: tow_to_datetime
    """
    t = pd.to_datetime(t)
    if hasattr(t, 'to_datetime64'):
        t = t.to_datetime64()
    elif hasattr(t, 'values'):
        t = t.values
        assert t.dtype == '<M8[ns]'
    else:
        raise NotImplementedError(
            "Expected either a Timestamp or datetime64 array")
    delta = (t - GPS_WEEK_0)
    assert delta.dtype == '<m8[ns]'
    # compute week number
    wn = np.floor(seconds_from_timedelta(delta) / WEEK_SECS).astype('int64')
    # subtract the whole weeks from timedelta and get the remaining seconds
    delta -= (wn * WEEK_SECS * 1.e9).astype('timedelta64[ns]')

    seconds = seconds_from_timedelta(delta)
    return {'wn': wn, 'tow': seconds}


def gps_minus_utc_seconds(gpst):
    """
    Returns current number of leap seconds between GPS time and UTC time.

    UTC leap second is added between 23:59:59 and 00:00:00 in UTC time.
    This function's input is gps time so the time offset changes e.g.
    between 00:00:16 and 00:00:17 in GPS time.

    Supports dates from 1th Jul 2012.

    Parameters
    ----------
    gpst : np.datetime64, pd.Timestamp, datetime.datetime
      A datetime object (possibly an array) that is convertable to
      datetime64 objects using pd.to_datetime (see the pandas docs
      for more details) in GPS time.

    Returns
    -------
    utc : float
      Returns the number (or an array of them) of leap second values.
    """

    delta_utc = np.zeros(gpst.shape, np.int)
    delta_utc = np.array(delta_utc)
    assert np.all(gpst >= np.datetime64('1999-01-01T00:00:13Z'))
    # difference was 16 seconds on 1st July 2012, add the leap seconds since that
    delta_utc += 13
    delta_utc[gpst >= np.datetime64('2005-01-01T00:00:13Z')] += 1
    delta_utc[gpst >= np.datetime64('2008-01-01T00:00:14Z')] += 1
    delta_utc[gpst >= np.datetime64('2012-07-01T00:00:15Z')] += 1
    delta_utc[gpst >= np.datetime64('2015-07-01T00:00:16Z')] += 1
    delta_utc[gpst >= np.datetime64('2017-01-01T00:00:17Z')] += 1
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
    delta_utc = gps_minus_utc_seconds(gpst)
    delta_utc = np.asarray(delta_utc)

    # now subtract out the delta_utc value (which is given in float seconds)
    return gpst - (delta_utc * 1e9).astype('timedelta64[ns]')


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

    See also: datetime_to_tow, gpst_to_utc
    """
    # GPS-UTC offset is defined in GPS time, so some iteration is needed
    delta_utc_tmp = gps_minus_utc_seconds(utc)
    delta_utc_tmp = np.array(delta_utc_tmp)
    gpst = utc + ((delta_utc_tmp) * 1e9).astype('timedelta64[ns]')

    delta_utc = gps_minus_utc_seconds(gpst)
    delta_utc = np.array(delta_utc)
    utc = pd.to_datetime(utc)
    return datetime_to_gps_format(utc + (delta_utc * 1e9).astype('timedelta64[ns]'))
