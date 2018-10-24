import math
import pyproj


# Covert ang to rads
def rad(ang):
    return (ang / 360) * 2 * (3.1415926)


# air density (simple model based on nasa function online)
def air_density(alt):
    if alt <= 11000:
        T = 15.04 - (0.00649 * alt)
        p = 101.29 * math.pow((T + 273.1) / 288.08, 5.256)
    elif alt <= 25000:
        T = -56.46
        p = float(22.65 * (math.exp(1.73 - 0.000157 * alt))).real
    else:
        T = -131.21 + (0.00299 * alt)
        p = 2.488 * (((T + 273.1) / 216.6) ** -11.388).real
    d = p / (0.2869 * (T + 273.1))
    return d


# Function to calculate the maximum altitude the rocket reached
def max_alt(alt_list):
    max = alt_list[0]
    for i in alt_list:
        if i > max:
            max = i
    return max

def alt(Ex, Ey, Ez):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    lons, lats, alt = pyproj.transform(ecef, lla, Ex, Ey, Ez, radians=True)
    return alt

def grav_force(Ex, Ey, Ez, m):
    #lat = rad(lat)
    G = -6.67408 * (1 / (10 ** 11))  # Gravitational Constant (m^3 kg^-1 s^-2)
    M = 5.972 * (10 ** 24)  # Earth Mass (kg)
    #a = 6398137  # equatoral radius
    #b = 6356752  # polar radius
    #R = math.sqrt((math.pow(math.pow(a, 2) * math.cos(lat), 2) + (math.pow(math.pow(b, 2) * math.sin(lat), 2))) / (
    #            math.pow(a * math.cos(lat), 2) + (math.pow(b * math.sin(lat), 2))))  # Radius of earth (m)
    r = (Ex**2 + Ey**2 + Ez**2)**0.5
    F = (G * M * m) / (r ** 2)  # Force of gravity (N)
    F_z = F * Ez/r
    F_x = F * (Ex/((Ex**2 + Ey**2)**0.5))
    F_y = F * (Ey/((Ex**2 + Ey**2)**0.5))
    print (F_x, F_y, F_z, sep='\t')
    return F_x, F_y, F_z  # in the -r direction


def drag_force(Ex, Ey, Ez, Evx, Evy, Evz):
    cd = 0.94  # coefficent of drag
    a = 0.00487  # cross sectional area m^2
    p = air_density(alt(Ex, Ey, Ez))  # air density with respect to alt
    # drag = (1/2)*p*v_sqrd*cd*a*(vy/(math.sqrt(v)))
    v_sqrd = (Evx ** 2) + (Evy ** 2) + (Evz ** 2)
    if Evx == 0:
        Ex_drag = 0
    else:
        Ex_drag = (1 / 2) * p * v_sqrd * cd * a * (-Evx / (math.sqrt(v_sqrd)))
    if Evy == 0:
        Ey_drag = 0
    else:
        Ey_drag = (1 / 2) * p * v_sqrd * cd * a * (-Evy / (math.sqrt(Evx**2 + Evy**2)))
    if Evz == 0:
        Ez_drag = 0
    else:
        Ez_drag = (1 / 2) * p * v_sqrd * cd * a * (-Evz / (math.sqrt(Evx**2 + Evy**2)))
    return Ex_drag, Ey_drag, Ez_drag


# Net Force
def net_force(Ex, Ey, Ez, Evx, Evy, Evz, m):
    Fx_drag, Fy_drag, Fz_drag = drag_force(Ex, Ey, Ez, Evx, Evy, Evz)
    Fx_grav, Fy_grav, Fz_grav = grav_force(Ex, Ey, Ez, m)
    Fx = Fx_drag + Fx_grav
    Fy = Fy_drag + Fy_grav
    Fz = Fz_drag + Fz_grav
    return Fx, Fy, Fz

##def lift_force        lift -> pitching moment by reference length

##def side_force        side -> yaw moment by reference length

##Areodynaminc forces are applied at center of press
