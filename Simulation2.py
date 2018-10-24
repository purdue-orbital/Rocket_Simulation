# Approximate Rocket Simulation


import csv
import pandas as pd
import random as rnd
from Forces2 import *
from math import *
import pyproj
import time as t

# Need to find ideal coefficient of drag
# Diameter assumed 0.3m
# Burn time 175 s +- 20 s
# avg thrust 1540 N
# Total mass 700 kg
# Propellant mass 1st stage 85% of first stage mass -> 510 kg +- x
# Total 2nd stage 98 kg
# 2nd Stage propellant 83 kg

## GOAL FOR FINAL CODE
# Iterate through launch angels to minimize delta V in the y(rocket frame) direction, to 150km
# after thrust, maximize delta v in the x(rocket frame) direction
# Minimize time for initial trust burn as third priority
# looking for initial launch angle, relative angle after thrust is 0, final velocity



## Inertial Earth Frame. Reference fram centered at the earth center of gravity (z-up, x-forward, y-right)
# a = 6398137  # equatoral radius
# b = 6356752  # polar radius
# radius = R = math.sqrt((math.pow(math.pow(a, 2) * math.cos(latitude), 2) + (math.pow(math.pow(b, 2) * math.sin(latitude), 2))) / (
#                 math.pow(a * math.cos(latitude), 2) + (math.pow(b * math.sin(latitude), 2))))  # Radius of earth (m)
# Ez = radius * sin(latitude)  # Zero at earths center of gravity, going up through north pole
# Ex = radius * cos(latitude) * cos(longitude)  # Zero at earths center of gravity, going through equator forward
# Ey = radius * cos(latitude) * sin(longitude)  # Zero at earths center of gravity, going through equator right
# with open('LLA.csv', 'r') as f:
# #     next(f)
# #     reader = csv.reader(f, 'excel')
# #     data = []
# #     for row in reader:
# #         data.append(float(row[0]))
# #     latitude = rad(data[0])
# #     longitude = rad(data[1])
# #     altitude = data[2]

with open('initial_position.csv', 'r') as f:
    next(f)
    data = next(f).split(',')
    latitude = rad(float(data[1]))
    longitude = rad(float(data[2]))
    altitude = float(data[0])

# Black Rock Navada. From 25km. 45 degrees from out of earth, due east.
# latitude = rad(28.5729)  # N. Latitude
# longitude = rad(80.6490)  # W. Longitude
# altitude = 0    # Altitude of rocket in meters
ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
Ex, Ey, Ez = pyproj.transform(lla, ecef, longitude, latitude, altitude, radians=True)
Evx, Evy, Evz = 0, 0, 0
r_initial = (Ex ** 2 + Ey ** 2 + Ez ** 2) ** 0.5
print(Ex, Ey, Ez, r_initial, sep="\t")


## Rocket specs
roc_mass = 0.0472  # mass of rocket in kg (not including engine
theta = 45  # Angle of launch from z
phi = 45  # Angle of launch from x
eng_file = "C6.csv"  # engine file location
eng_mass_initial = 0.024  # Loaded engine mass in kg
eng_mass_final = 0.0132  # empty engine mass in kg
total_mass = roc_mass + eng_mass_initial
final_roc_mass = roc_mass + eng_mass_final

## Earth rotation speed at inital position
## Position Velocity Attitude(Earth Centric x-forward y-right z-up)
## latitude and longitude position


# function which adds data at each time step to lists to be exported
def update(Ex, Ey, Ez, Evx, Evy, Evz, time, r):
    Ex_list.append(round(Ex, 6))
    Ey_list.append(round(Ey, 6))
    Ez_list.append(round(Ez, 6))
    Evx_list.append(round(Evx, 6))
    Evy_list.append(round(Evy, 6))
    Evz_list.append(round(Evz, 6))
    time_list.append(round(time, 6))
    r_list.append(round(r, 6))


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
Ex_list, Ey_list, Ez_list = [Ex], [Ey], [Ez]
Evx_list, Evy_list, Evz_list = [Evx], [Evy], [Evz]
time_list = [0]
r_list = [(Ex ** 2 + Ey ** 2 + Ez ** 2) ** 0.5]

# Initializing variables
time = 0  # time in seconds


# while thrust is greater than zero
# this is while the rocket engine is firing
for i in range(len(thrust) - 2):
    r = (Ex ** 2 + Ey ** 2 + Ez ** 2) ** 0.5
    dt = thrust[i][1]
    Efx, Efy, Efz = net_force(Ex, Ey, Ez, Evx, Evy, Evz, mass_list[i])
    Ex += (Evx * dt)
    Ey += (Evy * dt)
    Ez += (Evz * dt)
    dt = thrust[i + 1][1] - thrust[i][1]
    Evz += ((((thrust[i][0] * math.cos(theta)) + Efz) * dt) / mass_list[i])
    Evx += ((((thrust[i][0] * math.sin(theta)*math.cos(phi)) + Efx) * dt) / mass_list[i])
    Evy += ((((thrust[i][0] * math.sin(theta)*math.sin(phi)) + Efy) * dt) / mass_list[i])
    time += dt
    update(Ex, Ey, Ez, Evx, Evy, Evz, time, r)

# After thrust
# This is when the engine is out of fuel and there is no longer a thrust force
time_step = .05  # time time_step in seconds
dt = time_step
while r > r_initial:
    r = (Ex ** 2 + Ey ** 2 + Ez ** 2) ** 0.5
    Efx, Efy, Efz = net_force(Ex, Ey, Ez, Evx, Evy, Evz, final_roc_mass)
    Ex += (Evx * dt)
    Ey += (Evy * dt)
    Ez += (Evz * dt)
    Evx += ((Efx * dt) / final_roc_mass)
    Evy += ((Efy * dt) / final_roc_mass)
    Evz += ((Efz * dt) / final_roc_mass)
    #print(Evx, Evy, Evz, r, sep='\t')
    time += dt
    update(Ex, Ey, Ez, Evx, Evy, Evz, time, r)



## Print When Done
print("Simulations done")

## Make Excel Sheets
sim_sheet = pd.DataFrame({'Time': time_list,
                          'X-Position': Ex_list,
                          'Y-Position': Ey_list,
                          'Z-Position': Ez_list,
                          'X-Velocity': Evx_list,
                          'Y-Velocity': Evy_list,
                          'Z-Velocity': Evz_list,
                          'R': r_list})


thrust_sheet = pd.DataFrame({'Time': thrust_time_list,
                             'Thrust': thrust_list,
                             'Mass': mass_list})

sim_sheet.to_excel('Sim_Data.xlsx', sheet_name='Simulation Data', index=False)
thrust_sheet.to_excel('Thrust_Data.xlsx', sheet_name='Thrust Data', index=False)


