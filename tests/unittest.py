import pytest
import sys
import os
import json
from unittest.mock import patch, mock_open

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.user import User
from models.ride import Ride
from models.RideParticipation import RideParticipation
from data_handler import DataHandler
from controller import app


class TestRideSharing:

    def setup_method(self):
        """Setup method that runs before each test - Inicialización"""
        # Create test users
        self.driver = User("jperez", "Juan Perez", "ABC123")
        self.passenger1 = User("lgomez", "Luis Gomez")
        self.passenger2 = User("mrodriguez", "Maria Rodriguez")

        # Create test ride
        self.ride = Ride("2025/07/15 22:00", "Av Javier Prado 456, San Borja", 3, self.driver)

        # Add ride to driver
        self.driver.add_ride(self.ride)

        # Create Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

    # ==================== SUCCESS TEST CASES (4) ====================

    def test_create_user_success(self):
        """Caso de éxito: Crear un usuario con datos válidos"""
        # Inicialización
        with patch('src.data_handler.DataHandler.save_data'), \
                patch('src.data_handler.DataHandler.load_data'):
            # Mock data handler to return empty users list
            with patch('src.data_handler.DataHandler.get_user', return_value=None):
                user_data = {
                    "alias": "testuser",
                    "name": "Test User",
                    "carPlate": "TEST123"
                }

                # Ejecución
                response = self.client.post('/usuarios',
                                            json=user_data,
                                            content_type='application/json')

                # Verificación o Aserción
                assert response.status_code == 201
                response_data = json.loads(response.data)
                assert response_data['alias'] == "testuser"
                assert response_data['name'] == "Test User"
                assert response_data['carPlate'] == "TEST123"

    def test_add_participant_to_ride_success(self):
        """Caso de éxito: Agregar participante a un ride con espacios disponibles"""
        # Inicialización
        destination = "Av Aramburú 245, Surquillo"

        # Ejecución
        self.ride.add_participant(self.passenger1, destination)

        # Verificación o Aserción
        assert len(self.ride.participants) == 1
        assert self.ride.participants[0].participant.alias == "lgomez"
        assert self.ride.participants[0].destination == destination
        assert self.ride.participants[0].status == "waiting"

    def test_accept_participant_success(self):
        """Caso de éxito: Aceptar solicitud de participante en estado waiting"""
        # Inicialización
        self.ride.add_participant(self.passenger1, "Av Aramburú 245, Surquillo")

        # Ejecución
        self.ride.accept_participant(self.passenger1)

        # Verificación o Aserción
        participant = self.ride.participants[0]
        assert participant.status == "confirmed"
        assert participant.confirmation == True

    def test_start_ride_success(self):
        """Caso de éxito: Iniciar ride con todos los participantes confirmados o rechazados"""
        # Inicialización
        self.ride.add_participant(self.passenger1, "Av Aramburú 245, Surquillo")
        self.ride.add_participant(self.passenger2, "Av Benavides 123, Miraflores")
        self.ride.accept_participant(self.passenger1)
        self.ride.reject_participant(self.passenger2)

        # Ejecución
        self.ride.start_ride()

        # Verificación o Aserción
        assert self.ride.status == "inprogress"
        confirmed_participant = next(p for p in self.ride.participants if p.participant.alias == "lgomez")
        assert confirmed_participant.status == "inprogress"
        rejected_participant = next(p for p in self.ride.participants if p.participant.alias == "mrodriguez")
        assert rejected_participant.status == "rejected"

    # ==================== ERROR TEST CASES (3) ====================

    def test_add_duplicate_participant_error(self):
        """Caso de error: Intentar agregar el mismo participante dos veces al mismo ride"""
        # Inicialización
        self.ride.add_participant(self.passenger1, "Av Aramburú 245, Surquillo")

        # Ejecución y Verificación
        with pytest.raises(ValueError) as exc_info:
            self.ride.add_participant(self.passenger1, "Otro destino")

        # Aserción
        assert "El participante ya tiene una solicitud para este ride" in str(exc_info.value)

    def test_accept_participant_no_space_error(self):
        """Caso de error: Intentar aceptar participante cuando no hay espacios disponibles"""
        # Inicialización - Crear ride con 1 solo espacio
        small_ride = Ride("2025/07/15 22:00", "Av Javier Prado 456, San Borja", 1, self.driver)
        small_ride.add_participant(self.passenger1, "Destino 1")
        small_ride.add_participant(self.passenger2, "Destino 2")

        # Aceptar el primer participante (ocupa el único espacio)
        small_ride.accept_participant(self.passenger1)

        # Ejecución y Verificación
        with pytest.raises(ValueError) as exc_info:
            small_ride.accept_participant(self.passenger2)

        # Aserción
        assert "No hay espacios disponibles para confirmar más participantes" in str(exc_info.value)

    def test_start_ride_with_pending_participants_error(self):
        """Caso de error: Intentar iniciar ride con participantes en estado waiting"""
        # Inicialización
        self.ride.add_participant(self.passenger1, "Av Aramburú 245, Surquillo")
        self.ride.add_participant(self.passenger2, "Av Benavides 123, Miraflores")
        # Solo aceptamos uno, dejamos el otro en waiting
        self.ride.accept_participant(self.passenger1)

        # Ejecución y Verificación
        with pytest.raises(ValueError) as exc_info:
            self.ride.start_ride()

        # Aserción
        assert "Hay participantes con solicitudes pendientes" in str(exc_info.value)

    # ==================== ADDITIONAL TESTS ====================

    def test_end_ride_marks_inprogress_as_notmarked(self):
        """Caso de éxito: Al terminar ride, participantes en progreso se marcan como notmarked"""
        # Inicialización
        self.ride.add_participant(self.passenger1, "Av Aramburú 245, Surquillo")
        self.ride.accept_participant(self.passenger1)
        self.ride.start_ride()

        # Ejecución
        self.ride.end_ride()

        # Verificación o Aserción
        assert self.ride.status == "done"
        participant = self.ride.participants[0]
        assert participant.status == "notmarked"

    def test_unload_participant_success(self):
        """Caso de éxito: Bajar participante del ride en progreso"""
        # Inicialización
        self.ride.add_participant(self.passenger1, "Av Aramburú 245, Surquillo")
        self.ride.accept_participant(self.passenger1)
        self.ride.start_ride()

        # Ejecución
        self.ride.unload_participant(self.passenger1)

        # Verificación o Aserción
        participant = self.ride.participants[0]
        assert participant.status == "done"

    def test_join_ride_after_started_error(self):
        """Caso de error: Intentar unirse a un ride ya iniciado"""
        # Inicialización
        self.ride.status = "inprogress"

        # Ejecución y Verificación
        with pytest.raises(ValueError) as exc_info:
            self.ride.add_participant(self.passenger1, "Av Aramburú 245, Surquillo")

        # Aserción
        assert "Solo se puede unir a un ride antes de que inicie" in str(exc_info.value)

    def test_participant_statistics_calculation(self):
        """Caso de éxito: Verificar cálculo correcto de estadísticas de participante"""
        # Inicialización
        # Crear múltiples rides para el historial
        ride1 = Ride("2025/07/15 22:00", "Destino 1", 3, self.driver)
        ride2 = Ride("2025/07/16 22:00", "Destino 2", 3, self.driver)

        self.passenger1.add_ride(ride1)
        self.passenger1.add_ride(ride2)

        # Agregar participaciones con diferentes estados
        participation1 = RideParticipation(self.passenger1, "Destino A", "done")
        participation2 = RideParticipation(self.passenger1, "Destino B", "missing")

        ride1.participants.append(participation1)
        ride2.participants.append(participation2)

        # Ejecución
        stats = participation1.get_participant_info()

        # Verificación o Aserción
        assert stats['participant']['alias'] == "lgomez"
        assert stats['participant']['previousRidesTotal'] == 2
        assert stats['participant']['previousRidesCompleted'] == 1
        assert stats['participant']['previousRidesMissing'] == 1