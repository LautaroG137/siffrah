import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
import time
from cryptography.fernet import Fernet

load_dotenv()


def cargar_clave():
    return open("secret.key", "rb").read()


clave = cargar_clave()
cipher_suite = Fernet(clave)

if "sesionIniciada" not in st.session_state:    
    st.session_state.sesionIniciada = False
        
class Usuario:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def crear_usuario(self, name, password):
        encrypted_name = cipher_suite.encrypt(name.encode()).decode()
        encrypted_password = cipher_suite.encrypt(password.encode()).decode()

        self.cursor.execute('SELECT nombre_usuario FROM usuario')
        list_usuarios = self.cursor.fetchall()

        if list_usuarios:
            for usuario in list_usuarios:
                existente = False
                db_name = cipher_suite.decrypt(usuario["nombre_usuario"].encode()).decode()
                if db_name == name:
                    st.warning(f"El usuario {name} ya este registrado en la base de datos")
                    existente = True
                    break
            if not existente:
                self.cursor.execute('SELECT * FROM usuario ORDER BY idusuario DESC LIMIT 1')
                list_usuarios = self.cursor.fetchall()
                id = list_usuarios[0]['idusuario'] + 1
                self.cursor.execute(
                    'INSERT INTO usuario (idusuario, nombre_usuario, contraseña) VALUES (%s, %s, %s)',
                    (id, encrypted_name, encrypted_password)
                )
                self.connection.commit()
                st.success("El usuario se creó correctamente")
        else:
            id = 1
            self.cursor.execute(
                'INSERT INTO usuario (idusuario, nombre_usuario, contraseña) VALUES (%s, %s, %s)',
                (id, encrypted_name, encrypted_password)
            )
            self.connection.commit()
            st.success("El usuario se creó correctamente")

    def iniciar_sesion(self, name, password):
        self.cursor.execute("SELECT * FROM usuario")
        usuarios = self.cursor.fetchall()
        encontrado = False

        for usuario in usuarios:
            db_name = cipher_suite.decrypt(usuario["nombre_usuario"].encode()).decode()
            db_password = cipher_suite.decrypt(usuario["contraseña"].encode()).decode()
            if db_name == name and db_password == password:
                st.success("Se inició sesión correctamente")
                encontrado = True
                st.session_state.sesionIniciada = True
                st.session_state.page = 'index'
                break
        if encontrado == False:
            st.warning("el usuario y/o contraseña son incorrectos")
        time.sleep(0.5)
        st.rerun()
 
def displayRegistro():
    st.title("Registro de usuario")
    username = st.text_input("Nombre de usuario")
    password = st.text_input("Contraseña", type="password")
    password_2 = st.text_input(" Repita su Contraseña", type="password")

    if st.button("Registrarme"):
        if username and password and password_2 and password == password_2:
            usuario = Usuario()
            usuario.crear_usuario(username, password)
        else:
            if password_2 != password:
                st.warning("las contraseñas no coinciden")
            else:
                st.warning("complete todos los campos")

def displayInicioSesion():
    st.title("Inicio de sesión")
    username = st.text_input("Nombre de usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        usuario = Usuario()
        usuario.iniciar_sesion(username,password)

