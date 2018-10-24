import csv


class Engine:
    thrust = []
    mass_time = []
    total_trust = 0

    def __init__(self, eng_file, eng_mass_i, eng_mass_f, roc_mass):
        self.eng_file = eng_file
        total_thrust = self.total_trust()

    # Thrust
    # Aray of thrust at time

    def thrust_time(self, eng_file):
        with open(eng_file, 'r') as f:
            next(f)
            reader = csv.reader(f, 'excel')
            for row in reader:
                new_row = [float(row[0]), float(row[1])]
                self.thrust.append(new_row)
        thrust_list = [self.thrust[i][0] for i in range(0, len(self.thrust))]
        thrust_time_list = [self.thrust[i][1] for i in range(0, len(self.thrust))]
        return thrust_list, thrust_time_list

    ## Mass vs time curve
    def total_trust(self):
        total_thrust = 0
        for row in self.thrust:
            total_thrust += row[0]
        return total_thrust

    def mass_time(self, eng_mass_i, eng_mass_f, roc_mass):
        mass_loss = eng_mass_i - eng_mass_f
        mass_reman = eng_mass_i
        mass_time = []
        for row in self.thrust:
            perc = row[0] / self.total_thrust
            mass_loss = mass_reman * perc
            mass_reman -= mass_loss
            mass = roc_mass + mass_reman
            mass_time.append([mass, row[1]])
        return [mass_time[i][0] for i in range(0, len(self.thrust))]
