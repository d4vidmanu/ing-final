from src.models.RideParticipation import RideParticipation


class Ride:
    _id_counter = 1

    def __init__(self, ride_date_and_time, final_address, allowed_spaces, driver, status="ready"):
        self.id = Ride._id_counter
        Ride._id_counter += 1
        self.ride_date_and_time = ride_date_and_time
        self.final_address = final_address
        self.allowed_spaces = int(allowed_spaces)  # Ensure it's an integer
        self.driver = driver
        self.status = status  # ready, inprogress, done
        self.participants = []  # Lista de participantes en el ride

    def add_participant(self, participant, destination):
        # Check if participant already has a request for this ride
        existing_participant = next((p for p in self.participants if p.participant.alias == participant.alias), None)
        if existing_participant:
            raise ValueError("El participante ya tiene una solicitud para este ride")

        # Check if ride is still in ready status
        if self.status != "ready":
            raise ValueError("Solo se puede unir a un ride antes de que inicie")

        # Check available spaces
        confirmed_participants = len([p for p in self.participants if p.status == "confirmed"])
        if confirmed_participants >= self.allowed_spaces:
            raise ValueError("No hay espacios disponibles para este ride")

        self.participants.append(RideParticipation(participant, destination, "waiting"))

    def accept_participant(self, participant):
        # Find the participant in waiting status
        participant_obj = next((p for p in self.participants
                                if p.participant.alias == participant.alias and p.status == "waiting"), None)

        if not participant_obj:
            raise ValueError("No se encontró solicitud pendiente para este participante")

        # Check if there are available spaces
        confirmed_participants = len([p for p in self.participants if p.status == "confirmed"])
        if confirmed_participants >= self.allowed_spaces:
            raise ValueError("No hay espacios disponibles para confirmar más participantes")

        participant_obj.status = "confirmed"
        participant_obj.confirmation = True

    def reject_participant(self, participant):
        # Find the participant in waiting status
        participant_obj = next((p for p in self.participants
                                if p.participant.alias == participant.alias and p.status == "waiting"), None)

        if not participant_obj:
            raise ValueError("No se encontró solicitud pendiente para este participante")

        participant_obj.status = "rejected"
        participant_obj.confirmation = False

    def start_ride(self):
        # Check if ride is in ready status
        if self.status != "ready":
            raise ValueError("El ride no está en estado ready")

        # Check if all participants are either confirmed or rejected
        pending_participants = [p for p in self.participants if p.status not in ["confirmed", "rejected"]]
        if pending_participants:
            raise ValueError("Hay participantes con solicitudes pendientes")

        # Get confirmed participants who should be present
        confirmed_participants = [p for p in self.participants if p.status == "confirmed"]

        # For now, assume all confirmed participants are present
        # In a real scenario, you might want to check who's actually present
        for participant in confirmed_participants:
            participant.status = "inprogress"

        self.status = "inprogress"

    def end_ride(self):
        # Check if ride is in progress
        if self.status != "inprogress":
            raise ValueError("El ride no está en progreso")

        # Mark participants still in progress as "notmarked"
        for participant in self.participants:
            if participant.status == "inprogress":
                participant.status = "notmarked"

        self.status = "done"

    def unload_participant(self, participant):
        # Find the participant in inprogress status
        participant_obj = next((p for p in self.participants
                                if p.participant.alias == participant.alias and p.status == "inprogress"), None)

        if not participant_obj:
            raise ValueError("Participante no encontrado o no está en el ride")

        participant_obj.status = "done"

    def get_ride_info(self):
        return {
            "id": self.id,
            "rideDateAndTime": self.ride_date_and_time,
            "finalAddress": self.final_address,
            "allowedSpaces": self.allowed_spaces,  # Add this field
            "driver": self.driver.alias,
            "status": self.status,
            "participants": [participant.get_participant_info() for participant in self.participants]
        }