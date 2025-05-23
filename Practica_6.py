# -*- coding: utf-8 -*-
"""Practica6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1UJWqaYxd4pggzb4G92G-pHss-LaT4EPS

# Importacion de librerias
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.preprocessing import TransactionEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from mlxtend.frequent_patterns import apriori, association_rules

"""# Parte 1 Clustering en python

**Exploracion y preparacion del dataseet**
"""

#Cargar el dataseet
df = pd.read_csv("/content/drive/MyDrive/clases/universidad/semestre 6/Mineria de datos/online_retail_II_sample_5000.csv")

#Mostrar las primeras filas
print(df.head())

#Filtrado de filas donde Quantity y Price sean mayores a 0
df_clean = df[(df["Quantity"] > 0) & (df["Price"] > 0)]

#Eliminacion de datos nulos
df_clean = df_clean.dropna()

#Eliminacion de duplicados
df_clean = df_clean.drop_duplicates()

#Chequeo rapido de los datos
print(df_clean.head())

#Impresion de df_clean.describe() para observar la distribucion y detectar valores atipicos
print(df_clean.describe())

"""**Seleccion y Normalizacion de Caracteristicas**"""

#Creacion de caracteristica TotalPrice
df_clean["TotalPrice"] = df_clean["Quantity"] * df_clean["Price"]

#Guardamos el dataseet en una copia
df_clean.to_csv("/content/drive/MyDrive/clases/universidad/semestre 6/Mineria de datos/copy_online_retail_II_sample_5000.csv", index=False)

#Seleccionamos los datos guardandolos en una variable
features = df_clean[["Quantity", "Price", "TotalPrice"]]

#Verificamos los datos
print(features.head())

# Instanciar el escalador
scaler = StandardScaler()

# Ajustar y transformar los datos
features_scaled = scaler.fit_transform(features)

# Ver resultado como DataFrame
features_scaled = pd.DataFrame(features_scaled, columns=["Quantity", "Price Each", "TotalPrice"])

#Comprobar que su media sea 0 y desviacion estandar de 1
features_scaled.describe()

"""**Implementacion de K-means**"""

#configuracion inicial de valor k = 3

#Creacion del modelo
kmeans = KMeans(n_clusters=3, random_state=42)

#Ajuste del modelo
kmeans.fit(features_scaled)

#Obtener etiquetas de cluster
labels = kmeans.labels_
sse = kmeans.inertia_
sil_score = silhouette_score(features_scaled, labels)

#Impresion de resultados
print(f"Inercia (SSE): {sse}")
print(f"Coeficiente de silueta: {sil_score}")

#Ajuste de valor k probando en un rango de valores de 2 a 10

sse_values = []
silhouette_scores = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(features_scaled)
    sse_values.append(kmeans.inertia_)
    labels = kmeans.labels_
    sil_score = silhouette_score(features_scaled, labels)
    silhouette_scores.append(sil_score)

# Método del codo
plt.figure(figsize=(11, 4))

plt.subplot(1, 2, 1)
plt.plot(K_range, sse_values, marker='o')
plt.title('Método del Codo (Inercia)')
plt.xlabel('Número de Clusters K')
plt.ylabel('SSE')

plt.grid(True)

plt.tight_layout()
plt.show()

#El punto optimo es k = 5

"""**Implementacion de DBSCAN**"""

#Configuracion Inicial
dbscan = DBSCAN(eps=1.0, min_samples=5)

dbscan.fit(features_scaled)

# Etiquetas de cluster
db_labels = dbscan.labels_

# Calcular número de clusters (sin contar el ruido)
n_clusters = len(set(db_labels)) - (1 if -1 in db_labels else 0)

# Calcular número de puntos de ruido
n_noise = list(db_labels).count(-1)

# Calcular coeficiente de silueta si hay al menos 2 clusters
if n_clusters > 1:
    sil_score = silhouette_score(features_scaled , db_labels)
else:
    sil_score = np.nan  # No se puede calcular si todos están en un solo grupo o todos son ruido

# Mostrar resultados
print(f"Número de clusters (sin contar ruido): {n_clusters}")
print(f"Número de puntos de ruido: {n_noise}")
print(f"Coeficiente de silueta: {sil_score if not np.isnan(sil_score) else 'No aplicable'}")

#Ocupamos distintos datos para comprobar el "esp" y "min_samples" mas apropiados
eps_values = [0.2, 0.3,0.4, 0.5, 0.6, 0.7,0.8 , 0.9, 1.0]
min_samples_values = [1,2,3,4,5,6,7,8,9,10]

best_result = {"eps": None, "min_samples": None, "silhouette": -1, "n_clusters": 0, "n_noise": 0}

for eps in eps_values:
    for min_samples in min_samples_values:
        db = DBSCAN(eps=eps, min_samples=min_samples)
        labels = db.fit_predict(features_scaled)

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)

        if n_clusters > 1:
            sil = silhouette_score(features_scaled, labels)
            print(f"eps={eps}, min_samples={min_samples} --> Clusters: {n_clusters}, Ruido: {n_noise}, Silueta: {sil:.4f}")

            # Guardar mejor configuración
            if sil > best_result["silhouette"]:
                best_result.update({
                    "eps": eps,
                    "min_samples": min_samples,
                    "silhouette": sil,
                    "n_clusters": n_clusters,
                    "n_noise": n_noise
                })
        else:
            print(f"eps={eps}, min_samples={min_samples} --> Clusters: {n_clusters}, Ruido: {n_noise}, Silueta: N/A")

print("\nMejor configuración encontrada:")
print(best_result)

#Probamos el nuevo resultado

#Configuracion con los resultados obtenidos
dbscan = DBSCAN(eps=1.0, min_samples=2)

dbscan.fit(features_scaled)

# Etiquetas de cluster
db_labels = dbscan.labels_

# Calcular número de clusters (sin contar el ruido)
n_clusters = len(set(db_labels)) - (1 if -1 in db_labels else 0)

# Calcular número de puntos de ruido
n_noise = list(db_labels).count(-1)

# Calcular coeficiente de silueta si hay al menos 2 clusters
if n_clusters > 1:
    sil_score = silhouette_score(features_scaled , db_labels)
else:
    sil_score = np.nan  # No se puede calcular si todos están en un solo grupo o todos son ruido

# Mostrar resultados
print(f"Número de clusters (sin contar ruido): {n_clusters}")
print(f"Número de puntos de ruido: {n_noise}")
print(f"Coeficiente de silueta: {sil_score if not np.isnan(sil_score) else 'No aplicable'}")

"""**Visualizacion y analisis de resultados**"""

# Ejes para graficar
x = features_scaled['Quantity']
y = features_scaled['TotalPrice']

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.scatter(x, y, c=labels, cmap='viridis', alpha=0.6, edgecolors='k')
plt.title('Clusters con K-Means')
plt.xlabel('Quantity')
plt.ylabel('TotalPrice')

plt.subplot(1, 2, 2)
plt.scatter(x, y, c=db_labels, cmap='plasma', alpha=0.6, edgecolors='k')
plt.title('Clusters con DBSCAN')
plt.xlabel('Quantity')
plt.ylabel('TotalPrice')

plt.show()

"""# Parte 2: Reglas de asociacion en python

