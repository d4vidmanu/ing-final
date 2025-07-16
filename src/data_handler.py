import json
from src.models.ride import Ride  # Asegúrate de que la importación de Ride esté al inicio
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

                # Load users
                self.users = []
                for user_data in data.get('users', []):
                    user = User(user_data['alias'], user_data['name'], user_data.get('carPlate'))
                    self.users.append(user)

                # Load rides
                self.rides = []
                max_id = 0
                for ride_data in data.get('rides', []):
                    # Find the driver user object
                    driver = self.get_user(ride_data['driver'])
                    if driver:
                        ride = Ride(
                            ride_data['rideDateAndTime'],
                            ride_data['finalAddress'],
                            int(ride_data.get('allowedSpaces', 4)),  # Ensure int conversion
                            driver,
                            ride_data.get('status', 'ready')
                        )
                        ride.id = int(ride_data.get('id', len(self.rides) + 1))
                        max_id = max(max_id, ride.id)

                        # Load participants
                        for participant_data in ride_data.get('participants', []):
                            participant_user = self.get_user(participant_data['participant']['alias'])
                            if participant_user:
                                from src.models.RideParticipation import RideParticipation
                                participation = RideParticipation(
                                    participant_user,
                                    participant_data['destination'],
                                    participant_data.get('status', 'waiting')
                                )
                                participation.confirmation = participant_data.get('confirmation')
                                participation.occupied_spaces = participant_data.get('occupiedSpaces', 1)
                                ride.participants.append(participation)

                        self.rides.append(ride)
                        driver.add_ride(ride)

                # Update the ID counter
                Ride._id_counter = max_id + 1

        except FileNotFoundError:
            self.users = []
            self.rides = []

    def get_user(self, alias):
        return next((user for user in self.users if user.alias == alias), None)

    def get_ride(self, ride_id):
        return next((ride for ride in self.rides if ride.id == int(ride_id)), None)

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
        driver.add_ride(ride)  # Add ride to driver's rides
        self.save_data()
        return ride

    def get_active_rides(self):
        """Returns all rides that are not done"""
        return [ride for ride in self.rides if ride.status in ["ready", "inprogress"]]
