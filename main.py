import sys
import clr
import tkinter as tk
import psutil
import GPUtil
from time import sleep
from threading import Thread
from tqdm import tqdm

clr.AddReference('OpenHardwareMonitorLib')
from OpenHardwareMonitor import Hardware

class HardwareMonitor:
    def __init__(self):
        self.computer = Hardware.Computer()
        self.computer.CPUEnabled = True
        self.computer.GPUEnabled = True
        self.computer.Open()

    def get_temperatures(self):
        cpu_temp = None
        gpu_temp = None
        for hardware in self.computer.Hardware:
            hardware.Update()
            if hardware.HardwareType == Hardware.HardwareType.CPU:
                for sensor in hardware.Sensors:
                    if sensor.SensorType == Hardware.SensorType.Temperature:
                        cpu_temp = sensor.Value
            elif hardware.HardwareType == Hardware.HardwareType.GpuNvidia or hardware.HardwareType == Hardware.HardwareType.GpuAti:
                for sensor in hardware.Sensors:
                    if sensor.SensorType == Hardware.SensorType.Temperature:
                        gpu_temp = sensor.Value
            if cpu_temp is None:
                print("Error: Unable to read CPU temperature. Please run the program with elevated privileges.")
                sys.exit(1)
        return cpu_temp, gpu_temp

monitor = HardwareMonitor()

def update_stats(label_cpu, label_ram, label_gpu):
    with tqdm(total=100, desc='CPU', position=0) as cpubar, tqdm(total=100, desc='GPU', position=1) as gpubar, tqdm(total=100, desc='RAM', position=2) as rambar:
        while True:
            rambar.bar_format = '{l_bar}{bar}'
            cpubar.bar_format = '{l_bar}{bar}'
            gpubar.bar_format = '{l_bar}{bar}'

            gpus = GPUtil.getGPUs()
            gpu_load = gpus[0].load * 100 if gpus else 0

            cpu_temp, gpu_temp = monitor.get_temperatures()

            rambar.n = psutil.virtual_memory().percent
            cpubar.n = psutil.cpu_percent()
            gpubar.n = gpu_load

            label_cpu.config(text=f'{cpubar}, {cpu_temp:.0f}°C', fg="red", bg="black")
            label_gpu.config(text=f'{gpubar}, {gpu_temp:.0f}°C', fg="red", bg="black")
            label_ram.config(text=rambar, fg="red", bg="black")

            rambar.refresh()
            cpubar.refresh()
            gpubar.refresh()

            sleep(0.5)

root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.geometry("230x75+100+100")
root.config(bg='black', padx=0, pady=0)
root.wm_attributes('-alpha', 0.60)

label_cpu = tk.Label(root, font=("Helvetica", 12), anchor = "w")
label_gpu = tk.Label(root, font=("Helvetica", 12), anchor = "w")
label_ram = tk.Label(root, font=("Helvetica", 12), anchor = "w")

label_cpu.pack(fill='both', padx=10)
label_gpu.pack(fill='both', padx=10)
label_ram.pack(fill='both', padx=10)

thread = Thread(target=update_stats, args=(label_cpu, label_ram, label_gpu))
thread.daemon = True
thread.start()

root.mainloop()