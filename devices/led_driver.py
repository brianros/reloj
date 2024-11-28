from machine import Pin, PWM
import asyncio

class RGBLedDriver:
    def __init__(self, red_pin, green_pin, blue_pin):
        # Initialize RGB LED pins
        self.pwm_red = PWM(Pin(red_pin), freq=1000)
        self.pwm_green = PWM(Pin(green_pin), freq=1000)
        self.pwm_blue = PWM(Pin(blue_pin), freq=1000)
        
    def set_color(self, red, green, blue):
        self.pwm_red.duty_u16(red)
        self.pwm_green.duty_u16(green)
        self.pwm_blue.duty_u16(blue)
        
    async def smooth_transition(self, start_color, end_color, steps):
        for step in range(steps + 1):
            red = int(start_color[0] + (end_color[0] - start_color[0]) * step / steps)
            green = int(start_color[1] + (end_color[1] - start_color[1]) * step / steps)
            blue = int(start_color[2] + (end_color[2] - start_color[2]) * step / steps)
            self.set_color(red, green, blue)
            await asyncio.sleep_ms(100)
            
    def deinit(self):
        self.pwm_red.deinit()
        self.pwm_green.deinit()
        self.pwm_blue.deinit() 