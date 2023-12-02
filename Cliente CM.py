import socket
import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

# Dirección IP y puerto del servidor
SERVER_HOST = '192.168.100.10'
SERVER_PORT = 65432

# Crear ventana de tkinter
root = tk.Tk()
root.title("Lectura de Humedad")

# Crear figura de matplotlib
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
ax.set_title('Lectura de Humedad')
ax.set_xlabel('Tiempo')
ax.set_ylabel('Humedad')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Inicializar valores de la gráfica
buffer_size = 10
humidity_values = deque([0] * buffer_size, maxlen=buffer_size)
timestamps = deque(range(buffer_size), maxlen=buffer_size)
line, = ax.plot(timestamps, humidity_values)

def update_data():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            data = client_socket.recv(1024).decode().strip()
            try:
                humidity = int(data)
                humidity_values.append(humidity)
                timestamps.append(timestamps[-1] + 1)

                line.set_xdata(list(timestamps))
                line.set_ydata(list(humidity_values))

                ax.relim()
                ax.autoscale_view()

                canvas.draw_idle()

                if humidity < 600:
                    ask_activate_motors(client_socket)
            except (ValueError, IndexError):
                pass
        except ConnectionRefusedError:
            print("No se puede conectar con el servidor")

def ask_activate_motors(client_socket):
    result = messagebox.askyesno("Activar motores", "¿Deseas activar los motores?")
    if result:
        try:
            message = "A"  # Enviar 'A' al servidor si se elige "sí"
            client_socket.sendall(message.encode())
        except:
            messagebox.showerror("Error", "Error al enviar mensaje al servidor")
    else:
        try:
            message = "D"  # Enviar 'D' al servidor si se elige "no"
            client_socket.sendall(message.encode())
        except:
            messagebox.showerror("Error", "Error al enviar mensaje al servidor")

def update():
    update_data()
    root.after(1000, update)

update()

root.mainloop()