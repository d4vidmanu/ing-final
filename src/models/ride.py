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

    def start_ride(self):
        """Inicia el ride: cambia el estado de los participantes a 'inprogress' y de los no confirmados a 'missing'"""
        if self.status == "ready":
            # Cambiar el estado de los participantes no confirmados a 'missing'
            for participation in self.participants:
                if participation.status == "waiting":  # Si está esperando
                    participation.status = "missing"

            # Cambiar el estado de los participantes confirmados a 'inprogress'
            for participation in self.participants:
                if participation.status == "confirmed":  # Si está confirmado
                    participation.status = "inprogress"

            # Cambiar el estado del ride a 'inprogress'
            self.status = "inprogress"

    def end_ride(self):
        """Termina el ride: cambia el estado de los participantes en 'inprogress' a 'notmarked'"""
        if self.status == "inprogress":
            # Cambiar el estado de los participantes en 'inprogress' a 'notmarked'
            for participation in self.participants:
                if participation.status == "inprogress":
                    participation.status = "notmarked"

            # Cambiar el estado del ride a 'done'
            self.status = "done"

    def get_ride_info(self):
        return {
            "rideDateAndTime": self.ride_date_and_time,
            "finalAddress": self.final_address,
            "driver": self.driver.alias,
            "status": self.status,
            "participants": [participant.get_participant_info() for participant in self.participants]
        }
