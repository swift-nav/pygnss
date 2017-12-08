# Copyright (C) 2017 Swift Navigation Inc.
# Contact: Swift Navigation <dev@swiftnav.com> 
# This source is subject to the license found in the file 'LICENSE' which must
# be be distributed together with this source. All other rights reserved.


import numpy as np

WGS84_A = 6378137.0
WGS84_IF = 298.257223563
WGS84_F = (1 / WGS84_IF)
WGS84_E = np.sqrt(2 * WGS84_F - WGS84_F * WGS84_F)
WGS84_B = (WGS84_A * (1 - WGS84_F))


def llh_from_ecef(ecef):
    """Convert cartesian ECEF coords to geodetic coordinates.

    Converts from WGS84 Earth Centered, Earth Fixed (ECEF) Cartesian
    coordinates (X, Y and Z) into WGS84 geodetic coordinates (latitude,
    longitude and height).


    Parameters
    ----------
    ecef : array_like length 3
        Coordinates in ECEF

    Returns
    -------
    llh : array_like length 3
        (Latitude(Degrees), Longitude(Degrees), Height(m))
    """

    # Conversion from Cartesian to geodetic coordinates is a much harder
    # problem than conversion from geodetic to Cartesian. There is no
    # satisfactory closed form solution but many different iterative approaches
    # exist.

    # Here we implement a relatively new algorithm due to Fukushima (2006) that
    # is very computationally efficient, not requiring any transcendental
    # function calls during iteration and very few divisions. It also exhibits
    # cubic convergence rates compared to the quadratic rate of convergence
    # seen with the more common algortihms based on the Newton-Raphson method.

    # References: -# "A comparison of methods used in rectangular to Geodetic
    # Coordinates Transformations", Burtch R. R. (2006), American Congress for
    # Surveying and Mapping Annual Conference. Orlando, Florida.  -#
    # "Transformation from Cartesian to Geodetic Coordinates Accelerated by
    # Halleys Method", T. Fukushima (2006), Journal of Geodesy.

    x, y, z = ecef

    lat, lon, alt = None, None, None

    # Distance from polar axis.
    p = np.linalg.norm((x, y))

    # Compute longitude first, this can be done exactly.
    if p == 0:
        lon = 0
    else:
        lon = np.arctan2(y, x)

    # If we are close to the pole then convergence is very slow, treat this is
    # a special case.
    if p < WGS84_A * 1e-16:
        lat = np.copysign(np.pi / 2, z)
        alt = np.fabs(z) - WGS84_B
        return lat, lon, alt

    # Caluclate some other constants as defined in the Fukushima paper.
    P = p / WGS84_A
    e_c = np.sqrt(1 - WGS84_E**2)
    Z = np.fabs(z) * e_c / WGS84_A

    # Initial values for S and C correspond to a zero height solution.
    S = Z
    C = e_c * P

    # Neither S nor C can be negative on the first iteration so
    # starting prev = -1 will not cause and early exit.
    prev_C, prev_S = -1, -1
    A_n, B_n, D_n, F_n = 0, 0, 0, 0

    # Iterate a maximum of 10 times. This should be way more than enough for
    # all sane inputs
    for i in range(10):
        # Calculate some intermmediate variables used in the update step based
        # on the current state.
        A_n = np.sqrt(S * S + C * C)
        D_n = Z * A_n * A_n * A_n + WGS84_E * WGS84_E * S * S * S
        F_n = P * A_n * A_n * A_n - WGS84_E * WGS84_E * C * C * C
        B_n = 1.5 * WGS84_E * S * C * C * (A_n *
                                           (P * S - Z * C) - WGS84_E * S * C)

        # Update step.
        S = D_n * F_n - B_n * S
        C = F_n * F_n - B_n * C

        # The original algorithm as presented in the paper by Fukushima has
        # a problem with numerical stability. S and C can grow very large or
        # small and over or underflow a double. In the paper this is
        # acknowledged and the proposed resolution is to non-dimensionalise the
        # equations for S and C. However, this does not completely solve the
        # problem. The author caps the solution to only a couple of iterations
        # and in this period over or underflow is unlikely but as we require
        # a bit more precision and hence more iterations so this is still
        # a concern for us.
        #
        # As the only thing that is important is the ratio T = S/C, my solution
        # is to divide both S and C by either S or C. The scaling is chosen
        # such that one of S or C is scaled to unity whilst the other is scaled
        # to a value less than one. By dividing by the larger of S or C we
        # ensure that we do not divide by zero as only one of S or C should
        # ever be zero.
        #
        # This incurs an extra division each iteration which the author was
        # explicityl trying to avoid and it may be that this solution is just
        # reverting back to the method of iterating on T directly, perhaps this
        # bears more thought?
        if (S > C):
            C = C / S
            S = 1
        else:
            S = S / C
            C = 1

        # Check for convergence and exit early if we have converged.
        if np.fabs(S - prev_S) < 1e-16 and np.fabs(C - prev_C) < 1e-16:
            break
        else:
            prev_S = S
            prev_C = C

    A_n = np.sqrt(S * S + C * C)
    lat = np.copysign(1.0, ecef[2]) * np.arctan(S / (e_c * C))
    alt = (p * e_c * C + np.fabs(ecef[2]) * S - WGS84_A * e_c * A_n
           ) / np.sqrt(e_c * e_c * C * C + S * S)

    return np.rad2deg(lat), np.rad2deg(lon), alt


