import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
from ttkthemes import ThemedStyle

# Funciones de la pestaña de comunicación simple
def switch_tab(event):
    selected_tab = tab_control.index(tab_control.select())
    tab_control.select(1 if selected_tab == 0 else 0)

def toggle_serial_port():
    global serial_port
    selected_port = port_combo.get()
    try:
        if not serial_port:
            baudrate = baudrate_combo.get()
            serial_port = serial.Serial(port=selected_port, baudrate=baudrate, timeout=0.1)
            port_button.config(text="Cerrar Puerto")
        else:
            serial_port.close()
            serial_port = None
            port_button.config(text="Abrir Puerto")
    except Exception as e:
        messagebox.showerror("Error", f"Error al cambiar el estado del puerto serial:\n{str(e)}")

def send_data():
    data_to_send = entry.get()
    if serial_port:
        try:
            serial_port.write(data_to_send.encode())
            received_data = serial_port.readline()
            received_data_text.insert("1.0", f"Datos Recibidos: {received_data.decode()}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar o recibir datos:\n{str(e)}")
    else:
        messagebox.showerror("Error", "El puerto no está abierto")

def send_sequence():
    start, end, delay = int(start_spinbox.get()), int(end_spinbox.get()), int(delay_scale.get())
    if serial_port:
        try:
            for num in range(start, end + 1):
                serial_port.write(str(num).encode())
                received_data = serial_port.readline()
                received_data_text.insert("1.0", f"Enviado: {num}, Recibido: {received_data.decode()}\n")
                app.update()
                if delay > 0:
                    app.after(delay)
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar o recibir datos en secuencia:\n{str(e)}")
    else:
        messagebox.showerror("Error", "El puerto no está abierto")

def send_txt_file():
    if serial_port:
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Archivos TXT", "*.txt")])
            if file_path:
                with open(file_path, "rb") as file:
                    file_data = file.read()
                    serial_port.write(file_data)
                received_data = serial_port.readline()
                received_data_text.insert("1.0", f"Datos Recibidos: {received_data.decode()}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar el archivo:\n{str(e)}")
    else:
        messagebox.showerror("Error", "El puerto no está abierto")

def open_received_file():
    received_text = received_data_text.get("1.0", "end-1c")
    if received_text:
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos TXT", "*.txt")])
        if save_path:
            with open(save_path, "w") as file:
                file.write(received_text)


# Configuración del puerto serie (ajusta el puerto y la velocidad baud según tu configuración)
ser = serial.Serial('COM3', 9600)  # Reemplaza 'COM4' con el puerto de tu Arduino

# Crear la ventana principal
app = tk.Tk()
app.title("Aplicación con Pestañas de Comunicación y Control")
app.geometry("800x600")

style = ThemedStyle(app)
style.set_theme("equilux")

tab_control = ttk.Notebook(app)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)

tab_control.add(tab1, text="Pestaña 1: Comunicación Simple")
tab_control.add(tab2, text="Pestaña 2: Pestaña de Control")
tab_control.pack(expand=1, fill="both")

########### Funciones de la "Pestaña 2: Pestaña de Control" 

voltage_values = []
temperature_values = []

# Funciones para simular lecturas de sensores
def read_voltage():
    voltage = random.uniform(0, 5)  # Simulación de lectura de voltaje
    voltage_values.append(voltage)
    voltage_label.config(text=f"Voltaje: {voltage} V")
    update_voltage_plot()
    return voltage

def read_temperature():
    temperature = random.uniform(20, 30)  # Simulación de lectura de temperatura
    temperature_values.append(temperature)
    temperature_label.config(text=f"Temperatura: {temperature} °C")
    temperature_bar["value"] = temperature
    update_temperature_plot()
    return temperature

# Función para establecer la velocidad del motor en Arduino
def set_motor_speed(speed):
    ser.write(f'M{speed}\n'.encode())  # Envía el comando al Arduino para ajustar la velocidad

# Etiquetas para mostrar los valores de voltaje y temperatura
voltage_label = tk.Label(tab2, text="Voltaje: ")
voltage_label.pack()

temperature_label = tk.Label(tab2, text="Temperatura: ")
temperature_label.pack()

# Configuración de la salida PWM
motor_pin = 9  # Reemplaza con el pin de salida PWM de tu Arduino
motor_speed = 0  # Variable para almacenar la velocidad del motor

# Controles para ajustar la velocidad del motor
speed_label = tk.Label(tab2, text="INICIO:")
speed_label.pack()

speed_scale = tk.Scale(tab2, from_=0, to=255, orient="horizontal", length=200, label="0-255")
speed_scale.pack()

set_speed_button = tk.Button(tab2, text="BOTON DE INICIO", command=lambda: set_motor_speed(speed_scale.get()))
set_speed_button.pack()

# Gráficos para mostrar los valores de voltaje y temperatura
fig = plt.Figure(figsize=(6, 4), dpi=100)
voltage_plot = fig.add_subplot(111)
voltage_plot.set_xlabel('Muestras')
voltage_plot.set_ylabel('Voltaje (V)')
voltage_plot.set_title('Gráfico de Voltaje')

