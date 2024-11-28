from machine import Pin, PWM
import asyncio

class ServoDriver:
    def __init__(self, pin_number):
        self.servo_pin = Pin(pin_number)
        self.pwm = PWM(self.servo_pin, freq=50)  # 50 Hz frequency for servo
        
    async def set_pulse_width(self, pulse_width_ms):
        # Convert pulse width in ms to duty cycle for 16-bit
        duty = int((pulse_width_ms / 20) * 65535)  # 20 ms period for 50 Hz
        self.pwm.duty_u16(duty)
        await asyncio.sleep_ms(1)  # Small delay for stability
        
    def deinit(self):
        self.pwm.deinit() 