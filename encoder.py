# rotary_rgb_control.py

from machine import Pin, PWM
import time
import asyncio
import json

# Pin definitions
clk_pin = Pin(10, Pin.IN)
dt_pin = Pin(11, Pin.IN)
sw_pin = Pin(12, Pin.IN, Pin.PULL_UP)
red_pin = PWM(Pin(2))
green_pin = PWM(Pin(3))
blue_pin = PWM(Pin(4))
buzzer = PWM(Pin(1))
buzzer.freq(440)  # Default frequency (A4 note)
buzzer.duty_u16(0)  # Start silent

# Initialize PWM frequencies
red_pin.freq(1000)
green_pin.freq(1000)
blue_pin.freq(1000)

# Set initial duty cycle to 0
red_pin.duty_u16(0)
green_pin.duty_u16(0)
blue_pin.duty_u16(0)

print("PWM pins initialized")

# Initialize variables
color_index = 0
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
current_color = list(colors[0])  # Track current color as a list for gradual changes
target_color = list(colors[0])   # Track target color
intensity = 255
led_on = True
mode = 'color'  # 'color' or 'dim'

# Add these variables after other initializations
last_clk_state = clk_pin.value()  # Store last state of CLK pin
last_switch_state = sw_pin.value()  # Store last state of switch
button_press_start = 0  # To track long press
button_debounce_time = 0  # For debouncing
LONG_PRESS_TIME = 1000  # 1 second in milliseconds
DEBOUNCE_DELAY = 50  # 50ms debounce delay

# Update constants
STEPS_PER_COLOR = 4     # Fewer steps for quicker color changes
STEPS_PER_DIM = 20      # Keep dimming steps the same
TRANSITION_STEPS = 10   # Faster transitions

# Add these variables to track partial progress
current_progress = 0.0  # Track progress between colors (0.0 to 1.0)

# Add these variables to initialization
last_clk_state = clk_pin.value()
last_dt_state = dt_pin.value()

# Add these constants
ENCODER_CW = 1    # Clockwise rotation
ENCODER_CCW = -1  # Counter-clockwise rotation

# Add these variables
encoder_value = 0      # Generic encoder position
encoder_min = 0        # Minimum encoder value
encoder_max = 100      # Maximum encoder value
encoder_step = 5       # Step size for each encoder tick

# Add these constants for tunes
NOTE_C5 = 523
NOTE_E5 = 659
NOTE_G5 = 784
NOTE_C6 = 1047

# Helper functions for sound
async def beep(frequency=440, duration_ms=50):
    """Make a short beep"""
    buzzer.freq(frequency)
    buzzer.duty_u16(32768)  # 50% duty cycle
    await asyncio.sleep_ms(duration_ms)
    buzzer.duty_u16(0)

async def play_power_on():
    """Play power on tune (ascending)"""
    for note in [NOTE_C5, NOTE_E5, NOTE_G5]:
        buzzer.freq(note)
        buzzer.duty_u16(32768)
        await asyncio.sleep_ms(50)
        buzzer.duty_u16(0)
        await asyncio.sleep_ms(20)
    
async def play_power_off():
    """Play power off tune (descending)"""
    for note in [NOTE_G5, NOTE_E5, NOTE_C5]:
        buzzer.freq(note)
        buzzer.duty_u16(32768)
        await asyncio.sleep_ms(50)
        buzzer.duty_u16(0)
        await asyncio.sleep_ms(20)

# Function for smooth color transition between two colors
def interpolate_color(start_color, end_color, fraction):
    return [int(start_color[i] + (end_color[i] - start_color[i]) * fraction) for i in range(3)]

# Function to set RGB LED color and intensity
def set_color(r, g, b, override_intensity=None):
    i = override_intensity if override_intensity is not None else intensity
    r_duty = int(r * i / 255)
    g_duty = int(g * i / 255)
    b_duty = int(b * i / 255)
    
    # Convert to 16-bit values (0-65535)
    r_duty_16 = min(65535, r_duty * 256)
    g_duty_16 = min(65535, g_duty * 256)
    b_duty_16 = min(65535, b_duty * 256)
    
    red_pin.duty_u16(r_duty_16)
    green_pin.duty_u16(g_duty_16)
    blue_pin.duty_u16(b_duty_16)

