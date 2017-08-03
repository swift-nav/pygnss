import numpy as np

WGS84_A = 6378137.0
WGS84_IF = 298.257223563
WGS84_F = (1 / WGS84_IF)
WGS84_E = np.sqrt(2 * WGS84_F - WGS84_F * WGS84_F)
WGS84_B = (WGS84_A * (1 - WGS84_F))


def wgsecef2llh(ecef):
    # llh = [None, None, None]
    lat, lon, alt = None, None, None
    p = np.linalg.norm(ecef[:2])

    if p != 0:
        lon = np.arctan2(ecef[1], ecef[0])
    else:
        lon = 0

    if p < WGS84_A * 1e-16:
        lat = np.copysign(np.pi / 2, ecef[2])
        alt = np.fabs(ecef[2]) - WGS84_B
        return np.rad2deg(lat), np.rad2deg(lon), alt

    P = p / WGS84_A
    e_c = np.sqrt(1 - WGS84_E**2)
    # e_c = np.sqrt(WGS84_E * WGS84_A - 1)
    Z = np.fabs(ecef[2]) * e_c / WGS84_A

    S = Z
    C = e_c * P

    prev_C, prev_S = -1, -1
    A_n, B_n, D_n, F_n = 0, 0, 0, 0
    for i in range(10):
        A_n = np.sqrt(S * S + C * C)
        D_n = Z * A_n * A_n * A_n + WGS84_E * WGS84_E * S * S * S
        F_n = P * A_n * A_n * A_n - WGS84_E * WGS84_E * C * C * C
        B_n = 1.5 * WGS84_E * S * C * C * (A_n *
                                           (P * S - Z * C) - WGS84_E * S * C)

        S = D_n * F_n - B_n * S
        C = F_n * F_n - B_n * C

        if (S > C):
            C = C / S
            S = 1
        else:
            S = S / C
            C = 1

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


def wgsllh2ecef(llh):
    lat, lon, alt = llh
    lat, lon = np.deg2rad(lat), np.deg2rad(lon)

    ecef = [None, None, None]
    d = WGS84_E * np.sin(lat)
    N = WGS84_A / np.sqrt(1. - d*d)

    ecef[0] = (N + alt) * np.cos(lat) * np.cos(lon)
    ecef[1] = (N + alt) * np.cos(lat) * np.sin(lon)
    ecef[2] = ((1 - WGS84_E*WGS84_E)*N + alt) * np.sin(lat)

    return ecef


def ecef2ned_matrix(ref_ecef):
    M = np.empty([3, 3])
    llh = np.empty([3])
    llh = np.array(wgsecef2llh(ref_ecef))
    llh[0], llh[1] = np.deg2rad(llh[0]), np.deg2rad(llh[1])

    sin_lat = np.sin(llh[0])
    cos_lat = np.cos(llh[0])
    sin_lon = np.sin(llh[1])
    cos_lon = np.cos(llh[1])

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


def wgsecef2ned(pos, ref):
    return np.matmul(ecef2ned_matrix(ref), pos)


def wgsecef2azel(pos, ref):

    # Calculate the vector from the reference point in the local North, East,
    # Down frame of the reference point. */
    ned = wgsecef2ned(pos-ref, pos, ref)

    az = np.atan2(ned[1], ned[0])
    # atan2 returns angle in range [-pi, pi], usually azimuth is defined in the
    # range [0, 2pi]. */
    if (az < 0):
        az += 2*np.pi

    el = np.asin(-ned[2]/np.linalg.norm(ned))

    return az, el
