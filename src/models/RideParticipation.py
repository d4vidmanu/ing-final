class RideParticipation:
    def __init__(self, participant, destination, status="waiting"):
        self.confirmation = None  # Confirmación de participación (puede ser None al principio)
        self.participant = participant
        self.destination = destination
        self.occupied_spaces = 1  # Este valor puede cambiar si se ajustan los ocupantes
        self.status = status  # waiting, rejected, confirmed, missing, notmarked, inprogress, done

    def get_participant_info(self):
        # Count rides based on participation status, not ride status
        participant_rides = []

        # Get all rides where this participant has been involved
        for ride in self.participant.rides:
            for participation in ride.participants:
                if participation.participant.alias == self.participant.alias:
                    participant_rides.append(participation)

        # Count different statuses
        total_rides = len(participant_rides)
        completed_rides = len([p for p in participant_rides if p.status == "done"])
        missing_rides = len([p for p in participant_rides if p.status == "missing"])
        notmarked_rides = len([p for p in participant_rides if p.status == "notmarked"])
        rejected_rides = len([p for p in participant_rides if p.status == "rejected"])

        return {
            "confirmation": self.confirmation,
            "participant": {
                "alias": self.participant.alias,
                "previousRidesTotal": total_rides,
                "previousRidesCompleted": completed_rides,
                "previousRidesMissing": missing_rides,
                "previousRidesNotMarked": notmarked_rides,
                "previousRidesRejected": rejected_rides
            },
            "destination": self.destination,
            "occupiedSpaces": self.occupied_spaces,
            "status": self.status
        }