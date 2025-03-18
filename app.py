import os
import csv
import pandas as pd
import json
from flask import Flask, render_template, request, redirect, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from spam import detectar_spam


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'machinelearning'
db = SQLAlchemy(app)

# Definir modelo para la entidad de archivos
class Archivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    filas = db.Column(db.Integer, nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False)

with app.app_context():
    # Crear la base de datos
    db.create_all()


@app.route('/')
def index():  
  archivos = Archivo.query.all()

  data = session.get('data')
  collection = session.get('collection')

  if data is not None and collection is not None:
    # Ambas variables 'data' y 'collection' están presentes
    return render_template('index.html', archivos=archivos, data=data, collection=collection)
  elif data is not None:
      # Solo 'data' está presente, 'collection' no está presente
      return render_template('index.html', archivos=archivos, data=data, collection=[])
  elif collection is not None:
      # Solo 'collection' está presente, 'data' no está presente
      return render_template('index.html', archivos=archivos, data=[], collection=collection)
  else:
      # Ninguna de las variables está presente
      return render_template('index.html', archivos=archivos, data=[], collection=[])

  



@app.route('/message', methods=['POST'])
def message():
  nuevos_mensajes = [request.form['msg']]
  process(nuevos_mensajes, 'data')

  return redirect('/?page=msg')


@app.route('/message/cancel', methods=['POST'])
def message_cancel():
  session.pop('data')
  return redirect('/?page=msg')



@app.route('/message/collection', methods=['POST'])
def message_collection():
  nuevos_mensajes = request.form['msg']
  coleccion = json.loads(nuevos_mensajes)
  process(coleccion, 'collection')

  return redirect('/?page=collection')


@app.route('/message/collection/cancel', methods=['POST'])
def message_collection_cancel():
  session.pop('collection')
  return redirect('/?page=collection')



@app.route('/messages/add', methods=['POST'])
def add_dataset():

  archivo = Archivo.query.filter_by(estado=1).first()
  datatype = request.form['datatype']
  tag = request.form['tag']
  msg = request.form['msg']
  res = request.form['res']
  
  if res != 'correct':
     tag = intercambiar_valor(tag)

  agregar_linea_csv(tag, msg, archivo.nombre)

  if datatype == "data":
    eliminar_coincidencias(msg, 'data')
    return redirect('/?page=msg')
  
  elif datatype == "collection":
    eliminar_coincidencias(msg, 'collection')
    return redirect('/?page=collection')
  
  



@app.route('/cargar-archivo', methods=['POST'])
def cargar_archivo():
  archivo = request.files['archivo']
  nombre_archivo = archivo.filename

  # Generar un nombre único para el archivo
  nombre_unico = datetime.now().strftime("%Y%m%d%H%M%S") + '_' + nombre_archivo

  # Guardar el archivo en la carpeta "uploads"
  carpeta_uploads = 'uploads'
  ruta_archivo = os.path.join(carpeta_uploads, nombre_unico)
  archivo.save(ruta_archivo)
  cantidad_filas = contar_filas_csv(ruta_archivo)

  # Guardar el nombre y la fecha de registro en la base de datos
  nuevo_archivo = Archivo(nombre=nombre_unico, estado=0, filas=cantidad_filas, fecha_registro=datetime.now())
  db.session.add(nuevo_archivo)
  db.session.commit()

  return redirect('/?page=data')



@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_registro(id):
  archivo = Archivo.query.get_or_404(id)
  carpeta_uploads = 'uploads'

  # Eliminar el archivo del sistema de archivos
  ruta_archivo = os.path.join(carpeta_uploads, archivo.nombre)
  if os.path.exists(ruta_archivo):
      os.remove(ruta_archivo)

  # Eliminar el registro de la base de datos
  db.session.delete(archivo)
  db.session.commit()

  return redirect('/?page=data')  # Redirigir a la lista de archivos



@app.route('/actualizar_estado/<int:id>', methods=['POST'])
def actualizar_estado(id):
  # Obtener el registro correspondiente al ID
  archivo = Archivo.query.get(id)

  # Actualizar el estado del registro seleccionado a 1
  archivo.estado = 1
  db.session.commit()

  # Actualizar el estado de los demás registros a 0
  otros_archivos = Archivo.query.filter(Archivo.id != id).all()
  for otro_archivo in otros_archivos:
      otro_archivo.estado = 0
  db.session.commit()

  return redirect('/?page=data')




def contar_filas_csv(archivo_csv):
    df = pd.read_csv(archivo_csv)
    cantidad_filas = len(df)
    return cantidad_filas


def process(nuevos_mensajes, sessionname):
  archivo = Archivo.query.filter_by(estado=1).first()

  # Obtener los resultados desde la variable 'res'
  resultados = detectar_spam(archivo.nombre, nuevos_mensajes)

  # Obtener la fecha actual
  fecha_actual = datetime.now()

  # Crear la lista de datos con la estructura deseada
  data = []
  for mensaje, resultado in zip(nuevos_mensajes, resultados):
      resultado = resultado.item()  # Convertir el valor int64 a un tipo de dato nativo de Python
      data.append({
          'msg': mensaje,
          'res': bool(resultado),  # Convertir el resultado a un booleano
          'fecha': fecha_actual.strftime('%d de %B del %Y, %H:%M:%S')  # Formatear la fecha como deseas
      })

  session[sessionname] = data



def agregar_linea_csv(category, message, archivo_csv):
    
  with open('uploads/' + archivo_csv, 'a', newline='', encoding='utf-8') as file:
      writer = csv.writer(file)
      # Escribir la nueva línea en el archivo CSV
      writer.writerow([])
      writer.writerow([category, message])

  df = pd.read_csv('uploads/' + archivo_csv)
  df = df.dropna()
  df.to_csv('uploads/' + archivo_csv, index=False)

  # Obtener la cantidad actual de líneas en el archivo CSV
  cantidad_lineas_actual = contar_filas_csv(os.path.join('uploads', archivo_csv))

  # Actualizar la cantidad de líneas en el registro de archivo en la base de datos
  archivo = Archivo.query.filter_by(nombre=archivo_csv).first()
  archivo.filas = cantidad_lineas_actual
  db.session.commit()



def eliminar_coincidencias(valor, sessionname):
    data = session.get(sessionname)
    
    if data is not None:
        # Filtrar las coincidencias y crear una nueva colección sin ellas
        nueva_data = [item for item in data if item['msg'] != valor]
        
        # Guardar la nueva colección en la sesión
        session[sessionname] = nueva_data


def intercambiar_valor(variable):
    if variable == "spam":
        return "ham"
    elif variable == "ham":
        return "spam"
    else:
        return variable
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
