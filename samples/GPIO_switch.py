#!/usr/bin/python3

import time
import RPi.GPIO as GPIO

# Configuration des broches GPIO
bouton_1_pin = 23
bouton_2_pin = 25
#LED_pin = 12

# Configuration de la numérotation BCM
GPIO.setmode(GPIO.BCM)

# Configuration de la broche du bouton en entrée et de la broche de la LED en sortie
GPIO.setup(bouton_1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bouton_2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(LED_pin, GPIO.OUT)

try:

    print("Started")

    while True:
        # Lecture de l'état du bouton
        etat_bouton_1 = GPIO.input(bouton_1_pin)
        etat_bouton_2 = GPIO.input(bouton_2_pin)

        # Allumer la LED si le bouton est enfoncé
        # if etat_bouton_1 == GPIO.LOW:
        #     GPIO.output(LED_pin, GPIO.HIGH)
        # else:
        #     GPIO.output(LED_pin, GPIO.LOW)

        if etat_bouton_1 == GPIO.LOW:
            print("bouton_1")

        if etat_bouton_2 == GPIO.LOW:
            print("bouton_2")

        # Petite pause pour éviter de saturer le processeur
        time.sleep(0.1)

except KeyboardInterrupt:
    # Réinitialisation des broches GPIO lorsqu'on interrompt le programme avec Ctrl+C
    GPIO.cleanup()