**Preparacion de los datos para apriori**
"""

#Cargamos los datos nuevamente
data = pd.read_csv('/content/drive/MyDrive/clases/universidad/semestre 6/Mineria de datos/online_retail_II_sample_5000.csv')

#Obtenemos un dataseet de Invoice y Description
df_clean = df.dropna(subset=['Invoice', 'Description'])

#Agrupamos por factura e ítem y sumamos las cantidades
basket = (
    df_clean.groupby(['Invoice', 'Description'])['Quantity']
    .sum().unstack().reset_index().fillna(0)
    .set_index('Invoice')
)

#Convertimos las cantidades a presencia binaria (1 si hay, 0 si no hay)
basket_bin = basket.map(lambda x: 1 if x > 0 else 0)

# Filtrado: solo productos en al menos el 0.1% de las transacciones
min_support = 0.001 * len(basket_bin)
item_counts = basket_bin.sum(axis=0)
frequent_items = item_counts[item_counts >= min_support].index
basket_filtered = basket_bin[frequent_items]

# Mostrar dimensiones del resultado
print("Transacciones:", basket_filtered.shape[0])
print("Productos después del filtrado:", basket_filtered.shape[1])

#Probamos la matriz
basket_filtered.head(20).style.set_properties(**{'text-align': 'center'})

"""**Aplicacion de algoritmo apriori**"""

# Usamos un soporte minimo del 1 % para encontrar los mas frecuentes
frequent_itemsets = apriori(basket_filtered, min_support = 0.01, use_colnames=True)

# Mostrar ítems frecuentes encontrados
print("Ítems frecuentes:")
print(frequent_itemsets.head(20))

#No hay resultados

# Generar reglas de asociación con confianza mínima de 0.5
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

# Mostrar reglas sin filtrar por elevación
print("Reglas generadas:")
print(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(10))

#Dado a que no hay valores que cubren el 1% , no hay valores que mostrar

"""**Parametros para optimizacion**"""

supports = [0.005, 0.01, 0.015, 0.02]
confidences = [0.3, 0.5, 0.7, 0.8]

results = []

for support in supports:
    frequent_itemsets = apriori(basket_filtered, min_support=support, use_colnames=True)

    if frequent_itemsets.empty:
        continue  # Saltar si no se encuentran ítems frecuentes

    for confidence in confidences:
        try:
            rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=confidence)
            rules_filtered = rules[rules['lift'] > 1.0]
            results.append({
                'support': support,
                'confidence': confidence,
                'num_rules': len(rules_filtered)
            })
        except ValueError:
            # Si no se pueden generar reglas, continuar
            continue

# Mostrar resumen en tabla
results_df = pd.DataFrame(results)
print("\nResumen de reglas generadas:")
print(results_df.pivot(index='support', columns='confidence', values='num_rules'))

# Generar ítems frecuentes con soporte muy bajo (0.0002 = 0.02%)
frequent_itemsets = apriori(basket_filtered, min_support=0.0002, use_colnames=True)

# Generar reglas con confianza mínima de 0.2
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.2)

# Mostrar columnas clave
rules_top = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(10)
print("Top 10 reglas de asociación con soporte bajo:")
print(rules_top)

# Aplicar KMeans a la matriz de transacciones
n_clusters = 3
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
clusters = kmeans.fit_predict(basket_filtered)

# Añadir etiquetas de clúster al dataframe
basket_clustered = basket_filtered.copy()
basket_clustered['Cluster'] = clusters

# Ver tamaño de cada clúster
print("Transacciones por clúster:")
print(basket_clustered['Cluster'].value_counts())

# Reglas por clúster
for cluster_id in range(n_clusters):
    print(f"\n--- Reglas para clúster {cluster_id} ---")
    cluster_data = basket_clustered[basket_clustered['Cluster'] == cluster_id].drop(columns='Cluster')

    # Apriori con soporte bajo
    freq_items = apriori(cluster_data, min_support=0.002, use_colnames=True)
    if not freq_items.empty:
        rules = association_rules(freq_items, metric="confidence", min_threshold=0.2)
        rules = rules.sort_values(by='lift', ascending=False)
        display_rules = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head(5)
        print(display_rules)
    else:
        print("No se encontraron reglas para este clúster.")
