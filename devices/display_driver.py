from .servo_driver import ServoDriver
import asyncio

class ServoDisplay:
    def __init__(self, servo_pins):
        if len(servo_pins) != 4:
            raise ValueError("ServoDisplay requires exactly 4 servo pins")
        
        self.servos = [ServoDriver(pin) for pin in servo_pins]
        
    async def set_all_positions(self, position):
        # Create tasks for all servos to move simultaneously
        await asyncio.gather(
            *[servo.set_pulse_width(position) for servo in self.servos]
        )
            
    async def sweep_all(self, start_pos, end_pos, step=0.1):
        current_pos = start_pos
        while current_pos <= end_pos:
            await self.set_all_positions(current_pos)
            current_pos += step
            await asyncio.sleep_ms(50)
            
    async def set_individual_positions(self, positions):
        if len(positions) != 4:
            raise ValueError("Must provide 4 positions")
        await asyncio.gather(
            *[servo.set_pulse_width(pos) for servo, pos in zip(self.servos, positions)]
        )
            
    def deinit(self):
        for servo in self.servos:
            servo.deinit() 