from flask import Flask, jsonify, request
from src.data_handler import DataHandler

app = Flask(__name__)
data_handler = DataHandler()


@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    """Crea un nuevo usuario"""
    data = request.get_json()
    alias = data.get('alias')
    name = data.get('name')
    car_plate = data.get('carPlate', None)  # Optional

    if alias and name:
        # Crear un nuevo usuario
        new_user = data_handler.add_user(alias, name, car_plate)  # Llama a add_user con los parámetros directamente
        return jsonify(new_user.get_user_info()), 201
    return jsonify({"error": "Faltan datos necesarios"}), 400


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


@app.route('/usuarios/<alias>/rides', methods=['GET'])
def obtener_rides_usuario(alias):
    """Retorna los datos de los rides creados por el usuario"""
    usuario = data_handler.get_user(alias)
    if usuario:
        return jsonify([ride.get_ride_info() for ride in usuario.rides]), 200
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/usuarios/<alias>/rides/<ride_id>', methods=['GET'])
def obtener_ride(alias, ride_id):
    """Retorna los datos del ride incluyendo los participantes y estadisticas"""
    usuario = data_handler.get_user(alias)
    if usuario:
        ride = data_handler.get_ride(ride_id)
        if ride:
            ride_info = ride.get_ride_info()
            return jsonify(ride_info), 200
        return jsonify({"error": "Ride no encontrado"}), 404
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/usuarios/<alias>/rides/<ride_id>/requestToJoin/<participant_alias>', methods=['POST'])
def solicitar_unirse_ride(alias, ride_id, participant_alias):
    """Solicitar unirse a un ride"""
    usuario = data_handler.get_user(alias)
    if usuario:
        ride = data_handler.get_ride(ride_id)
        if ride:
            participant = data_handler.get_user(participant_alias)
            if participant and ride.status == "ready" and len(ride.participants) < ride.allowed_spaces:
                ride.add_participant(participant, "waiting")
                return jsonify({"message": "Solicitud de union al ride realizada"}), 200
            return jsonify({"error": "No se puede unir al ride, estado no valido o sin espacio"}), 422
        return jsonify({"error": "Ride no encontrado"}), 404
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/usuarios/<alias>/rides/<ride_id>/accept/<participant_alias>', methods=['POST'])
def aceptar_solicitud_ride(alias, ride_id, participant_alias):
    """Aceptar la solicitud de unirse a un ride"""
    usuario = data_handler.get_user(alias)
    if usuario:
        ride = data_handler.get_ride(ride_id)
        if ride:
            participant = data_handler.get_user(participant_alias)
            if participant:
                if any(p.participant.alias == participant_alias for p in ride.participants if p.status == "waiting"):
                    ride.accept_participant(participant)
                    return jsonify({"message": "Solicitud aceptada"}), 200
                return jsonify({"error": "Solicitud no encontrada o ya aceptada"}), 422
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({"error": "Ride no encontrado"}), 404
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/usuarios/<alias>/rides/<ride_id>/reject/<participant_alias>', methods=['POST'])
def rechazar_solicitud_ride(alias, ride_id, participant_alias):
    """Rechazar la solicitud de unirse a un ride"""
    usuario = data_handler.get_user(alias)
    if usuario:
        ride = data_handler.get_ride(ride_id)
        if ride:
            participant = data_handler.get_user(participant_alias)
            if participant:
                if any(p.participant.alias == participant_alias for p in ride.participants if p.status == "waiting"):
                    ride.reject_participant(participant)
                    return jsonify({"message": "Solicitud rechazada"}), 200
                return jsonify({"error": "Solicitud no encontrada"}), 422
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({"error": "Ride no encontrado"}), 404
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/usuarios/<alias>/rides/<ride_id>/start', methods=['POST'])
def iniciar_ride(alias, ride_id):
    """Iniciar un ride"""
    usuario = data_handler.get_user(alias)
    if usuario:
        ride = data_handler.get_ride(ride_id)
        if ride:
            if ride.status == "ready" and all(p.status in ["confirmed", "rejected"] for p in ride.participants):
                ride.start_ride()
                return jsonify({"message": "Ride iniciado", "ride": ride.get_ride_info()}), 200
            return jsonify({"error": "Ride no esta listo o hay participantes pendientes"}), 422
        return jsonify({"error": "Ride no encontrado"}), 404
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/usuarios/<alias>/rides/<ride_id>/end', methods=['POST'])
def terminar_ride(alias, ride_id):
    """Terminar un ride"""
    usuario = data_handler.get_user(alias)
    if usuario:
        ride = data_handler.get_ride(ride_id)
        if ride:
            if ride.status == "inprogress":
                ride.end_ride()
                return jsonify({"message": "Ride terminado", "ride": ride.get_ride_info()}), 200
            return jsonify({"error": "Ride no esta en progreso"}), 422
        return jsonify({"error": "Ride no encontrado"}), 404
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/usuarios/<alias>/rides/<ride_id>/unloadParticipant', methods=['POST'])
def bajar_participante_ride(alias, ride_id):
    """Bajar un participante del ride"""
    usuario = data_handler.get_user(alias)
    if usuario:
        ride = data_handler.get_ride(ride_id)
        if ride:
            participant = data_handler.get_user(request.json['participant_alias'])
            if participant:
                ride.unload_participant(participant)
                return jsonify({"message": "Participante bajado del ride", "ride": ride.get_ride_info()}), 200
            return jsonify({"error": "Participante no encontrado"}), 404
        return jsonify({"error": "Ride no encontrado"}), 404
    return jsonify({"error": "Usuario no encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=True)
