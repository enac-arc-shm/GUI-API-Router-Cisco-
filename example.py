import json
import requests
import tkinter as tk
from tkinter import messagebox, ttk
from requests.auth import HTTPBasicAuth


# Configuración de conexión al router
ROUTER_IP = '192.168.56.101'
USERNAME = 'cisco'
PASSWORD = 'cisco123'
BASE_URL = f'https://{ROUTER_IP}/restconf'

# Desactivar las advertencias de SSL (no recomendable para producción)
requests.packages.urllib3.disable_warnings()

def get_interfaces_info():
    url = f'{BASE_URL}/data/ietf-interfaces:interfaces'
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={'Accept': 'application/yang-data+json'}, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        messagebox.showerror("Error", f"Error al obtener la información de las interfaces: {response.status_code}")
        return {}

def format_interfaces_info(info):
    formatted_info = ""
    interfaces = info.get('ietf-interfaces:interfaces', {}).get('interface', [])
    for iface in interfaces:
        formatted_info += f"Interface: {iface.get('name')}\n"
        formatted_info += f"  Type: {iface.get('type')}\n"
        if 'ietf-ip:ipv4' in iface:
            for address in iface['ietf-ip:ipv4'].get('address', []):
                formatted_info += f"  IPv4 Address: {address.get('ip')}\n"
                formatted_info += f"  Subnet Mask: {address.get('netmask')}\n"
        formatted_info += "\n"
    return formatted_info

def set_banner_motd(banner_message):
    url = f'{BASE_URL}/data/Cisco-IOS-XE-native:native/banner'
    headers = {
        'Content-Type': 'application/yang-data+json',
        'Accept': 'application/yang-data+json'
    }
    payload = {
        "Cisco-IOS-XE-native:banner": {
            "motd": {
                "banner": banner_message
            }
        }
    }

    response = requests.put(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, data=json.dumps(payload), verify=False)

    if response.status_code in [200, 201, 204]:
        messagebox.showinfo("Éxito", "Banner MOTD actualizado correctamente.")
    else:
        messagebox.showerror("Error", f"Error al actualizar el banner MOTD: {response.status_code}")
        print(response.text)

def save_running_config():
    url = f'{BASE_URL}/operations/cisco-ia:save-config'
    headers = {
        'Content-Type': 'application/yang-data+json',
        'Accept': 'application/yang-data+json'
    }
    payload = {
        "cisco-ia:input": {}
    }

    response = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, data=json.dumps(payload), verify=False)

    if response.status_code in [200, 201, 204]:
        messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
    else:
        messagebox.showerror("Error", f"Error al guardar la configuración: {response.status_code}")
        print(response.text)

def set_hostname(hostname):
    url = f'{BASE_URL}/data/Cisco-IOS-XE-native:native/hostname'
    headers = {
        'Content-Type': 'application/yang-data+json',
        'Accept': 'application/yang-data+json'
    }
    payload = {
        "Cisco-IOS-XE-native:hostname": hostname
    }

    response = requests.put(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, data=json.dumps(payload), verify=False)

    if response.status_code in [200, 201, 204]:
        messagebox.showinfo("Éxito", f"Hostname actualizado a {hostname} correctamente.")
    else:
        messagebox.showerror("Error", f"Error al actualizar el hostname: {response.status_code}")
        print(response.text)

def get_hostname():
    url = f'{BASE_URL}/data/Cisco-IOS-XE-native:native/hostname'
    headers = {
        'Content-Type': 'application/yang-data+json',
        'Accept': 'application/yang-data+json'
    }

    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, verify=False)
    return(json.dumps(response.json() , indent=4))

# Interfaz gráfica
def create_gui():

    _hostname = get_hostname()
    try:
        data_dict = json.loads(_hostname)
        hostname = data_dict.get("Cisco-IOS-XE-native:hostname", "Hostname no encontrado")
    except json.JSONDecodeError:
        hostname = "Error al decodificar JSON"

    root = tk.Tk()
    root.title(str(hostname))

    # Estilo
    style = ttk.Style()
    style.theme_use('clam')

    # Colores
    background_color = '#2E2E2E'
    frame_color = '#3E3E3E'
    button_color = '#5A5A5A'
    text_color = '#FFFFFF'
    entry_background_color = '#5A5A5A'
    entry_foreground_color = '#FFFFFF'

    # Configurar estilos
    style.configure('TLabel', background=background_color, foreground=text_color, font=('Helvetica', 10))
    style.configure('TFrame', background=frame_color)
    style.configure('TButton', background=button_color, foreground=text_color, font=('Helvetica', 10, 'bold'))
    style.configure('TEntry', fieldbackground=entry_background_color, foreground=entry_foreground_color)
    style.configure('TextFrame.TFrame', background=frame_color)

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(2, weight=1)
    frame.columnconfigure(3, weight=1)

    # Mostrar información de las interfaces
    def show_interfaces_info():
        info = get_interfaces_info()
        if info:
            formatted_info = format_interfaces_info(info)
            text.delete('1.0', tk.END)
            text.insert(tk.END, formatted_info)

    # Actualización del hostname
    hostname_entry = ttk.Entry(frame, width=50)
    hostname_entry.grid(row=2, column=0,columnspan=1,  padx=(0, 10), pady=8, sticky=(tk.W, tk.E))

    def update_hostname():
        hostname = hostname_entry.get()
        set_hostname(hostname)

    hostname_button = ttk.Button(frame, text='Actualizar Hostname', command=update_hostname)
    hostname_button.grid(row=2, column=1, pady=5,  padx=(10, 0),sticky=(tk.W, tk.E))

    # Actualización del banner MOTD
    banner_entry = ttk.Entry(frame, width=50)
    banner_entry.grid(row=3, column=0, columnspan=1,padx=(0, 10), pady=8, sticky=(tk.W, tk.E))

    def update_banner():
        banner_message = banner_entry.get()
        set_banner_motd(banner_message)

    update_banner_button = ttk.Button(frame, text='Actualizar Banner', command=update_banner)
    update_banner_button.grid(row=3, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))

    interfaces_info_button = ttk.Button(frame, text='Mostrar Información de Interfaces', command=show_interfaces_info)
    interfaces_info_button.grid(row=6, column=0, columnspan=5, pady=5, sticky=(tk.W, tk.E))

    # Área de texto para mostrar la información
    text_frame = ttk.Frame(frame, padding="5", style='TextFrame.TFrame')
    text_frame.grid(row=7, column=0, columnspan=4, pady=10, padx=10, sticky=(tk.W, tk.E))
    text_frame.columnconfigure(0, weight=1)
    text_frame.rowconfigure(0, weight=1)

    save_config_button = ttk.Button(frame, text='Guardar Configuración', command=save_running_config)
    save_config_button.grid(row=8, column=0, columnspan=5, pady=5, sticky=(tk.W, tk.E))

    text = tk.Text(text_frame, wrap='word', height=20, width=70, background='#D3D3D3')
    text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    scroll_y = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
    scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
    text['yscrollcommand'] = scroll_y.set

    root.mainloop()

if __name__ == '__main__':
    create_gui()
