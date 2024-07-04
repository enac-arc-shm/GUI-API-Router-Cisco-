import json
import requests
import tkinter as tk
from tkinter import messagebox, ttk
from requests.auth import HTTPBasicAuth
from flask import Flask, redirect, url_for, render_template, request


# Configuración de conexión al router
ROUTER_IP = '192.168.56.101'
USERNAME = 'cisco'
PASSWORD = 'cisco123'
BASE_URL = f'https://{ROUTER_IP}/restconf'

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)

def get_users():
    url = f'{BASE_URL}/data/Cisco-IOS-XE-native:native/username'
    response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers={'Accept': 'application/yang-data+json'}, verify=False)

    if response.status_code == 200:
        return response.json().get('Cisco-IOS-XE-native:username', [])
    else:
        return []

def create_user(username, password):
    url = f'{BASE_URL}/data/Cisco-IOS-XE-native:native/username={username}'
    headers = {
        'Content-Type': 'application/yang-data+json',
        'Accept': 'application/yang-data+json'
    }
    payload = {
        "Cisco-IOS-XE-native:username": {
            "name": username,
            "privilege": 15,
            "secret": {
                "encryption": 0,
                "secret": password
            }
        }
    }

    response = requests.put(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, data=json.dumps(payload), verify=False)

    if response.status_code in [200, 201, 204]:
        print(f"Usuario {username} creado correctamente.") 
    else:
        print("Error", f"Error al crear el usuario: {response.status_code}")

def delete_user(username):
    url = f'{BASE_URL}/data/Cisco-IOS-XE-native:native/username={username}'
    headers = {
        'Accept': 'application/yang-data+json'
    }

    response = requests.delete(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers, verify=False)

    if response.status_code in [200, 204]:
        print("Éxito", f"Usuario {username} eliminado correctamente.")
    else:
        print("Error", f"Error al eliminar el usuario: {response.status_code}")


@app.route('/')
def index():
    users = get_users()
    return render_template('index.html', users=users)

@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/delete_item/<string:user>')
def delete_item(user):
    delete_user(user)
    return redirect(url_for('index'))


@app.route('/create_user_route', methods=['GET', 'POST'])
def create_user_route():
    user = request.form['user']
    password = request.form['password']
    create_user(user, password)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8008)