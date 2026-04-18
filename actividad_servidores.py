from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel
from typing import List


# Crear la API con fastAPI
app = FastAPI() 

# Modelo en Pydantic de un item que va a ser recibido por la API 
class Item(BaseModel):
    name: str
    price: float

# Modelo en Pydantic de un item que vamos a añadir a la base de datos
class ItemDB(BaseModel):
    id: int
    name: str
    price: float
    created_at: str

# Modelo de una lista de items
class ListItems(BaseModel):
    items: List[Item]

# Función para conectarnos con la base de datos de sqlite
def get_db_connection():
    
    # Crear la conexión con la base de datos que esta en el archivo prueba.db
    conn = sqlite3.connect('data/prueba.db')
    # Configurar sqlite para que nos funcione como un diccionario ya que estaremos usando JSON
    conn.row_factory = sqlite3.Row
    conn.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Devolvemos el objeto de la conexion que creamos
    return conn

# Método GET, la raiz de la API aquí solo puse un saludo por que sí
@app.get("/")
def saludar():
    return {"message": "Hola buenos días"}

# Método POST de un item, recibe un request que debe tener como contenido
# Un objeto de tipo Item como el definido anteriormente
@app.post("/items/")
def create_item(load: ListItems):
    # Obtenemos la conexión 
    conexion = get_db_connection()
    # Un cursor sirve para poder escribir en la base de datos de sqlite
    cursor = conexion.cursor()

    # Para cada item de la lista le hacemos el insert correspondiente
    for item in load.items:
        cursor.execute("INSERT INTO items (name, price) VALUES (?, ?)", (item.name, item.price))
    
    # Guardamos los insert que acabamos de hacer, esto es como hacer un ;
    conexion.commit()
    # Cerramos la conexión 
    conexion.close()
    #  Devolvemos la cantidad de items que se crearon
    return {"message": f"Se insertaron {len(load.items)} items"}


# Método GET que va a servir para devolver todos los items
# El formato de respuesta es por lo tanto una lista de ItemDB que es como se guardan realmente
@app.get("/items/all", response_model=List[ItemDB])
def read_all_items():
    # Nuevamente conexión y cursor 
    conexion = get_db_connection()
    cursor = conexion.cursor()
    
    # Hacemos un select de todos los items en la tabla items
    cursor.execute("select * from items")
    # Obtenemos todos los resultados de la query que acabamos de ejecutar
    filas = cursor.fetchall()
    # Cerramos la conexión
    conexion.close()

    if not filas:
        return []
    
    # Devolvemos el diccionario que corresponde a cada una de las filas en la consulta 
    # podemos hacer esto porque estamos usando el row factory
    return [dict(fila) for fila in filas]


# Método GET que devuelve un solo item por su id
@app.get("/items/{item_id}", response_model = ItemDB)
def read_item(item_id: int):
    # Conexión y cursor como anteriormente
    conexion = get_db_connection()
    cursor = conexion.cursor()
    
    # Hacemos el seelct solo del item con el id
    cursor.execute(f"select * from items where id = {item_id}")
    fila = cursor.fetchone()
    conexion.close()

    if fila is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    # Devolvemos el diccionario correspondiente a la fila que nos devolvió
    return dict(fila)



    


