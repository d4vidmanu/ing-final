from flask import Flask, jsonify, request
from src.data_handler import DataHandler

app = Flask(__name__)
data_handler = DataHandler()


# CREATE USER ENDPOINT (Missing)
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    """Crear un nuevo usuario"""
    try:
        data = request.json
        if not data or 'alias' not in data or 'name' not in data:
            return jsonify({"error": "Faltan datos requeridos: alias y name"}), 400

        usuario = data_handler.add_user(
            alias=data['alias'],
            name=data['name'],
            car_plate=data.get('carPlate')
        )
        return jsonify(usuario.get_user_info()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Retorna lista de usuarios"""
    usuarios = [usuario.get_user_info() for usuario in data_handler.users]
    return jsonify(usuarios), 200


@app.route('/usuarios/<alias>', methods=['GET'])
def obtener_usuario(alias):
    """Retorna los datos del usuario"""
    usuario = data_handler.get_user(alias)
    if usuario:
        return jsonify(usuario.get_user_info()), 200
    return jsonify({"error": "Usuario no encontrado"}), 404


# CREATE RIDE ENDPOINT (Missing)
@app.route('/usuarios/<alias>/rides', methods=['POST'])
def crear_ride(alias):
    """Crear un nuevo ride"""
    try:
        usuario = data_handler.get_user(alias)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        data = request.json
        if not data or 'rideDateAndTime' not in data or 'finalAddress' not in data or 'allowedSpaces' not in data:
            return jsonify({"error": "Faltan datos requeridos: rideDateAndTime, finalAddress, allowedSpaces"}), 400

        ride = data_handler.add_ride(
            ride_date_and_time=data['rideDateAndTime'],
            final_address=data['finalAddress'],
            allowed_spaces=data['allowedSpaces'],
            driver=usuario
        )
        return jsonify(ride.get_ride_info()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route('/usuarios/<alias>/rides', methods=['GET'])
def obtener_rides_usuario(alias):
    """Retorna los datos de los rides creados por el usuario"""
    usuario = data_handler.get_user(alias)
    if usuario:
        return jsonify([ride.get_ride_info() for ride in usuario.rides]), 200
    return jsonify({"error": "Usuario no encontrado"}), 404


# LIST ACTIVE RIDES ENDPOINT (Missing)
@app.route('/rides/active', methods=['GET'])
def listar_rides_activos():
    """Retorna lista de rides activos"""
    rides_activos = data_handler.get_active_rides()
    return jsonify([ride.get_ride_info() for ride in rides_activos]), 200


@app.route('/usuarios/<alias>/rides/<ride_id>', methods=['GET'])
def obtener_ride(alias, ride_id):
    """Retorna los datos del ride incluyendo los participantes y estadisticas"""
    usuario = data_handler.get_user(alias)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    ride = data_handler.get_ride(ride_id)
    if not ride:
        return jsonify({"error": "Ride no encontrado"}), 404

    ride_info = ride.get_ride_info()
    return jsonify({"ride": ride_info}), 200


@app.route('/usuarios/<alias>/rides/<ride_id>/requestToJoin/<participant_alias>', methods=['POST'])
def solicitar_unirse_ride(alias, ride_id, participant_alias):
    """Solicitar unirse a un ride"""
    try:
        usuario = data_handler.get_user(alias)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        ride = data_handler.get_ride(ride_id)
        if not ride:
            return jsonify({"error": "Ride no encontrado"}), 404

        participant = data_handler.get_user(participant_alias)
        if not participant:
            return jsonify({"error": "Participante no encontrado"}), 404

        data = request.json
        destination = data.get('destination') if data else None
        if not destination:
            return jsonify({"error": "Destino es requerido"}), 400

        ride.add_participant(participant, destination)
        data_handler.save_data()
        return jsonify({"message": "Solicitud de union al ride realizada"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route('/usuarios/<alias>/rides/<ride_id>/accept/<participant_alias>', methods=['POST'])
def aceptar_solicitud_ride(alias, ride_id, participant_alias):
    """Aceptar la solicitud de unirse a un ride"""
    try:
        usuario = data_handler.get_user(alias)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        ride = data_handler.get_ride(ride_id)
        if not ride:
            return jsonify({"error": "Ride no encontrado"}), 404

        # Check if user is the driver
        if ride.driver.alias != alias:
            return jsonify({"error": "Solo el conductor puede aceptar solicitudes"}), 422

        participant = data_handler.get_user(participant_alias)
        if not participant:
            return jsonify({"error": "Participante no encontrado"}), 404

        ride.accept_participant(participant)
        data_handler.save_data()
        return jsonify({"message": "Solicitud aceptada"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route('/usuarios/<alias>/rides/<ride_id>/reject/<participant_alias>', methods=['POST'])
def rechazar_solicitud_ride(alias, ride_id, participant_alias):
    """Rechazar la solicitud de unirse a un ride"""
    try:
        usuario = data_handler.get_user(alias)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        ride = data_handler.get_ride(ride_id)
        if not ride:
            return jsonify({"error": "Ride no encontrado"}), 404

        # Check if user is the driver
        if ride.driver.alias != alias:
            return jsonify({"error": "Solo el conductor puede rechazar solicitudes"}), 422

        participant = data_handler.get_user(participant_alias)
        if not participant:
            return jsonify({"error": "Participante no encontrado"}), 404

        ride.reject_participant(participant)
        data_handler.save_data()
        return jsonify({"message": "Solicitud rechazada"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route('/usuarios/<alias>/rides/<ride_id>/start', methods=['POST'])
def iniciar_ride(alias, ride_id):
    """Iniciar un ride"""
    try:
        usuario = data_handler.get_user(alias)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        ride = data_handler.get_ride(ride_id)
        if not ride:
            return jsonify({"error": "Ride no encontrado"}), 404

        # Check if user is the driver
        if ride.driver.alias != alias:
            return jsonify({"error": "Solo el conductor puede iniciar el ride"}), 422

        ride.start_ride()
        data_handler.save_data()
        return jsonify({"message": "Ride iniciado", "ride": ride.get_ride_info()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route('/usuarios/<alias>/rides/<ride_id>/end', methods=['POST'])
def terminar_ride(alias, ride_id):
    """Terminar un ride"""
    try:
        usuario = data_handler.get_user(alias)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        ride = data_handler.get_ride(ride_id)
        if not ride:
            return jsonify({"error": "Ride no encontrado"}), 404

        # Check if user is the driver
        if ride.driver.alias != alias:
            return jsonify({"error": "Solo el conductor puede terminar el ride"}), 422

        ride.end_ride()
        data_handler.save_data()
        return jsonify({"message": "Ride terminado", "ride": ride.get_ride_info()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


@app.route('/usuarios/<alias>/rides/<ride_id>/unloadParticipant', methods=['POST'])
def bajar_participante_ride(alias, ride_id):
    """Bajar un participante del ride"""
    try:
        usuario = data_handler.get_user(alias)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        ride = data_handler.get_ride(ride_id)
        if not ride:
            return jsonify({"error": "Ride no encontrado"}), 404

        data = request.json
        if not data or 'participant_alias' not in data:
            return jsonify({"error": "participant_alias es requerido"}), 400

        participant = data_handler.get_user(data['participant_alias'])
        if not participant:
            return jsonify({"error": "Participante no encontrado"}), 404

        ride.unload_participant(participant)
        data_handler.save_data()
        return jsonify({"message": "Participante bajado del ride", "ride": ride.get_ride_info()}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


if __name__ == '__main__':
    app.run(debug=True)