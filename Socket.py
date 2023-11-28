import socket
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from ttkthemes import ThemedTk

class SocketApp:
    def __init__(self):
        self.root = ThemedTk(theme="plastik")
        self.root.configure(bg="green")  # Ajustar el color de fondo a negro
        self.root.title("Socket Connection")

        self.connection_type_label = ttk.Label(self.root, text="Conección tipo Chat:", background="black", foreground="white")
        self.connection_type_label.pack(pady=5)

        self.connection_type_var = tk.StringVar()
        self.connection_type_var.set("Servidor")

        self.server_radio = ttk.Radiobutton(self.root, text="Servidor", variable=self.connection_type_var, value="Servidor", style="black.TRadiobutton")
        self.server_radio.pack(anchor=tk.W)
        self.client_radio = ttk.Radiobutton(self.root, text="Cliente", variable=self.connection_type_var, value="Cliente", style="black.TRadiobutton")
        self.client_radio.pack(anchor=tk.W)

        self.ip_label = ttk.Label(self.root, text="Ingresa Dirección IP:", background="white", foreground="")
        self.ip_label.pack(pady=5)

        self.ip_entry = ttk.Entry(self.root)
        self.ip_entry.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=40, height=10, bg="yellow", fg="black")
        self.text_area.pack(padx=10, pady=10)

        self.start_button = ttk.Button(self.root, text="Iniciar", command=self.start_connection, style="Black.TButton")
        self.start_button.pack(pady=10)

    def start_connection(self):
        connection_type = self.connection_type_var.get()
        ip_address = self.ip_entry.get()

        if connection_type == "Servidor":
            threading.Thread(target=self.start_server, args=(ip_address,), daemon=True).start()
        elif connection_type == "Cliente":
            self.start_client(ip_address)

    def start_server(self, host):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, 65433))
            s.listen()
            self.text_area.insert(tk.END, f"Server listening on {host}:65433\n")
            conn, addr = s.accept()
            with conn:
                self.text_area.insert(tk.END, f"Connected by {addr}\n")
                while True:
                    try:
                        data = conn.recv(1024)
                        if not data:
                            self.text_area.insert(tk.END, "Client disconnected\n")
                            break
                        self.text_area.insert(tk.END, f"Received: {data.decode('utf-8')}\n")
                    except Exception as e:
                        self.text_area.insert(tk.END, f"Error on server: {e}\n")
                        break

    def start_client(self, host):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, 65433))
                self.text_area.insert(tk.END, f"Connected to {host}:65433\n")
                while True:
                    message = input("Enter a message: ")
                    s.sendall(message.encode('utf-8'))
                    data = s.recv(1024)
                    self.text_area.insert(tk.END, f"Received: {data.decode('utf-8')}\n")
            except Exception as e:
                self.text_area.insert(tk.END, f"Error on client: {e}\n")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SocketApp()
    app.run()

