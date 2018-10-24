import math


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
    d = p / (0.2869 * (T + 237.1))
    return d


# Function to calculate the maximum altitude the rocket reached
def max_alt(alt_list):
    max = alt_list[0]
    for i in alt_list:
        if i > max:
            max = i
    return max


def grav_force(m, h, lat):
    lat = rad(lat)
    G = -6.67408 * (1 / (10 ** 11))  # Gravitational Constant (m^3 kg^-1 s^-2)
    M = 5.972 * (10 ** 24)  # Earth Mass (kg)
    a = 6398137  # equatoral radius
    b = 6356752  # polar radius
    R = math.sqrt((math.pow(math.pow(a, 2) * math.cos(lat), 2) + (math.pow(math.pow(b, 2) * math.sin(lat), 2))) / (
                math.pow(a * math.cos(lat), 2) + (math.pow(b * math.sin(lat), 2))))  # Radius of earth (m)
    r = R + h  # distance from center of earth to rocket (m)
    F = (G * M * m) / (r ** 2)  # Force of gravity (N)
    return F  # in the -r direction


def drag_force(vx, vy, alt):
    cd = 0.3  # coefficent of drag
    a = 0.0015  # cross sectional area m^2
    p = air_density(alt)  # air density with respect to alt
    # drag = (1/2)*p*v_sqrd*cd*a*(vy/(math.sqrt(v)))
    v_sqrd = (vx ** 2) + (vy ** 2)
    if vx == 0:
        x_drag = 0
    else:
        x_drag = (1 / 2) * p * v_sqrd * cd * a * (vx / (math.sqrt(v_sqrd)))
    if vy == 0:
        y_drag = 0
    else:
        y_drag = (1 / 2) * p * v_sqrd * cd * a * (vy / (math.sqrt(v_sqrd)))
    return x_drag, y_drag


# Net Force
def net_force(alt, vx, vy, mass, lat):
    x_drag, y_drag = drag_force(vx, vy, alt)
    fx = -x_drag
    fy = grav_force(mass, alt, lat) - y_drag
    return fx, fy

##def lift_force        lift -> pitching moment by reference length

##def side_force        side -> yaw moment by reference length

##Areodynaminc forces are applied at center of press

vx_list = []
vy_list = []
alt_list = []
dis_list = []
time_list = []
