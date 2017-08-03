import numpy as np

WGS84_A = 6378137.0
WGS84_IF = 298.257223563
WGS84_F = (1 / WGS84_IF)
WGS84_E = np.sqrt(2 * WGS84_F - WGS84_F * WGS84_F)
print(WGS84_E)
WGS84_B = (WGS84_A * (1 - WGS84_F))


def wgesecef2llh(ecef):
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
