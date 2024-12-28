import streamlit as st
import pandas as pd
import usuario
from cliente import DataManagerCliente 
from producto import DataManagerProducto
from venta import DataManagerVenta
from cuentaCorriente import DataManagerCuentasCorrientes
from transacciones import dataManagerTransacciones

def main():
    if "page" not in st.session_state:
        st.session_state.page = "index"
    if "sesionIniciada" not in st.session_state:    
        st.session_state.sesionIniciada = False

    st.sidebar.title("Menu de opciones")
    if st.sidebar.button("inicio"):
        st.session_state.page = 'index'
    if st.session_state.sesionIniciada == False:
        if st.sidebar.button("Iniciar sesión"):
            st.session_state.page = 'inicio_sesion'
        if st.sidebar.button("Registrar usuario"):
            st.session_state.page = 'registro_usuario'
    elif st.session_state.sesionIniciada == True:
        if st.sidebar.button("Clientes"):
            st.session_state.page = 'Clientes'
        if st.sidebar.button("Productos"):
            st.session_state.page = 'Productos'
        if st.sidebar.button("Venta"):
            st.session_state.page = 'Venta'
        if st.sidebar.button("Cuentas corrientes"):
            st.session_state.page = 'Cuentas_corrientes'
        if st.sidebar.button("Transacciones"):
            st.session_state.page = 'Transacciones'
        if st.sidebar.button("Cerrar sesion"):
            st.session_state.sesionIniciada = False
            st.rerun()
        


    if st.session_state.page =="index":
        st.title("Siffrah")
        st.header('Sistema de control de stock')

    if st.session_state.page == 'registro_usuario':
        usuario.displayRegistro()
    
    if st.session_state.page == 'inicio_sesion':
         if usuario.displayInicioSesion() == True:
            sesion = True
            st.rerun()
        
    if st.session_state.page == "Clientes":
        objeto = DataManagerCliente()
        objeto.displayClientes()
        
    if st.session_state.page == "Productos":
        objeto = DataManagerProducto()
        objeto.displayProductos()
    
    if st.session_state.page == 'Venta':
        objeto = DataManagerVenta()
        objeto.displayVenta()
        
    if st.session_state.page == 'Cuentas_corrientes':
        objeto = DataManagerCuentasCorrientes()
        objeto.displayCuentasCorrientes()  
        
    if st.session_state.page == 'Transacciones':
        objeto = dataManagerTransacciones()
        objeto.displayTransacciones()

    
     
        
if __name__ == "__main__":
    main()