from machine import Pin, PWM
import asyncio

class BuzzerDriver:
    def __init__(self, pin_number):
        self.buzzer_pin = Pin(pin_number)
        self.pwm = PWM(self.buzzer_pin, freq=440)  # Default to A4 note
        self.pwm.duty_u16(0)  # Start silent
        
    async def play_tone(self, frequency, duration_ms=100, duty=32768):
        """Play a tone at specified frequency for duration_ms milliseconds"""
        self.pwm.freq(frequency)
        self.pwm.duty_u16(duty)  # 50% duty cycle
        await asyncio.sleep_ms(duration_ms)
        self.pwm.duty_u16(0)
        
    async def play_melody(self, notes):
        """
        Play a sequence of notes
        notes: list of tuples (frequency, duration_ms)
        """
        for freq, duration in notes:
            await self.play_tone(freq, duration)
            await asyncio.sleep_ms(50)  # Small gap between notes
            
    def stop(self):
        """Stop playing sound"""
        self.pwm.duty_u16(0)
        
    def deinit(self):
        self.pwm.deinit() 