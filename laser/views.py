from flask import Blueprint, render_template, request, jsonify
from . import laser_control

laser_bp = Blueprint('laser', __name__,
                        template_folder='templates')

@laser_bp.route('/laser')
def laser_view():
    return render_template('laser/laser.html')

@laser_bp.route('/laser/api/set_state', methods=['POST'])
def set_laser_state_view():
    data = request.get_json()
    state = data.get('state', False)
    laser_control.set_laser(state)
    status_text = "aan" if state else "uit"
    return jsonify({'status': 'success', 'message': f'Laser is nu {status_text}'})