fig2 = plt.Figure(figsize=(6, 4), dpi=100)
temperature_plot = fig2.add_subplot(111)
temperature_plot.set_xlabel('Muestras')
temperature_plot.set_ylabel('Temperatura (°C)')
temperature_plot.set_title('Gráfico de Temperatura')

# Creación de lienzo para los gráficos
voltage_canvas = FigureCanvasTkAgg(fig, master=tab2)
voltage_canvas.get_tk_widget().pack()

temperature_canvas = FigureCanvasTkAgg(fig2, master=tab2)
temperature_canvas.get_tk_widget().pack()

# Barra de progreso para mostrar el último valor adquirido de temperatura
temperature_bar = ttk.Progressbar(tab2, orient="horizontal", length=200, mode="determinate")
temperature_bar.pack()

# Funciones para actualizar los gráficos de voltaje y temperatura
def update_voltage_plot():
    voltage_plot.clear()
    voltage_plot.plot(range(len(voltage_values)), voltage_values, marker='o', linestyle='-', color='b')
    voltage_plot.set_xlabel('Muestras')
    voltage_plot.set_ylabel('Voltaje (V)')
    voltage_plot.set_title('Gráfico de Voltaje')
    voltage_canvas.draw()

def update_temperature_plot():
    temperature_plot.clear()
    temperature_plot.plot(range(len(temperature_values)), temperature_values, marker='o', linestyle='-', color='r')
    temperature_plot.set_xlabel('Muestras')
    temperature_plot.set_ylabel('Temperatura (°C)')
    temperature_plot.set_title('Gráfico de Temperatura')
    temperature_canvas.draw()

# Función para actualizar datos y controlar el motor
def update_data():
    voltage = read_voltage()
    temperature = read_temperature()
    set_motor_speed(motor_speed)  # Actualiza la velocidad del motor
    app.after(1000, update_data)

# Iniciar la actualización de datos
update_data()


# Pestaña 1: Comunicación Simple
port_label = ttk.Label(tab1, text="Seleccione el puerto COM:")
port_label.grid(row=0, column=0, padx=10, pady=5)
available_ports = [f'COM{x}' for x in range(1, 17)]
port_combo = ttk.Combobox(tab1, values=available_ports, state="readonly")
port_combo.set(available_ports[0])
port_combo.grid(row=0, column=1, padx=10, pady=5)
port_button = ttk.Button(tab1, text="Abrir Puerto", command=toggle_serial_port)
port_button.grid(row=0, column=2, padx=10, pady=10)

baudrate_label = ttk.Label(tab1, text="Seleccione la velocidad:")
baudrate_label.grid(row=1, column=0, padx=10, pady=5)
baudrate_values = [9600, 19200, 38400, 57600, 115200]
baudrate_combo = ttk.Combobox(tab1, values=baudrate_values, state="readonly")
baudrate_combo.set(9600)
baudrate_combo.grid(row=1, column=1, padx=10, pady=5)

user_input_label = ttk.Label(tab1, text="Ingrese datos:")
user_input_label.grid(row=2, column=0, padx=10, pady=5)
entry = ttk.Entry(tab1)
entry.grid(row=2, column=1, padx=10, pady=5)
send_button = ttk.Button(tab1, text="Enviar Datos", command=send_data)
send_button.grid(row=2, column=2, padx=10, pady=5)

received_data_label = ttk.Label(tab1, text="Datos Recibidos: ")
received_data_label.grid(row=3, column=0, padx=10, pady=5)
received_data_text = tk.Text(tab1, wrap=tk.WORD, height=5, width=50)
received_data_text.grid(row=3, column=1, padx=10, pady=5, columnspan=2)

spinbox_label = ttk.Label(tab1, text="Seleccione el rango de números:")
spinbox_label.grid(row=4, column=0, padx=10, pady=5)
start_spinbox = ttk.Spinbox(tab1, from_=0, to=100, increment=1, width=5)
start_spinbox.set(0)
start_spinbox.grid(row=4, column=1, padx=10, pady=5)
end_spinbox = ttk.Spinbox(tab1, from_=0, to=100, increment=1, width=5)
end_spinbox.set(10)
end_spinbox.grid(row=4, column=2, padx=10, pady=5)

send_sequence_button = ttk.Button(tab1, text="Enviar Secuencia", command=send_sequence)
send_sequence_button.grid(row=5, column=1, columnspan=2, padx=10, pady=5)

delay_label = ttk.Label(tab1, text="Seleccione el retardo (ms):")
delay_label.grid(row=6, column=0, padx=10, pady=5)
delay_scale = ttk.Scale(tab1, from_=0, to=1000, orient="horizontal", length=200)
delay_scale.set(0)
delay_scale.grid(row=6, column=1, columnspan=2, padx=10, pady=5)

send_file_button = ttk.Button(tab1, text="Enviar Archivo TXT", command=send_txt_file)
send_file_button.grid(row=7, column=1, columnspan=2, padx=10, pady=5)

open_file_button = ttk.Button(tab1, text="Abrir Archivo Recibido", command=open_received_file)
open_file_button.grid(row=8, column=1, columnspan=2, padx=10, pady=5)

serial_port = None

app.mainloop()
