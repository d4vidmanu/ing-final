class RideParticipation:
    def __init__(self, participant, destination, status="waiting"):
        self.confirmation = None  # Confirmación de participación (puede ser None al principio)
        self.participant = participant
        self.destination = destination
        self.occupied_spaces = 1  # Este valor puede cambiar si se ajustan los ocupantes
        self.status = status  # waiting, rejected, confirmed, missing, notmarked, inprogress, done

    def get_participant_info(self):
        return {
            "confirmation": self.confirmation,
            "participant": {
                "alias": self.participant.alias,
                "previousRidesTotal": len(self.participant.rides),
                "previousRidesCompleted": len([ride for ride in self.participant.rides if ride.status == "done"]),
                "previousRidesMissing": len([ride for ride in self.participant.rides if ride.status == "missing"]),
                "previousRidesNotMarked": len([ride for ride in self.participant.rides if ride.status == "notmarked"]),
                "previousRidesRejected": len([ride for ride in self.participant.rides if ride.status == "rejected"])
            },
            "destination": self.destination,
            "occupiedSpaces": self.occupied_spaces,
            "status": self.status
        }

    def accept_participant(self):
        """Marcar al participante como confirmado"""
        self.confirmation = "accepted"
        self.status = "confirmed"  # Cambiar el estado a confirmado

    def change_status(self, new_status):
        """Cambia el estado del participante"""
        valid_status = ["waiting", "rejected", "confirmed", "missing", "notmarked", "inprogress", "done"]
        if new_status in valid_status:
            self.status = new_status
        else:
            raise ValueError(f"Estado {new_status} no válido.")
