import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

class Transaccion:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host = os.getenv('DB_HOST'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            database = os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor(dictionary=True)
        
        
    def obtener_dato(self):
        self.cursor.execute('SELECT * FROM ventas')
        result = self.cursor.fetchall()
        return result
    
class dataManagerTransacciones:
    def __init__(self) -> None:
        self.db_ventas = Transaccion()
        
    def displayTransacciones(self):
        st.title("Registro de transacciones")
        registro = self.db_ventas.obtener_dato()
        st.dataframe(registro)
    
    
    