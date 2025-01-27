import tkinter as tk
import math
import time
import threading

class AlphaBot2Simulator:
    def __init__(self, root):
        self.root = root
        self.root.title("AlphaBot2 Simulator")
        
        # Simulation parameters
        self.width = 600
        self.height = 400
        self.robot_size = 30
        self.speed = 3  # pixels per update
        self.turn_speed = 5  # degrees per update
        
        # Initial state
        self.x = self.width // 2
        self.y = self.height // 2
        self.heading = 0  # degrees
        self.moving = False
        self.current_action = None
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.pack()
        
        # Create robot representation
        self.robot = self.draw_robot()
        
        # Movement bindings (optional)
        self.root.bind('<KeyPress>', self.key_press)
        self.root.bind('<KeyRelease>', self.key_release)
        
    def draw_robot(self):
        angle = math.radians(self.heading)
        x0 = self.x - self.robot_size/2
        y0 = self.y - self.robot_size/2
        x1 = self.x + self.robot_size/2
        y1 = self.y + self.robot_size/2
        
        return self.canvas.create_polygon(
            [
                self.x + math.cos(angle) * self.robot_size/2,
                self.y + math.sin(angle) * self.robot_size/2,
                self.x + math.cos(angle + 2*math.pi/3) * self.robot_size/2,
                self.y + math.sin(angle + 2*math.pi/3) * self.robot_size/2,
                self.x + math.cos(angle - 2*math.pi/3) * self.robot_size/2,
                self.y + math.sin(angle - 2*math.pi/3) * self.robot_size/2,
            ],
            fill='blue', outline='black'
        )
    
    def update_robot(self):
        self.canvas.delete(self.robot)
        self.robot = self.draw_robot()
        
    def forward(self):
        self.moving = True
        while self.moving and self.current_action == 'forward':
            dx = math.cos(math.radians(self.heading)) * self.speed
            dy = math.sin(math.radians(self.heading)) * self.speed
            self.x = (self.x + dx) % self.width
            self.y = (self.y + dy) % self.height
            self.update_robot()
            time.sleep(0.05)
            
    def backward(self):
        self.moving = True
        while self.moving and self.current_action == 'backward':
            dx = math.cos(math.radians(self.heading)) * self.speed
            dy = math.sin(math.radians(self.heading)) * self.speed
            self.x = (self.x - dx) % self.width
            self.y = (self.y - dy) % self.height
            self.update_robot()
            time.sleep(0.05)
            
    def turn_left(self):
        self.moving = True
        while self.moving and self.current_action == 'left':
            self.heading = (self.heading + self.turn_speed) % 360
            self.update_robot()
            time.sleep(0.05)
            
    def turn_right(self):
        self.moving = True
        while self.moving and self.current_action == 'right':
            self.heading = (self.heading - self.turn_speed) % 360
            self.update_robot()
            time.sleep(0.05)
            
    def stop(self):
        self.moving = False
        self.current_action = None
        
    def key_press(self, event):
        if event.keysym == 'Up':
            self.current_action = 'forward'
            threading.Thread(target=self.forward).start()
        elif event.keysym == 'Down':
            self.current_action = 'backward'
            threading.Thread(target=self.backward).start()
        elif event.keysym == 'Right':
            self.current_action = 'left'
            threading.Thread(target=self.turn_left).start()
        elif event.keysym == 'Left':
            self.current_action = 'right'
            threading.Thread(target=self.turn_right).start()
            
    def key_release(self, event):
        self.stop()

# Modified GPIO simulator
class GPIOSimulator:
    def __init__(self, simulator):
        self.simulator = simulator
        self.pins = {
            12: False,  # IN1
            13: False,  # IN2
            20: False,  # IN3
            21: False,  # IN4
        }
        
    def output(self, pin, state):
        if pin in self.pins:
            self.pins[pin] = state
            self.update_movement()
            
    def update_movement(self):
        # Map physical motor controls to simulator movements
        in1, in2, in3, in4 = [self.pins[p] for p in [12, 13, 20, 21]]
        
        if in1 and not in2 and in3 and not in4:
            self.simulator.current_action = 'forward'
            threading.Thread(target=self.simulator.forward).start()
        elif not in1 and in2 and not in3 and in4:
            self.simulator.current_action = 'backward'
            threading.Thread(target=self.simulator.backward).start()
        elif not in1 and in2 and in3 and not in4:
            self.simulator.current_action = 'left'
            threading.Thread(target=self.simulator.turn_left).start()
        elif in1 and not in2 and not in3 and in4:
            self.simulator.current_action = 'right'
            threading.Thread(target=self.simulator.turn_right).start()
        else:
            self.simulator.stop()

# To use with your original code:
if __name__ == "__main__":
    root = tk.Tk()
    simulator = AlphaBot2Simulator(root)
    gpio_simulator = GPIOSimulator(simulator)
    
    # Replace RPi.GPIO with this simulator in your code
    GPIO = gpio_simulator
    
    # Example usage (same structure as physical code)
    def run_demo():
        while True:
            
            # GPIO.output(12, True)
            # GPIO.output(13, False)
            # GPIO.output(20, True)
            # GPIO.output(21, False)
            # time.sleep(2)
            
            # GPIO.output(12, False)
            # GPIO.output(13, True)
            # GPIO.output(20, True)
            # GPIO.output(21, False)
            time.sleep(1)
            
            # GPIO.output(12, True)
            # GPIO.output(13, False)
            # GPIO.output(20, False)
            # GPIO.output(21, True)
            # time.sleep(1)
            
            # GPIO.output(12, False)
            # GPIO.output(13, True)
            # GPIO.output(20, False)
            # GPIO.output(21, True)
            # time.sleep(2)
            
            # GPIO.output(12, False)
            # GPIO.output(13, False)
            # GPIO.output(20, False)
            # GPIO.output(21, False)
            # time.sleep(1)
    
    threading.Thread(target=run_demo, daemon=True).start()
    root.mainloop()