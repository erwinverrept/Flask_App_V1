# turntable/motor_control.py
import time

try:
    import RPi.GPIO as GPIO
    IS_RASPBERRY_PI = True
except ImportError:
    print("WAARSCHUWING: RPi.GPIO kon niet worden geïmporteerd. GPIO-functionaliteit is uitgeschakeld.")
    IS_RASPBERRY_PI = False

# --- Motor Configuratie ---
CONTROL_PINS = [17, 18, 27, 22]
STEPS_PER_REVOLUTION = 2048 # Aantal stappen voor 360 graden. Pas eventueel aan.
JOG_STEPS = 25 # Aantal stappen voor de 'stapje' knoppen.

STEP_SEQUENCE = [
    [1, 0, 0, 1], [1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0],
    [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1]
]

# Houd de huidige positie bij in het geheugen. Reset bij herstart van de server.
current_angle = 0.0

def setup_gpio():
    """Zet de GPIO-pinnen op en ruim eventuele oude configuraties op."""
    if not IS_RASPBERRY_PI: return
    
    # Voorkom "channel is already in use" waarschuwingen
    GPIO.setwarnings(False)

    # Ruim vorige GPIO-instellingen op. Dit is nuttig bij het herstarten van de server.
    GPIO.cleanup() 
    
    GPIO.setmode(GPIO.BCM)
    for pin in CONTROL_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

def _perform_steps(steps, direction):
    """Interne functie om de motor te laten draaien."""
    if not IS_RASPBERRY_PI:
        print(f"SIMULATIE: Draai {steps} stappen naar {direction}")
        time.sleep(1) # Simuleer een draaitijd
        return

    sequence = STEP_SEQUENCE if direction == 'right' else STEP_SEQUENCE[::-1]
    
    for _ in range(steps):
        for step in sequence:
            for pin_index, pin_value in enumerate(step):
                GPIO.output(CONTROL_PINS[pin_index], pin_value)
            time.sleep(0.002)

    # Schakel pinnen uit na de beweging
    for pin in CONTROL_PINS:
        GPIO.output(pin, 0)

def move_by_degrees(degrees, direction):
    """Beweeg de motor een specifiek aantal graden."""
    global current_angle
    degrees = float(degrees)
    
    steps_to_move = int(degrees / 360.0 * STEPS_PER_REVOLUTION)
    
    _perform_steps(steps_to_move, direction)

    # Update de hoek
    if direction == 'left':
        current_angle -= degrees
    else:
        current_angle += degrees
    
    current_angle %= 360 # Normaliseer naar 0-360
    return current_angle

def jog_motor(direction):
    """Beweeg de motor een klein, vast aantal stappen voor fijnafstelling."""
    global current_angle
    
    _perform_steps(JOG_STEPS, direction)

    angle_change = (JOG_STEPS / STEPS_PER_REVOLUTION) * 360.0
    if direction == 'left':
        current_angle -= angle_change
    else:
        current_angle += angle_change

    current_angle %= 360
    return current_angle

# Initialiseer GPIO
setup_gpio()
