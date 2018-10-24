# Approximate Rocket Simulation


import csv
import pandas as pd
import random as rnd
from Forces import *
from math import *
import pyproj



## Inertial Earth Frame. Reference fram centered at the earth center of gravity (z-up, x-forward, y-right)
# a = 6398137  # equatoral radius
# b = 6356752  # polar radius
# radius = R = math.sqrt((math.pow(math.pow(a, 2) * math.cos(latitude), 2) + (math.pow(math.pow(b, 2) *
#                 math.sin(latitude), 2))) / (math.pow(a * math.cos(latitude), 2) + (math.pow(b *
#                 math.sin(latitude), 2))))  # Radius of earth (m)
# Ez = radius * sin(latitude)  # Zero at earths center of gravity, going up through north pole
# Ex = radius * cos(latitude) * cos(longitude)  # Zero at earths center of gravity, going through equator forward
# Ey = radius * cos(latitude) * sin(longitude)  # Zero at earths center of gravity, going through equator right

latitude = rad(28.5729)  # N. Latitude
longitude = rad(80.6490)  # W. Longitude
altitude = 0 # Altitude of rocket in meters
ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
Ex, Ey, Ez = pyproj.transform(lla, ecef, longitude, latitude, altitude, radians=True)
Evx, Evy, Evz = 0, 0, 0
print(Ex, Ey, Ez, sep="\t")


## Rocket specs
roc_mass = 0.027  # mass of rocket in kg (not including engine
angle = 0  # Angle of launch from straight up
eng_file = "C6.csv"  # engine file location
eng_mass_initial = 0.0156  # Loaded engine mass in kg
eng_mass_final = 0.0097  # empty engine mass in kg
total_mass = roc_mass + eng_mass_initial
sim_runs = 5

## Earth rotation speed at inital position
## Position Velocity Attitude(Earth Centric x-forward y-right z-up)
## latitude and longitude position


# function which adds data at each time step to lists to be exported
def update(vx, vy, altitude, distance, time):
    vx_list.append(round(vx, 4))
    vy_list.append(round(vy, 4))
    alt_list.append(round(altitude, 4))
    dis_list.append(round(distance, 4))
    time_list.append(round(time, 4))


# Thrust
# Creating an array of thrusts and times to be used in the while thrust is true loop
thrust = []
with open(eng_file, 'r') as f:
    next(f)
    reader = csv.reader(f, 'excel')
    for row in reader:
        new_row = [float(row[0]), float(row[1])]
        thrust.append(new_row)
thrust_list = [thrust[i][0] for i in range(0, len(thrust))]
thrust_time_list = [thrust[i][1] for i in range(0, len(thrust))]

# total_mass vs time curve
# this is used to represent the mass loss while the rocket burns fuel
mass_time = []
total_thrust = 0
for row in thrust:
    total_thrust += row[0]

mass_loss = eng_mass_initial - eng_mass_final
mass_reman = eng_mass_initial
for row in thrust:
    percentage = row[0] / total_thrust   # percentage of total thrust to find percentage of mass lost
    mass_loss = mass_reman * percentage
    mass_reman -= mass_loss
    total_mass = roc_mass + mass_reman
    mass_time.append([total_mass, row[1]])
mass_list = [mass_time[i][0] for i in range(0, len(thrust))]

# Lists used to store data and later import data to excel
Ex_list, Ey_list, Ez_list = [], [], []
Evx_list, Evy_list, Evz_list = [], [], []
vx_list = []
vy_list = []
alt_list = []
dis_list = []
time_list = []

# Initializing variables
vx = 0  # velocity in x direction m/s
vy = 0  # velocity in y direction m/s
distance = 0  # distance travels horizontally
time = 0  # time in seconds

# Uncertainty tp be used in monte carlo simulations (not applied yet)
u_ang = 1  # angle uncertainty in degrees
u_alt = 10  # altitude uncertainty

# Randomizing initial variables in range of the uncertainty
angle += rnd.randrange(-u_ang*100, u_ang*100)/100
altitude += rnd.randrange(-u_alt, u_alt)

# while thrust is greater than zero
# this is while the rocket engine is firing
for i in range(len(thrust) - 2):
    fx, fy = net_force(altitude, vx, vy, total_mass, latitude)
    dt = thrust[i + 1][1] - thrust[i][1]
    vx += ((((thrust[i][0] * math.sin(rad(angle))) + fx) * dt) / mass_list[i])
    vy += ((((thrust[i][0] * math.cos(rad(angle))) + fy) * dt) / mass_list[i])
    altitude += (vy * dt)
    distance += (vx * dt)
    time += dt
    update(vx, vy, altitude, distance, time)

# After thrust
# This is when the engine is out of fuel and there is no longer a thrust force
time_step = .05  # time time_step in seconds
dt = time_step
while altitude > 0:
    fx, fy = net_force(altitude, vx, vy, total_mass, latitude)
    vy += ((fy * dt) / total_mass)
    vx += ((fx * dt) / total_mass)
    distance += (vx * dt)
    altitude += (vy * dt)
    time += dt
    update(vx, vy, altitude, distance, time)



## Print When Done
print("Simulations done\nMaximum Altitude: {0:.4f}\nDistance Traveled: {1:.4f}".format(max_alt(alt_list), distance))

## Make Excel Sheets
sim_sheet = pd.DataFrame({'Time': time_list,
                          'X-Velocity': vx_list,
                          'Y-Velocity': vy_list,
                          'Altitude': alt_list,
                          'Distance': dis_list})

thrust_sheet = pd.DataFrame({'Time': thrust_time_list,
                             'Thrust': thrust_list,
                             'Mass': mass_list})

sim_sheet.to_excel('Sim_Data.xlsx', sheet_name='Simulation Data', index=False)
thrust_sheet.to_excel('Thrust_Data.xlsx', sheet_name='Thrust Data', index=False)


