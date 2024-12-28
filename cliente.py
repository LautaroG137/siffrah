import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
import time

load_dotenv()

class Cliente:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host = os.getenv('DB_HOST'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            database = os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def obtener_dato(self):
        self.cursor.execute('SELECT * FROM clientes')
        result = self.cursor.fetchall()
        return result
    
    def obtener_id_por_nombre(self, nombre):
        self.cursor.execute('SELECT idclientes FROM clientes WHERE nombre_cliente = %s', (nombre,))
        result = self.cursor.fetchone()
        return result['idclientes'] 

    def crear_cliente(self,name):
        self.cursor.execute('SELECT nombre_cliente FROM clientes')
        list_clientes = self.cursor.fetchall()
        
        if (len(list_clientes)) != 0:
            for i in range(len(list_clientes)):
                existente = False
                if list_clientes[i]["nombre_cliente"] == name:
                    st.warning(f"El cliente {name} ya está registrado en la base de datos")
                    existente = True
                    break
                
            if existente == False:
                self.cursor.execute('SELECT * FROM clientes ORDER BY idclientes DESC LIMIT 1')
                list_clientes = self.cursor.fetchall()
                id = list_clientes[0]['idclientes']
                id +=1
                self.cursor.execute('INSERT INTO clientes(idclientes , nombre_cliente) VALUES(%s,%s)',(id,name))
                self.connection.commit()
                st.success("el cliente se creo correctamente")   
        else:
            id=1
            self.cursor.execute('INSERT INTO clientes(idclientes , nombre_cliente) VALUES(%s,%s)',(id,name))
            self.connection.commit()
            st.success("el cliente se creo correctamente")
    
    def actualizarCliente(self,id,name):
        self.cursor.execute('UPDATE clientes SET nombre_cliente = %s WHERE idclientes = %s',(name,id))
        self.connection.commit()
        
    def eliminarCliente(self, id):
        self.cursor.execute('DELETE FROM clientes WHERE idclientes = %s',(id,))
        self.connection.commit()
    
class DataManagerCliente:
    def __init__(self) -> None:
        self.db_cliente = Cliente()
                
    @st.dialog("Cargar nuevo cliente")
    def display_crearCliente(self):
        name = st.text_input("ingrese nombre del cliente")
        if st.button("cargar"):
            self.db_cliente.crear_cliente(name)
            time.sleep(0.5)
            st.rerun()
            
    @st.dialog("Modificar/eliminar cliente")
    def display_modificar_cliente(self,id,name):
        nombre_cliente = st.text_input('Ingrese el cliente', value=name)
        accion_realizada = None
        col_a,col_b, col_c =  st.columns([3,2,2])
        with col_b:
            if st.button('Modificar', use_container_width=True):
                self.db_cliente.actualizarCliente(id, nombre_cliente)
                accion_realizada = "modificado"
        with col_c:    
            if st.button('Eliminar', use_container_width=True):
                self.db_cliente.eliminarCliente(id)
                accion_realizada = "eliminado"
        if accion_realizada:
            with st.container():  # Usar contenedor para que ocupe todo el ancho
                if accion_realizada == "modificado":
                    st.success(f"El cliente ha sido {accion_realizada} exitosamente.")
                    time.sleep(0.5)
                    st.rerun()
                elif accion_realizada == "eliminado":
                    st.success(f"El cliente ha sido {accion_realizada} exitosamente.")
                    time.sleep(0.5)
                    st.rerun()                 

    def displayClientes(self):
        st.title("Clientes")
        data_clientes = self.db_cliente.obtener_dato()
        df_clientes = pd.DataFrame(data_clientes)
        df_clientes = df_clientes.rename(columns={"idclientes":"ID" , "nombre_cliente":"CLIENTE"})
        evento = st.dataframe(df_clientes , # nos dice con que dataframe vamos a trabajar
                            hide_index=True , # escondemos la columna de los indices
                            use_container_width=True ,  #usamos todos el ancho del contenedor
                            height=175 , #determinamos la altura del dataframe
                            selection_mode="single-row", #establecemos el modo de seleccion por filas simple(solo se puede seleccionar una fila a la vez)
                            on_select="rerun")  # cuando se selecciona algun cliente , se refresca la pagina
        if evento['selection']['rows']:
            filtrado = df_clientes[df_clientes.index.isin(evento.selection['rows'])]
            valor_id = int(filtrado.iloc[0,0])
            valor_nombre = str(filtrado.iloc[0,1])
            self.display_modificar_cliente(valor_id, valor_nombre)
                    
        if st.button("Cargar cliente"):
            self.display_crearCliente()