import RPi.GPIO as GPIO
import time

# Set up GPIO pins
SPINNER_PIN_A = 17  # Example pin numbers, adjust as needed
SPINNER_PIN_B = 27  # Example pin numbers, adjust as needed

# Variables to keep track of spinner state
spinner_state = 0
last_spinner_state = 0

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SPINNER_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SPINNER_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Callback function for spinner rotation
def spinner_callback(channel):
    global spinner_state, last_spinner_state

    # Read the state of both pins
    pin_a_state = GPIO.input(SPINNER_PIN_A)
    pin_b_state = GPIO.input(SPINNER_PIN_B)

    # Combine the two pin states into one variable
    new_spinner_state = (pin_a_state << 1) | pin_b_state

    # Calculate direction of rotation
    if new_spinner_state != spinner_state:
        if (last_spinner_state == 0 and new_spinner_state == 1) or \
           (last_spinner_state == 2 and new_spinner_state == 3) or \
           (last_spinner_state == 3 and new_spinner_state == 0) or \
           (last_spinner_state == 1 and new_spinner_state == 2):
            print("Clockwise")
        else:
            print("Counterclockwise")

    last_spinner_state = spinner_state
    spinner_state = new_spinner_state

# Main function
def main():
    try:
        setup_gpio()

        # Add event detection for spinner rotation
        GPIO.add_event_detect(SPINNER_PIN_A, GPIO.BOTH, callback=spinner_callback, bouncetime=5)

        print("Ready to detect spinner rotation")

        # Keep the program running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()

# Run the main function
if __name__ == "__main__":
    main()