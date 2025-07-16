from src.models.RideParticipation import RideParticipation


class Ride:
    def __init__(self, ride_date_and_time, final_address, allowed_spaces, driver, status="ready"):
        self.ride_date_and_time = ride_date_and_time
        self.final_address = final_address
        self.allowed_spaces = allowed_spaces
        self.driver = driver
        self.status = status  # ready, inprogress, done
        self.participants = []  # Lista de participantes en el ride

    def add_participant(self, participant, destination):
        if len(self.participants) < self.allowed_spaces:
            self.participants.append(RideParticipation(participant, destination, "waiting"))
        else:
            raise ValueError("No hay espacios disponibles para este ride")

    def get_ride_info(self):
        return {
            "rideDateAndTime": self.ride_date_and_time,
            "finalAddress": self.final_address,
            "driver": self.driver.alias,
            "status": self.status,
            "participants": [participant.get_participant_info() for participant in self.participants]
        }
