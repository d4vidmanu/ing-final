class User:
    def __init__(self, alias, name, car_plate=None):
        self.alias = alias
        self.name = name
        self.car_plate = car_plate  # Puede ser nulo para participantes sin coche
        self.rides = []  # Lista de participaciones en rides

    def add_ride(self, ride):
        self.rides.append(ride)

    def get_user_info(self):
        return {
            "alias": self.alias,
            "name": self.name,
            "carPlate": self.car_plate,
            "rides": [ride.get_ride_info() for ride in self.rides]
        }