def ecef_from_llh(llh):
    """Convert geodetic LLH coordinates to ECEF coordinates.

    Converts from WGS84 geodetic coordinates (latitude, longitude and height)
    into WGS84 Earth Centered, Earth Fixed Cartesian (ECEF) coordinates
    (X, Y and Z).

    Parameters
    ----------
    llh : array_like length 3
        (Latitude(Degrees), Longitude(Degrees), Height(m))

    Returns
    -------
    ecef : array_like length 3
        Coordinates in ECEF
    """

    lat, lon, alt = llh
    lat = np.deg2rad(lat)
    lon = np.deg2rad(lon)

    d = WGS84_E * np.sin(lat)
    N = WGS84_A / np.sqrt(1. - d * d)

    x = (N + alt) * np.cos(lat) * np.cos(lon)
    y = (N + alt) * np.cos(lat) * np.sin(lon)
    z = ((1 - WGS84_E * WGS84_E) * N + alt) * np.sin(lat)

    return x, y, z


def ecef_to_ned_matrix(ref_ecef):
    """Populates a provided 3x3 matrix with the appropriate rotation
    matrix to transform from ECEF to NED coordinates, given the
    provided ECEF reference vector.
    """
    M = np.empty([3, 3])
    llh = np.array(llh_from_ecef(ref_ecef))

    lat_radians = np.deg2rad(llh[0])
    lon_radians = np.deg2rad(llh[1])

    sin_lat = np.sin(lat_radians)
    cos_lat = np.cos(lat_radians)
    sin_lon = np.sin(lon_radians)
    cos_lon = np.cos(lon_radians)

    M[0][0] = -sin_lat * cos_lon
    M[0][1] = -sin_lat * sin_lon
    M[0][2] = cos_lat
    M[1][0] = -sin_lon
    M[1][1] = cos_lon
    M[1][2] = 0.0
    M[2][0] = -cos_lat * cos_lon
    M[2][1] = -cos_lat * sin_lon
    M[2][2] = -sin_lat

    return M


def ned_from_ecef(ecef_vector, reference_location):
    """Convert ECEF coordinates into NED frame of given reference.
    """
    return np.dot(ecef_to_ned_matrix(reference_location), ecef_vector)


def relative_position_in_ned(ecef_target, ecef_reference):
    """Returns the vector between two ECEF points in the NED frame of the
    reference.

    Parameters
    ----------
    ecef_target : array-like length 3
        A length three vector which corresponds to the target position,
        or end point of the desired vector in ECEF frame.
    ecef_reference : array-like length 3
        A length three vector which corresponds to the reference position,
        or the starting point of the desired vector.

    Returns
    -------
    ned : array-like
        A length three vector which points from reference to target in the
        north/east/down reference frame centered at the reference position.
    """
    ecef_target = np.asarray(ecef_target)
    ecef_reference = np.asarray(ecef_reference)
    return ned_from_ecef((ecef_target - ecef_reference), ecef_reference)


def azimuth_elevation_from_ecef(ecef_target, ecef_reference):
    """Returns the azimuth and elevation of a vector pointing from `ref_position`
    to `position` where both are given in ECEF

    Parameters
    ----------
    pos : array-like length 3
        The position in ECEF of the end point of the vector.  Typically
        this would be the location of a satellite.
    ref : array-like length 3
        The reference position in ECEF, or the start of the vector.  Typically
        this would be the location of the receiver.

    Returns
    -------
    azimuth : float
        The azimuth, or the angle between a horizontal projection of the vector
        pointing from `reference position` to `position` and the vector pointing
        due north (degrees)
    elevation : float
        The elevation angle, or the angle between the horizon at the `reference
        position` and the object at `position` (degrees)
    """
    ecef_target = np.asarray(ecef_target)
    ecef_reference = np.asarray(ecef_reference)
    # Calculate the vector from the reference point in the local North, East,
    # Down frame of the reference point. */
    ned = relative_position_in_ned(ecef_target, ecef_reference)
    # atan2 returns angle in range [-pi, pi], usually azimuth is defined in the
    # range [0, 2pi]. */
    azimuth = np.mod(np.arctan2(ned[1], ned[0]), 2 * np.pi)
    elevation = np.arcsin(-ned[2] / np.linalg.norm(ned))

    return np.rad2deg(azimuth), np.rad2deg(elevation)
