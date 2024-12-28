import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
import time
from cliente import Cliente

load_dotenv()

class CuentaCorriente:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host = os.getenv('DB_HOST'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            database = os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor(dictionary=True)
        
    def obtener_dato(self):
        self.cursor.execute('SELECT * FROM cuentascorrientes')
        result = self.cursor.fetchall()
        return result
    
    def obtener_cuenta_por_idcliente(self, idcliente):
        self.cursor.execute('SELECT * FROM cuentascorrientes WHERE idclientes = %s', (idcliente,))
        result = self.cursor.fetchall()
        return result
         
    def cargarVentaCuenta(self,idcliente,detalle,total):
        self.cursor.execute('INSERT INTO cuentascorrientes(idclientes,detalle,total,fecha) VALUES(%s,%s,%s,CURDATE())',(idcliente,detalle,total))
        self.connection.commit()
        st.success("la venta se cargo correctamente en la cuenta")
    def cargarPago(self,idcliente,detalle,total):
        self.cursor.execute('INSERT INTO cuentascorrientes(idclientes,detalle,total,fecha) VALUES(%s,%s,%s,CURDATE())',(idcliente,detalle,total))
        self.connection.commit()
        st.success("el pago se cargo correctamente")
    def cargarVenta(self,detalle,total,cobro):
        self.cursor.execute('INSERT INTO ventas(detalle,total,cobro,fecha) VALUES(%s,%s,%s,CURDATE())',(detalle,total,cobro))
        self.connection.commit()
        st.success("la venta se cargo correctamente")
        
class DataManagerCuentasCorrientes:
    def __init__(self) -> None:
        self.db_cuentas = CuentaCorriente()
        
    def displayCuentasCorrientes(self):
        st.title("Cuentas Corrientes")
        Clientes = Cliente()
        clientes = Clientes.obtener_dato()
        seleccion = st.selectbox(
            "clientes:", 
            [cliente["nombre_cliente"] for cliente in clientes]
            )
        if st.button("mostrar cuenta corriente"):
            id = Clientes.obtener_id_por_nombre(seleccion)
            cuenta= self.db_cuentas.obtener_cuenta_por_idcliente(id)
            st.dataframe(cuenta)
            total = sum(total['total'] for total in cuenta)
            st.warning(f"El total adeudado en la cuenta de {seleccion} es de : ${total}")
        st.title("Pago o entrega a cuenta")
        detalle= st.text_input("detalle de pago")
        monto = st.number_input("monto a entregar")
        if st.button("pagar/entrega a cuenta"):
            id = Clientes.obtener_id_por_nombre(seleccion)
            if detalle =="" or monto == 0:
                st.warning("para que el pago sea efectivo debe ingresar un detalle y un monto mayor a 0")
            else:
                self.db_cuentas.cargarPago(id,detalle,-monto)
                self.db_cuentas.cargarVenta(detalle,-monto,"pago de cuenta corriente")

    
    
    
            
            
                