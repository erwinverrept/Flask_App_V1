from flask import Blueprint, render_template, request, jsonify
from . import motor_control

turntable_bp = Blueprint('turntable', __name__,
                            template_folder='templates')

@turntable_bp.route('/turntable')
def turntable_view():
    return render_template('turntable/turntable.html', degrees=range(360))

@turntable_bp.route('/api/turn_by_degrees', methods=['POST'])
def turn_by_degrees_view():
    data = request.get_json()
    direction = data.get('direction')
    degrees = data.get('degrees')

    if direction in ['left', 'right'] and degrees is not None:
        new_angle = motor_control.move_by_degrees(degrees, direction)
        return jsonify({'status': 'success', 'new_angle': new_angle})
    
    return jsonify({'status': 'error'}), 400

@turntable_bp.route('/api/jog', methods=['POST'])
def jog_view():
    data = request.get_json()
    direction = data.get('direction')
    
    if direction in ['left', 'right']:
        new_angle = motor_control.jog_motor(direction)
        return jsonify({'status': 'success', 'new_angle': new_angle})
        
    return jsonify({'status': 'error'}), 400
