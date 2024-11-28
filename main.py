import asyncio
from devices.servo_driver import ServoDriver
from devices.led_driver import RGBLedDriver
from devices.display_driver import ServoDisplay
from devices.buzzer_driver import BuzzerDriver
from devices.encoder_driver import EncoderDriver

# Pin definitions
SERVO_PINS = [15, 14, 13, 12]  # Four servo pins
LED_PINS = {
    'red': 2,
    'green': 3,
    'blue': 4
}
BUZZER_PIN = 5
ENCODER_PINS = {
    'clk': 6,
    'dt': 7,
    'sw': 8
}

async def handle_encoder(encoder, display, buzzer, led):
    last_count = encoder.get_counter()
    while True:
        # Check encoder for position changes
        current_count = encoder.get_counter()
        if current_count != last_count:
            # Use encoder position to control servo position
            position = 1 + (current_count % 10) / 10  # Maps to 1.0-2.0 ms
            await display.set_all_positions(position)
            last_count = current_count
        
        # Check for button press
        if encoder.get_button_press():
            # Create tasks for concurrent operations
            await asyncio.gather(
                buzzer.play_tone(440, 100),  # Play A4 note
                led.smooth_transition((65535, 0, 0), (0, 65535, 0), 10)
            )
        
        await asyncio.sleep_ms(10)  # Small delay to prevent busy waiting

async def main():
    try:
        # Initialize devices
        display = ServoDisplay(SERVO_PINS)
        led = RGBLedDriver(LED_PINS['red'], LED_PINS['green'], LED_PINS['blue'])
        buzzer = BuzzerDriver(BUZZER_PIN)
        encoder = EncoderDriver(
            ENCODER_PINS['clk'],
            ENCODER_PINS['dt'],
            ENCODER_PINS['sw']
        )
        
        # Create and run tasks
        await handle_encoder(encoder, display, buzzer, led)
            
    except KeyboardInterrupt:
        # Clean shutdown
        display.deinit()
        led.deinit()
        buzzer.deinit()

if __name__ == '__main__':
    asyncio.run(main()) 