# Function to handle encoder value changes
async def on_encoder_change(direction):
    """Handle encoder rotation events"""
    global encoder_value, color_index, intensity, current_progress, current_color
    
    if not led_on:
        return
    
    # Now we can await the beep
    await beep(440 if direction == ENCODER_CW else 392)
    
    if mode == 'color':
        # Calculate progress step
        step = 1.0 / STEPS_PER_COLOR
        current_progress += (step * direction)
        
        if direction == ENCODER_CW:
            # Get current and next colors for interpolation
            current_color = colors[color_index]
            next_index = (color_index + 1) % len(colors)
            next_color = colors[next_index]
            
            # Interpolate between colors based on progress
            intermediate_color = interpolate_color(current_color, next_color, current_progress)
            set_color(*intermediate_color)
            print(f"CW - Color progress: {current_progress:.2f}")
            
            # If we've completed a full step, update the color index
            if current_progress >= 1.0:
                color_index = next_index
                current_progress = 0.0
                print(f"CW - Color changed to index: {color_index}")
                
        else:  # Counter-clockwise
            # Get current and previous colors for interpolation
            current_color = colors[color_index]
            prev_index = (color_index - 1) % len(colors)
            prev_color = colors[prev_index]
            
            # Interpolate between colors based on progress
            intermediate_color = interpolate_color(current_color, prev_color, abs(current_progress))
            set_color(*intermediate_color)
            print(f"CCW - Color progress: {current_progress:.2f}")
            
            # If we've completed a full step backwards, update the color index
            if current_progress <= -1.0:
                color_index = prev_index
                current_progress = 0.0
                print(f"CCW - Color changed to index: {color_index}")
            
    elif mode == 'dim':
        step = 255 // STEPS_PER_DIM
        if direction == ENCODER_CW:
            intensity = min(255, intensity + step)
            print(f"CW - Intensity increased to: {intensity}")
        else:
            intensity = max(0, intensity - step)
            print(f"CCW - Intensity decreased to: {intensity}")
        set_color(*colors[color_index])

# Modify the main control functions to be async
async def rotary_encoder():
    global last_clk_state, last_dt_state
    
    while True:
        clk_state = clk_pin.value()
        dt_state = dt_pin.value()
        
        if clk_state != last_clk_state:  # CLK has changed
            if clk_state == 0:  # CLK has gone from 1 to 0
                if last_dt_state == 1 and dt_state == 1:  # Counter-clockwise
                    await on_encoder_change(ENCODER_CCW)
                elif last_dt_state == 0 and dt_state == 0:  # Clockwise
                    await on_encoder_change(ENCODER_CW)
        
        # Store states for next iteration
        last_clk_state = clk_state
        last_dt_state = dt_state
        
        await asyncio.sleep_ms(1)  # Small delay for debouncing

# Add these functions for state management
def save_state():
    """Save current state to file"""
    state = {
        'mode': mode,
        'color_index': color_index,
        'intensity': intensity,
        'led_on': led_on
    }
    try:
        with open('led_state.json', 'w') as f:
            json.dump(state, f)
    except:
        print("Could not save state")

def load_state():
    """Load saved state from file"""
    global mode, color_index, intensity, led_on
    try:
        with open('led_state.json', 'r') as f:
            state = json.load(f)
            mode = state.get('mode', 'color')
            color_index = state.get('color_index', 0)
            intensity = state.get('intensity', 255)
            led_on = state.get('led_on', True)
    except:
        print("No saved state found, using defaults")
        # Default values are already set in initialization

# Update the switch_press function to save state on mode changes
async def switch_press():
    global led_on, mode, intensity, last_switch_state, button_press_start, button_debounce_time
    
    while True:
        current_time = time.ticks_ms()
        switch_state = sw_pin.value()
        
        if (switch_state != last_switch_state and 
            time.ticks_diff(current_time, button_debounce_time) >= DEBOUNCE_DELAY):
            
            button_debounce_time = current_time
            
            if switch_state == 0:  # Button pressed
                button_press_start = current_time
                print("Button press started")
                await beep(NOTE_C5, 50)
            
            elif switch_state == 1:  # Button released
                press_duration = time.ticks_diff(current_time, button_press_start)
                print(f"Press duration: {press_duration}ms")
                
                if press_duration >= LONG_PRESS_TIME:
                    led_on = False
                    print("Long press detected - LED turned OFF")
                    set_color(0, 0, 0)
                    await play_power_off()
                    save_state()  # Save state when turning off
                else:
                    if not led_on:
                        led_on = True
                        print("LED turned ON")
                        set_color(*colors[color_index])
                        await play_power_on()
                        save_state()  # Save state when turning on
                    else:
                        if mode == 'color':
                            mode = 'dim'
                            print("Switched to DIM mode")
                            await beep(NOTE_E5, 100)
                        else:
                            mode = 'color'
                            print("Switched to COLOR mode")
                            await beep(NOTE_G5, 100)
                        save_state()  # Save state when changing modes
            
            last_switch_state = switch_state
        
        await asyncio.sleep_ms(10)

async def color_transition(start_color, end_color, duration_ms=500):
    """Smooth color transition with async"""
    start_time = time.ticks_ms()
    while True:
        current_time = time.ticks_ms()
        elapsed = time.ticks_diff(current_time, start_time)
        if elapsed >= duration_ms:
            set_color(*end_color)
            break
            
        fraction = elapsed / duration_ms
        intermediate_color = interpolate_color(start_color, end_color, fraction)
        set_color(*intermediate_color)
        await asyncio.sleep_ms(10)

# Update the main function to load state at startup
async def main():
    print("Loading saved state...")
    load_state()
    print(f"Initial state - Mode: {mode}, LED On: {led_on}, Color Index: {color_index}, Intensity: {intensity}")
    
    if led_on:
        set_color(*colors[color_index])
    else:
        set_color(0, 0, 0)
    
    # Create tasks for encoder and button handling
    encoder_task = asyncio.create_task(rotary_encoder())
    button_task = asyncio.create_task(switch_press())
    
    # Wait for both tasks indefinitely
    await asyncio.gather(encoder_task, button_task)

# Start the async event loop
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program terminated by user")
finally:
    # Clean up
    set_color(0, 0, 0)