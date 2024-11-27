from machine import Pin, PWM
import time

# Set up the PWM pins for servos
servo_pin_1 = Pin(15)  # First servo pin
servo_pin_2 = Pin(14)  # Second servo pin
pwm_1 = PWM(servo_pin_1, freq=50)  # 50 Hz frequency for first servo
pwm_2 = PWM(servo_pin_2, freq=50)  # 50 Hz frequency for second servo

# Set up the PWM pins for RGB LED
red_pin = Pin(2)  # Red pin
green_pin = Pin(3)  # Green pin
blue_pin = Pin(4)  # Blue pin
pwm_red = PWM(red_pin, freq=1000)  # 1 kHz frequency for red
pwm_green = PWM(green_pin, freq=1000)  # 1 kHz frequency for green
pwm_blue = PWM(blue_pin, freq=1000)  # 1 kHz frequency for blue

def set_servo_pulse_width(pwm, pulse_width_ms):
    # Convert pulse width in ms to duty cycle for 16-bit
    duty = int((pulse_width_ms / 20) * 65535)  # 20 ms period for 50 Hz
    pwm.duty_u16(duty)

def set_rgb_color(red, green, blue):
    # Set RGB LED color
    pwm_red.duty_u16(red)
    pwm_green.duty_u16(green)
    pwm_blue.duty_u16(blue)

def smooth_transition(start_color, end_color, steps):
    # Smoothly transition between two colors
    for step in range(steps + 1):
        red = int(start_color[0] + (end_color[0] - start_color[0]) * step / steps)
        green = int(start_color[1] + (end_color[1] - start_color[1]) * step / steps)
        blue = int(start_color[2] + (end_color[2] - start_color[2]) * step / steps)
        set_rgb_color(red, green, blue)
        time.sleep(0.1)  # Adjust for speed of transition

try:
    while True:
        # Sweep from 1 ms to 2 ms for servos and transition colors
        for position in range(1, 3):  # Sweep from 1 ms to 2 ms
            set_servo_pulse_width(pwm_1, position)  # Move first servo
            set_servo_pulse_width(pwm_2, position)  # Move second servo
            
            # Define start and end colors based on position
            if position == 1:
                start_color = (65535, 0, 0)  # Full red
                end_color = (0, 65535, 0)    # Full green
            else:
                start_color = (0, 65535, 0)  # Full green
                end_color = (0, 0, 65535)     # Full blue
            
            smooth_transition(start_color, end_color, 10)  # Smooth transition in 10 steps
            time.sleep(1)  # Wait for 1 second

        # Sweep back from 2 ms to 1 ms for servos and transition colors
        for position in range(2, 0, -1):  # Sweep from 2 ms to 1 ms
            set_servo_pulse_width(pwm_1, position)  # Move first servo
            set_servo_pulse_width(pwm_2, position)  # Move second servo
            
            # Define start and end colors based on position
            if position == 2:
                start_color = (0, 65535, 0)  # Full green
                end_color = (0, 0, 65535)     # Full blue
            else:
                start_color = (0, 0, 65535)     # Full blue
                end_color = (65535, 0, 0)      # Full red
            
            smooth_transition(start_color, end_color, 10)  # Smooth transition in 10 steps
            time.sleep(1)  # Wait for 1 second

except KeyboardInterrupt:
    pwm_1.deinit()  # Stop PWM for first servo on exit
    pwm_2.deinit()  # Stop PWM for second servo on exit
    pwm_red.deinit()  # Stop PWM for red LED on exit
    pwm_green.deinit()  # Stop PWM for green LED on exit
    pwm_blue.deinit()  # Stop PWM for blue LED on exit
