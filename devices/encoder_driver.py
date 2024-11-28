from machine import Pin
import time

class EncoderDriver:
    def __init__(self, clk_pin, dt_pin, sw_pin=None):
        # Rotary Encoder pins
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP) if sw_pin is not None else None
        
        # Initialize state
        self.counter = 0
        self.clk_last_state = self.clk.value()
        self.last_button_state = True if self.sw else None
        self.button_pressed = False
        
        # Set up interrupts
        self.clk.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._rotation_handler)
        if self.sw:
            self.sw.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._button_handler)
    
    def _rotation_handler(self, pin):
        """Handle rotation interrupt"""
        clk_state = self.clk.value()
        if clk_state != self.clk_last_state:
            if self.dt.value() != clk_state:
                self.counter += 1
            else:
                self.counter -= 1
            self.clk_last_state = clk_state
    
    def _button_handler(self, pin):
        """Handle button press interrupt"""
        if self.sw:
            current_state = self.sw.value()
            if current_state == False and self.last_button_state == True:
                self.button_pressed = True
            self.last_button_state = current_state
    
    def get_counter(self):
        """Get current counter value"""
        return self.counter
    
    def reset_counter(self):
        """Reset counter to zero"""
        self.counter = 0
    
    def get_button_press(self):
        """Get and clear button press state"""
        if self.button_pressed:
            self.button_pressed = False
            return True
        return False 