import json

from src.models.ride import Ride
from src.models.user import User


class DataHandler:
    def __init__(self, filename='data.json'):
        self.filename = filename
        self.users = []
        self.rides = []
        self.load_data()

    def save_data(self):
        data = {
            'users': [user.get_user_info() for user in self.users],
            'rides': [ride.get_ride_info() for ride in self.rides]
        }
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.users = [User(**user) for user in data.get('users', [])]
                self.rides = [Ride(**ride) for ride in data.get('rides', [])]
        except FileNotFoundError:
            self.users = []
            self.rides = []

    def get_user(self, alias):
        return next((user for user in self.users if user.alias == alias), None)

    def get_ride(self, ride_id):
        return next((ride for ride in self.rides if ride.id == ride_id), None)

    def add_user(self, alias, name, car_plate=None):
        if self.get_user(alias):
            raise ValueError("El usuario ya existe.")
        user = User(alias, name, car_plate)
        self.users.append(user)
        self.save_data()
        return user

    def add_ride(self, ride_date_and_time, final_address, allowed_spaces, driver):
        ride = Ride(ride_date_and_time, final_address, allowed_spaces, driver)
        self.rides.append(ride)
        self.save_data()
        return ride
