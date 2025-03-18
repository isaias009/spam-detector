import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras.layers import Dense

def detectar_spam(csv_file, nuevos_correos):
    # Procesar el conjunto de datos
    data_set = pd.read_csv('uploads/' + csv_file, encoding='latin-1')
    data = data_set.where((pd.notnull(data_set)), '')

    # Cambiar a valores binarios utilizando LabelEncoder
    label_encoder = LabelEncoder()
    data['Category'] = label_encoder.fit_transform(data['Category'])

    # Separar el conjunto de datos en datos de entrenamiento y prueba
    x = data['Message']
    y = data['Category']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=3)

    # Transformar el texto plano a vectores
    vector_extract = TfidfVectorizer(min_df=1, stop_words='english', lowercase=True)
    x_train_features = vector_extract.fit_transform(x_train)
    x_test_features = vector_extract.transform(x_test)

    # Convertir las matrices dispersas a matrices densas
    x_train_features_dense = x_train_features.toarray()
    x_test_features_dense = x_test_features.toarray()

    # Crear el modelo
    model = Sequential()
    model.add(Dense(64, activation='relu', input_dim=x_train_features.shape[1]))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Entrenar el modelo
    model.fit(x_train_features_dense, y_train, epochs=10, batch_size=32, validation_data=(x_test_features_dense, y_test))

    # Preprocesar los nuevos correos electrónicos
    nuevos_correos_features = vector_extract.transform(nuevos_correos)
    nuevos_correos_features_dense = nuevos_correos_features.toarray()

    # Hacer predicciones utilizando el modelo entrenado
    predicciones = model.predict(nuevos_correos_features_dense)

    # Convertir las predicciones en etiquetas de categoría
    etiquetas_predichas = np.where(predicciones < 0.5, 0, 1)

    # Devolver la lista de booleanos
    return etiquetas_predichas.astype(int)
