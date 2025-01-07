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


def message_processor():
    """Function that continuously processes and prints messages from the queue"""
    while True:
        if not animation_queue.empty():
            animation = animation_queue.get()
            animation()
        else:
            default_animation()
        # time.sleep(1)  # Simulate a delay between messages

class RequestHandler(BaseHTTPRequestHandler):
    """Custom request handler for the HTTP server"""
    def do_GET(self):
        if self.path == '/led':
            animation_queue.put(blink_led_pwm)
            self.send_response(200)
            self.end_headers()
        else:
            # If the path is not recognized, respond with a 404
            self.send_response(404)
            self.end_headers()

def default_animation(duration=3):
    """simule tv effect avec bande led"""
    
    print("playing default animation...")

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(LED_RED, GPIO.OUT)
    GPIO.PWM(LED_RED, 0.1)

    GPIO.setup(LED_WHITE, GPIO.OUT)

    pwm_white = GPIO.PWM(LED_WHITE, 100)
    pwm_white.start(0)

    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            brightness = random.randint(50, 100)
            pwm_white.ChangeDutyCycle(brightness)
            time.sleep(random.uniform(0.8, 1.3))
    finally:
        print("stop default animation...")
        pwm_white.ChangeDutyCycle(0)
        pwm_white.stop()
        GPIO.cleanup()


def blink_led_pwm(duration=3):
    "clignotement de la bande led"
    
    print("playing blink_led_pwm...")

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(LED_WHITE, GPIO.OUT)
    GPIO.PWM(LED_WHITE, 0.1)

    GPIO.setup(LED_RED, GPIO.OUT)
    pwm_red = GPIO.PWM(LED_RED, 100)
    pwm_red.start(0)

    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            pwm_red.ChangeDutyCycle(100)
            time.sleep(0.5)
            pwm_red.ChangeDutyCycle(0)
            time.sleep(0.3)
    finally:
        print("stop blink_led_pwm...")
        pwm_red.ChangeDutyCycle(0)
        pwm_red.stop()
        GPIO.cleanup()



def start_server():
    """Start the HTTP server"""
    port = 8080
    
    print(f"Starting server on http://localhost:{port}")

    httpd = HTTPServer(("", port), RequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    threading.Thread(target=start_server).start()
    message_processor()
