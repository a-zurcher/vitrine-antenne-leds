from multiprocessing import Process
from signal import signal, SIGTERM

import RPi.GPIO as GPIO
import time
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from queue import Queue


# Initialize the queue to store messages
animation_queue = Queue()

LED_WHITE = 12
LED_RED = 18
GPIO.setup(LED_WHITE, GPIO.OUT)
GPIO.setup(LED_RED, GPIO.OUT)
currently_running_animation_process: Process = Process()

def reset_animation():
    """Function that continuously processes and prints messages from the queue"""
    global currently_running_animation_process

    currently_running_animation_process = Process(target=default_animation)
    currently_running_animation_process.start()

class RequestHandler(BaseHTTPRequestHandler):
    """Custom request handler for the HTTP server"""

    def do_GET(self):
        if self.path == '/led':
            global currently_running_animation_process
            currently_running_animation_process.terminate()
            currently_running_animation_process = Process(target=blink_led_pwm)
            currently_running_animation_process.start()

            self.send_response(200)
            self.end_headers()
        else:
            # If the path is not recognized, respond with a 404
            self.send_response(404)
            self.end_headers()

def default_animation():
    """simule tv effect avec bande led"""
    def terminate(*args):
        print("stopping default animation...")
        pwm_white.ChangeDutyCycle(0)
        pwm_white.stop()
        GPIO.cleanup()

    print("playing default animation...")

    signal(SIGTERM, terminate)

    GPIO.setmode(GPIO.BCM)

    pwm_white = GPIO.PWM(LED_WHITE, 100)
    pwm_white.start(0)

    while True:
        brightness = random.randint(50, 100)
        pwm_white.ChangeDutyCycle(brightness)
        time.sleep(random.uniform(0.2, 1.3))


def blink_led_pwm(duration=3):
    """clignotement de la bande led"""

    def terminate(*args):
        print("stopping default animation...")
        pwm_red.ChangeDutyCycle(0)
        pwm_red.stop()
        GPIO.cleanup()

        reset_animation()

    signal(SIGTERM, terminate)
    
    print("playing blink_led_pwm...")

    GPIO.setmode(GPIO.BCM)
    pwm_red = GPIO.PWM(LED_RED, 100)
    pwm_red.start(0)

    start_time = time.time()

    while time.time() - start_time < duration:
        pwm_red.ChangeDutyCycle(100)
        time.sleep(0.5)
        pwm_red.ChangeDutyCycle(0)
        time.sleep(0.3)

    print("stop blink_led_pwm...")
    pwm_red.ChangeDutyCycle(0)
    pwm_red.stop()

    reset_animation()



def start_server():
    """Start the HTTP server"""
    port = 8080
    
    print(f"Starting server on http://localhost:{port}")

    httpd = HTTPServer(("", port), RequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    reset_animation()
    threading.Thread(target=start_server).start()
