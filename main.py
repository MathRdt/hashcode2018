import sys
import operator
from typing import Dict, Tuple, List
from dataclasses import dataclass

def parse_file(filename):
    with open(filename, 'r') as f:
        row, col, veh, nb_ride, bonus, step = map(int, f.readline().split(' '))
        driving = SelfDriving(row, col, veh, bonus, step)
        for i in range(nb_ride):
            s_x, s_y, e_x, e_y, s_t, e_t = map(int, f.readline().split(' '))
            driving.add_ride(s_x, s_y, e_x, e_y, s_t, e_t, i)
        return driving

def print_scores(driving):
    for vehicules in driving.vehicules:
        print(len(vehicules.rides), ' '.join(vehicules.rides) )

@dataclass
class Point():
    x: int
    y: int

@dataclass
class Ride():
    id: int
    pos_start: Point
    pos_end: Point
    time_start: int
    time_end: int
    ride_score:int
    global_score:int

@dataclass
class Vehicule():
    id: int
    current_pos: Point
    rides: List[int]
    next_available_time: int

def dist(a: Point, b: Point):
    return abs(a.x - b.x) + abs(a.y - b.y)

@dataclass
class SelfDriving():
    def __init__(self, row, col, vehicules, bonus, max_time):
        self.row = row
        self.col = col
        self.bonus = bonus
        self.max_time = max_time
        self.score = 0
        self.current_time = 0
        self.rides = []
        self.vehicules = []
        for i in range(vehicules):
            self.vehicules.append(Vehicule(i, Point(0, 0), [],0))

    def add_ride(self, s_x, s_y, e_x, e_y, s_t, e_t, id):
        s_point = Point(s_x, s_y)
        e_point = Point(e_x, e_y)
        ride = Ride(id, s_point, e_point, s_t, e_t,dist(s_point, e_point),0)
        self.rides.append(ride)

    # def determine_max_score_for_vehicule(self, v: Vehicule):
    #     max_score = -1
    #     max_ride = None
    #     max_ride_end_time = 0
    #     for r in self.rides:
    #         score = 0
    #         start_t = max(r.time_start, self.current_time + (dist(v.current_pos, r.pos_start)))
    #         end_time = start_t + r.ride_score
    #         if end_time <= r.time_end and end_time <= self.max_time:
    #             score += r.ride_score
    #             if start_t == r.time_start:
    #                 score += self.bonus
    #         if score > max_score:
    #             max_score = score
    #             max_ride = r
    #             max_ride_end_time = end_time
    #     # if self.current_time > 0 :
    #     #     print(max_score, max_ride, end_time)
    #     return max_score, max_ride, end_time

    def can_he_bonus(self, v:Vehicule, r:Ride):
        if r.time_start < self.current_time + dist(v.current_pos,r.pos_start):
            return False
        return True

    def can_he_get_on_time(self, v:Vehicule, r:Ride):
        start_t = max(r.time_start, self.current_time + (dist(v.current_pos, r.pos_start)))
        end_time = start_t + r.ride_score
        if end_time <= r.time_end and end_time <= self.max_time:
            return True
        return False

    def determine_total_max_score(self):
        self.current_time = min([v.next_available_time for v in self.vehicules])
        if self.current_time < self.max_time:
            vehicules = [v for v in self.vehicules if v.next_available_time == self.current_time]
            for r in self.rides:
                for v in vehicules:
                    if self.can_he_bonus(v,r):
                        end_time = r.time_start + r.ride_score
                        self.update_vehicule(v, r, end_time)
                        self.rides.remove(r)
                        return
                    if self.can_he_get_on_time(v,r):
                        start_t = max(r.time_start, self.current_time + (dist(v.current_pos, r.pos_start)))
                        end_time = start_t + r.ride_score
                        self.update_vehicule(v, r, end_time)
                        self.rides.remove(r)
                        return
            self.current_time = self.max_time +1


    def update_vehicule(self, v: Vehicule, ride:Ride, next_available_time):
        v.next_available_time = next_available_time
        v.current_pos = ride.pos_end
        v.rides.append(str(ride.id))

    def algo_global(self):
        # rides_by_score = sorted(self.rides,key=lambda ride: -ride.ride_score)
        # rides_by_start = sorted(self.rides,key=lambda ride: ride.time_start)
        # rides_by_end = sorted(self.rides,key=lambda ride: ride.time_end)
        # print('score du plus haut au plus bas')
        # print([r.id for r in rides_by_score])
        # print('start du plus court au plus long')
        # print([r.id for r in rides_by_start])
        # print('end du plus court au plus long')
        # print([r.id for r in rides_by_end])

        ride_max_score = max(r.ride_score for r in self.rides)
        ride_latest_end = min(r.time_end for r in self.rides)
        ride_latest_start = max(r.time_start for r in self.rides)

        # print(ride_max_score)
        # print(ride_latest_end)
        # print(ride_latest_start)
        ride_factor = 0.7
        latest_factor = 0.3
        for r in self.rides:
            # print(r.ride_score/ride_max_score)
            # print((ride_latest_start -r.time_start)/ride_latest_start)
            # print(- r.time_end/ride_latest_end)

            r.global_score = ride_factor*(r.ride_score/ride_max_score) - latest_factor*(r.time_end/ride_latest_end) #+ (ride_latest_start -r.time_start)/ride_latest_start
        # print(self.rides)

        self.rides = sorted(self.rides,key=lambda ride: -ride.global_score)
        while self.current_time < self.max_time and self.rides != []:
            self.determine_total_max_score()

def main():
    filename = sys.argv[1]
    driving = parse_file(filename)
    driving.algo_global()
    print_scores(driving)
if __name__ == '__main__':
    main()