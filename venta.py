import mysql.connector
import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
import time
from producto import DataManagerProducto , Producto
from cliente import Cliente
from datetime import datetime
from cuentaCorriente import CuentaCorriente

load_dotenv()

if "df_productos" not in st.session_state:
    st.session_state.df_productos = pd.DataFrame(columns=["Producto","Precio Efectivo","Precio de lista","Cantidad","Total Efectivo","Total Lista"])      
if "totales" not in st.session_state:
    st.session_state["totales"] = pd.DataFrame([[0, 0]], columns=["TOTAL EFECTIVO", "TOTAL LISTA"])  
    
class Venta:
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
    
    def cargarVenta(self,detalle,total,cobro):
        self.cursor.execute('INSERT INTO ventas(detalle,total,cobro,fecha) VALUES(%s,%s,%s,CURDATE())',(detalle,total,cobro))
        self.connection.commit()
        st.success("la venta se cargo correctamente")
     
class DataManagerVenta:
    def __init__(self) -> None:
        self.db_venta = Venta()
    
    def displayVenta(self):
        if "nueva_fila" not in st.session_state:
            st.session_state.nueva_fila = None
        st.title("VENTA")
        if st.session_state.nueva_fila !=None :  
            # aca se carga el nuevo producto a la lista de venta
            nueva_fila = pd.DataFrame([st.session_state.nueva_fila])
            st.session_state.df_productos = pd.concat([st.session_state.df_productos, nueva_fila], ignore_index=True)
            st.session_state.nueva_fila = None
            
        #se muestra en pantalla la lista de venta
        st.write(st.session_state.df_productos) 
        
        # esto muestra los totales de los productos en la lista de venta
        st.session_state["totales"].loc[0, "TOTAL LISTA"] = st.session_state.df_productos["Total Lista"].sum()
        st.session_state["totales"].loc[0, "TOTAL EFECTIVO"] = st.session_state.df_productos["Total Efectivo"].sum()
        st.write(st.session_state["totales"])
        
        col1,col2,col3,col4,col5 =st.columns([1, 1, 1, 1, 1])
        with col1:
            if st.button("Cargar producto"):
                self.cargar_prod()
        with col2:
            if st.button("borrar producto"):
                df_prod=st.session_state.df_productos
                self.borrar_prod(df_prod)
        with col3:
            if st.button("Venta efectivo"):
                df_prod=st.session_state.df_productos
                cliente= None
                self.vender(df_prod,cliente,type="efectivo")
                st.session_state.df_productos = pd.DataFrame(columns=["Producto","Precio Efectivo","Precio de lista","Cantidad","Total Efectivo","Total Lista"])
                st.rerun() 
        with col4:
            if st.button("Venta de lista"):
                df_prod=st.session_state.df_productos
                cliente=None
                self.vender(df_prod,cliente,type="lista")
                st.session_state.df_productos = pd.DataFrame(columns=["Producto","Precio Efectivo","Precio de lista","Cantidad","Total Efectivo","Total Lista"])
                st.rerun() 
        with col5:
            if st.button("Venta a cuenta"):
                st.session_state.cliente = None
                self.seleccionar_cliente()
                               
                  
    @st.dialog("seleccionar cliente")   
    def seleccionar_cliente(self):
        clientes = Cliente()
        clientes = clientes.obtener_dato()

        seleccion = st.selectbox(
        "clientes:", 
        [cliente["nombre_cliente"] for cliente in clientes]
        ) 
        st.write(f"a seleccionado la cuenta corriente del cliente: {seleccion}")
        if st.button("seleccionar"):
            st.session_state.cliente = seleccion
            if st.session_state.cliente != None:
                df_prod=st.session_state.df_productos
                cliente = st.session_state.cliente
                self.vender(df_prod,cliente,type="cuenta")

           
    @st.dialog("Cargar Producto")    # con esta funcion se cargan productos al dataframe df_productos
    def cargar_prod(self):
        productos = Producto()
        productos = productos.obtener_dato()
       
        seleccion = st.selectbox(
            "Productos disponibles:", 
            [producto["nombre_producto"] for producto in productos]
        )
        
        producto_seleccionado = next(producto for producto in productos if producto["nombre_producto"] == seleccion)
        st.write(f"Has seleccionado: {producto_seleccionado['nombre_producto']}")
        st.write(f"Precio efectivo: {producto_seleccionado['precio_efectivo_producto']}")
        st.write(f"Precio lista: {producto_seleccionado['precio_lista_producto']}")
        st.write(f"Stock disponible: {producto_seleccionado['stock_producto']}")
        cantidad = st.number_input(f"Cuantos {producto_seleccionado['nombre_producto']} va a vender?",step=1, format="%d")
        
        if st.button("cargar"):
            df = st.session_state.df_productos['Producto']
            df = df.tolist()
            if cantidad == 0:
                st.warning("la cantidad a vender debe ser mayor a 0")
            elif producto_seleccionado['stock_producto'] < cantidad :
                st.warning(f"no tiene el suficiente stock de {producto_seleccionado['nombre_producto']}")
            elif producto_seleccionado['nombre_producto'] in df :
                st.warning(f" el producto {producto_seleccionado['nombre_producto']} ya se encuentra en la lista de venta")
            else:
                st.session_state.nueva_fila = {"Producto":producto_seleccionado['nombre_producto'],"Precio Efectivo":producto_seleccionado['precio_efectivo_producto'],"Precio de lista":producto_seleccionado['precio_lista_producto'],"Cantidad":cantidad,"Total Efectivo":producto_seleccionado['precio_efectivo_producto']*cantidad,"Total Lista":producto_seleccionado['precio_lista_producto']*cantidad}
                st.rerun()
                
    @st.dialog("que producto quiere borrar?")
    def borrar_prod(self,df):
        st.write(df)
        indice = st.number_input("que indice desea borrar?",step=1, format="%d")
        if st.button("borrar"):
            if indice == 0:
                totalEf=(df.iloc[0, 4])
                totalList=(df.iloc[0, 5])
                st.session_state["totales"].loc[0, "TOTAL EFECTIVO"] -= totalEf
                st.session_state["totales"].loc[0, "TOTAL LISTA"] -= totalList
                df = df.drop(indice)
                st.session_state.df_productos = df
                st.rerun()     
            if indice !=0 :
                totalEf=(df.iloc[0, 4])
                totalList=(df.iloc[0, 5])
                st.session_state["totales"].loc[0, "TOTAL EFECTIVO"] -= totalEf
                st.session_state["totales"].loc[0, "TOTAL LISTA"] -= totalList
                df = df.drop(indice)
                st.session_state.df_productos = df
                st.rerun()
            st.rerun()
            
                
    def vender(self,df,cliente,type):
        if len(st.session_state.df_productos)>0:
            if type == "efectivo":
                df = df.to_numpy()
                nombre_prod = df[:, [0,3]]
                producto = Producto()
                lista = []
                for nombre , cantidad in nombre_prod:
                    lista.append(f"{cantidad} {nombre}")
                    id=(producto.obtenerID(nombre))
                    id= id[0]["idproductos"]
                    producto.bajarStock(id,cantidad)
                detalle = ", ".join(lista)
                total=st.session_state["totales"].loc[0, "TOTAL EFECTIVO"]
                venta = Venta()
                venta.cargarVenta(detalle,total,type)
            elif type == "lista":
                df = df.to_numpy()
                nombre_prod = df[:, [0,3]]
                producto = Producto()
                lista = []
                for nombre , cantidad in nombre_prod:
                    lista.append(f"{cantidad} {nombre}")
                    id=(producto.obtenerID(nombre))
                    id= id[0]["idproductos"]
                    producto.bajarStock(id,cantidad)
                detalle = ", ".join(lista)
                total=st.session_state["totales"].loc[0, "TOTAL LISTA"]
                venta = Venta()
                venta.cargarVenta(detalle,total,type)
            elif type == "cuenta":
                df = df.to_numpy()
                nombre_prod = df[:, [0,3]]
                producto = Producto()
                lista = []
                for nombre , cantidad in nombre_prod:
                    lista.append(f"{cantidad} {nombre}")
                    id=(producto.obtenerID(nombre))
                    id= id[0]["idproductos"]
                    producto.bajarStock(id,cantidad)
                detalle = ", ".join(lista)
                clientes = Cliente()
                idcliente = clientes.obtener_id_por_nombre(cliente)
                cc = CuentaCorriente()
                total=st.session_state["totales"].loc[0, "TOTAL LISTA"]
                cc.cargarVentaCuenta(idcliente,detalle,total)
                venta = Venta()
                venta.cargarVenta(detalle,total,type)
                time.sleep(1)
                st.session_state.cliente = None
                st.session_state.df_productos = pd.DataFrame(columns=["Producto","Precio Efectivo","Precio de lista","Cantidad","Total Efectivo","Total Lista"])
                st.rerun()
                
            
            
            
            
        