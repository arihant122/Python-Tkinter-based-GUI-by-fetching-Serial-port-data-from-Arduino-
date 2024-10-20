import tkinter as tk
import serial
import threading
import time

# Set up serial connection
serial_port = 'COM5'  # Update with your serial port
baud_rate = 9600       # Update with your baud rate
ser = serial.Serial(serial_port, baud_rate)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Data Reader")

        # Create labels and entry boxes for the first four values
        self.labels = []
        self.entries = []
        for i in range(4):
            label = tk.Label(root, text=f"Val{i+1}", font=("Helvetica", 24))
            label.grid(row=i, column=0, padx=10, pady=10)
            entry = tk.Entry(root, font=("Helvetica", 24), width=10, justify='center')
            entry.grid(row=i, column=1, padx=10, pady=10)
            entry.config(state='readonly')  # Make entry read-only
            self.labels.append(label)
            self.entries.append(entry)

        # Create LED indicator
        self.led = tk.Canvas(root, width=50, height=50, bg='white', highlightthickness=0)
        self.led.grid(row=4, column=0, columnspan=2, pady=10)
        self.led.create_oval(5, 5, 45, 45, fill='green', outline='black', width=2)

        # Start the serial reading thread
        self.running = True
        threading.Thread(target=self.read_serial_data, daemon=True).start()
        
        # Update LED state
        self.update_led()

    def read_serial_data(self):
        while self.running:
            if ser.in_waiting:
                data = ser.readline().decode('utf-8').strip()
                values = data.split(',')
                if len(values) >= 5:
                    for i in range(4):
                        self.entries[i].config(state='normal')
                        self.entries[i].delete(0, tk.END)
                        self.entries[i].insert(0, values[i])
                        self.entries[i].config(state='readonly')
                    self.last_value = int(values[4])  # Assume last value is at index 4
            time.sleep(0.1)

    def update_led(self):
        if hasattr(self, 'last_value'):
            color = 'red' if self.last_value == 1 else 'green'
            self.led.itemconfig(1, fill=color)
            self.led.after(500, self.blink_led if color == 'red' else self.keep_green)

    def blink_led(self):
        current_color = self.led.itemcget(1, 'fill')
        new_color = 'green' if current_color == 'red' else 'red'
        self.led.itemconfig(1, fill=new_color)
        self.led.after(500, self.update_led)

    def keep_green(self):
        self.led.itemconfig(1, fill='green')
        self.led.after(500, self.update_led)

    def on_close(self):
        self.running = False
        ser.close()
        self.root.destroy()

# Create the main window
root = tk.Tk()
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
root.mainloop()
