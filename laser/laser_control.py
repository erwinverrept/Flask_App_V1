# laser/laser_control.py
try:
    import RPi.GPIO as GPIO
    IS_RASPBERRY_PI = True
except ImportError:
    print("WAARSCHUWING: RPi.GPIO kon niet worden geïmporteerd. GPIO-functionaliteit is uitgeschakeld.")
    IS_RASPBERRY_PI = False

LASER_PIN = 24

def setup_gpio():
    """Zet de GPIO-pin voor de laser op."""
    if not IS_RASPBERRY_PI:
        return
    
    GPIO.setwarnings(False)
    # We gebruiken hier geen cleanup, omdat de turntable app de pinnen misschien ook gebruikt.
    # Als je alleen de laser gebruikt, is GPIO.cleanup() een goede optie.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LASER_PIN, GPIO.OUT)
    # Zorg ervoor dat de laser altijd 'uit' is bij het opstarten
    GPIO.output(LASER_PIN, GPIO.LOW)

def set_laser(state):
    """Zet de laser aan (True) of uit (False)."""
    if not IS_RASPBERRY_PI:
        status = "AAN" if state else "UIT"
        print(f"SIMULATIE: Laser is nu {status}")
        return

    if state:
        GPIO.output(LASER_PIN, GPIO.HIGH) # Zet de laser aan
    else:
        GPIO.output(LASER_PIN, GPIO.LOW) # Zet de laser uit

# Initialiseer de GPIO pin wanneer deze module wordt geladen
setup_gpio()
