import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
import time

load_dotenv()

class Producto:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host = os.getenv('DB_HOST'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            database = os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor(dictionary=True)
        
    def obtener_dato(self):
        self.cursor.execute('SELECT * FROM productos')
        result = self.cursor.fetchall()
        return result   
         
    def crearProd(self,nombre,precioEfectivo,precioLista,stock):
        self.cursor.execute("SELECT * FROM productos")
        list_prod = self.cursor.fetchall()
        if (len(list_prod)) != 0:
            for i in range(len(list_prod)):
                existente = False
                if list_prod[i]["nombre_producto"] == nombre:
                    st.warning(f"El producto {nombre} ya está registrado en la base de datos")
                    existente = True
                    break
                
            if existente == False:
                self.cursor.execute('SELECT * FROM productos ORDER BY idproductos DESC LIMIT 1')
                list_prod = self.cursor.fetchall()
                id = list_prod[0]['idproductos']
                id +=1
                self.cursor.execute('INSERT INTO productos(idproductos , nombre_producto , precio_lista_producto , precio_efectivo_producto , stock_producto) VALUES(%s,%s,%s,%s,%s)',(id,nombre,precioLista,precioEfectivo,stock))
                self.connection.commit()
                st.success("el producto se creo correctamente")   
        else:
            id=1
            self.cursor.execute('INSERT INTO productos(idproductos , nombre_producto , precio_lista_producto , precio_efectivo_producto , stock_producto) VALUES(%s,%s,%s,%s,%s)',(id,nombre,precioLista,precioEfectivo,stock))
            self.connection.commit()
            st.success("el producto se creo correctamente")

    def actualizarProducto(self,id,nombre,precioLista,precioEfectivo,stock):
        self.cursor.execute('UPDATE productos SET nombre_producto = %s , precio_lista_producto = %s , precio_efectivo_producto = %s , stock_producto = %s  WHERE idproductos = %s',(nombre,precioLista,precioEfectivo,stock,id))
        self.connection.commit()
        
    def eliminarProducto(self, id):
        self.cursor.execute('DELETE FROM productos WHERE idproductos = %s',(id,))
        self.connection.commit()
    def bajarStock(self, id, cantidad):
        self.cursor.execute('UPDATE productos SET stock_producto = stock_producto - %s WHERE idproductos = %s',(cantidad, id))
        self.connection.commit()
    def obtenerID(self,nombre):
        self.cursor.execute("SELECT idproductos FROM productos WHERE nombre_producto = %s" ,(nombre,))
        id = self.cursor.fetchall()
        return id
        
class DataManagerProducto:
    def __init__(self) -> None:
        self.db_producto = Producto()
        
    def displayProductos(self):
        st.title("productos")
        list_productos = self.db_producto.obtener_dato()
        df_productos = pd.DataFrame(list_productos)
        df_productos = df_productos.rename(columns={"idproductos":"ID","nombre_producto":"PRODUCTO","precio_efectivo_producto":"PRECIO EFECTIVO","precio_lista_producto":"PRECIO LISTA","stock_producto":"STOCK"})
        evento = st.dataframe(df_productos , # nos dice con que dataframe vamos a trabajar
                            hide_index=True , # escondemos la columna de los indices
                            use_container_width=True ,  #usamos todos el ancho del contenedor
                            height=175 , #determinamos la altura del dataframe
                            selection_mode="single-row", #establecemos el modo de seleccion por filas simple(solo se puede seleccionar una fila a la vez)
                            on_select="rerun")  # cuando se selecciona algun cliente , se refresca la pagina
        if evento['selection']['rows']:
            filtrado = df_productos[df_productos.index.isin(evento.selection['rows'])]
            valor_id = int(filtrado.iloc[0,0])
            valor_nombre = str(filtrado.iloc[0,1])
            valor_precio_efectivo = str(filtrado.iloc[0,2])
            valor_precio_lista = str(filtrado.iloc[0,3])
            valor_stock = str(filtrado.iloc[0,4])
            self.displayModificarProducto(valor_id, valor_nombre,valor_precio_efectivo,valor_precio_lista,valor_stock)    
                 
        if st.button("Cargar nuevo Producto"):
            self.displayCrearProducto()
            
           
    @st.dialog("Cargar nuevo producto")
    def displayCrearProducto(self):
        nombre = st.text_input("nombre del prodcuto")
        precioEfectivo = st.text_input("precio efectivo")
        precioLista = st.text_input("precio lista")
        stock = st.text_input("stock")
        if st.button("Crear"):
            self.db_producto.crearProd(nombre,precioEfectivo,precioLista,stock)
            time.sleep(0.5)
            st.rerun()

    @st.dialog("modificar o eliminar producto")
    def displayModificarProducto(self,id,nombre,precioEfectivo,precioLista,stock):
        nombre_producto = st.text_input('Ingrese el producto', value=nombre)
        precio_lista_producto = st.text_input("ingrese precio de lista", value=precioLista)
        precio_efectivo_producto = st.text_input("ingrese precio efectivo", value=precioEfectivo)
        stock_producto = st.text_input("stock", value=stock)
        accion_realizada = None
        col_a,col_b, col_c =  st.columns([3,2,2])
        with col_b:
            if st.button('Modificar', use_container_width=True):
                self.db_producto.actualizarProducto(id,nombre_producto,precio_lista_producto,precio_efectivo_producto,stock_producto)         
                accion_realizada = "modificado"
        with col_c:    
            if st.button('Eliminar', use_container_width=True):
                self.db_producto.eliminarProducto(id)
                accion_realizada = "eliminado"
        if accion_realizada:
            with st.container():  # Usar contenedor para que ocupe todo el ancho
                if accion_realizada == "modificado":
                    st.success(f"El producto ha sido {accion_realizada} exitosamente.")
                    time.sleep(0.5)
                    st.rerun()
                elif accion_realizada == "eliminado":
                    st.success(f"El producto ha sido {accion_realizada} exitosamente.")
                    time.sleep(0.5)
                    st.rerun()                 