from flask import Flask, request, jsonify
import os
from port import PortManager
from planner import Planner

app = Flask(__name__)

# 初始化 Planner
location = os.path.realpath(os.path.join(
    os.getcwd(), os.path.dirname(__file__)))

port_file = os.path.join(location, "ports.csv")
manager = PortManager(port_file)

map_file = os.path.join(location, "raw-data/map.tif")
planner = Planner(map_file)


@app.route('/get_port_info', methods=['GET'])
def get_port_info():
    '''
    Get port information by port code. Example:
    - curl "http://127.0.0.1:5000/get_port_info?code=HKGOM"
    '''
    code = request.args.get('code')
    port = manager.find_port_by_code(code)
    if not port:
        return jsonify({'error': 'Invalid port code / Port Code not found'}), 400

    port_info = {
        'code': port.code,
        'name': port.name,
        'name_wo_diacritics': port.name_wo_diacritics,
        'function': port.function,
        'longitude': port.coordinates[1],
        'latitude': port.coordinates[0]
    }
    return jsonify(port_info)


def validate_coordinates(coordinates):
    try:
        lat = float(coordinates[0])
        lon = float(coordinates[1])
    except ValueError:
        return False, "Coordinates must be numbers."
    if not (-90 <= lat <= 90):
        return False, "Latitude must be between -90 and 90."
    if not (-180 <= lon <= 180):
        return False, "Longitude must be between -180 and 180."
    return True, ""


@app.route('/calculate_distance', methods=['POST'])
def calculate_distance():
    '''
    Calculate the distance between two ports or coordinates. Examples:
    - curl -X POST http://127.0.0.1:5000/calculate_distance \
        -H "Content-Type: application/json" \
        -d '{
            "from_code": "HKGOM",
            "to_code": "USZJI"
            }'
    - curl -X POST http://127.0.0.1:5000/calculate_distance \
        -H "Content-Type: application/json" \
        -d '{
            "from_longitude": 114.18333333333334,
            "from_latitude": 22.3,
            "to_longitude": -118.1,
            "to_latitude": 34.53333333333333
            }'
    '''
    data = request.json

    if 'from_code' in data and 'to_code' in data:
        port_from = manager.find_port_by_code(data['from_code'])
        port_to = manager.find_port_by_code(data['to_code'])
        if not port_from or not port_to:
            return jsonify({'error': 'Invalid port code / Port Code not found'}), 400
        distance = planner.cal_distance(port_from, port_to)

    elif all(k in data for k in ('from_longitude', 'from_latitude', 'to_longitude', 'to_latitude')):
        from_coor = (data['from_latitude'], data['from_longitude'])
        to_coor = (data['to_latitude'], data['to_longitude'])

        valid_from, error_from = validate_coordinates(from_coor)
        valid_to, error_to = validate_coordinates(to_coor)

        if not valid_from:
            return jsonify({'error': error_from}), 400
        if not valid_to:
            return jsonify({'error': error_to}), 400

        distance = planner.cal_distance_by_coordinates(from_coor, to_coor)

    else:
        return jsonify({'error': 'Invalid input'}), 400

    return jsonify({'distance_km': distance})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
