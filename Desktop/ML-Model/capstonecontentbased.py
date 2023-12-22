# -*- coding: utf-8 -*-
"""CapstoneContentBased.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13xYmS6y2cfmM7UBRBxNJSsdflPzEe7wF
"""

import pandas as pd
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Flatten, Dense
from tensorflow.keras.models import Model
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load dataset
umkm = pd.read_csv('umkm_dataset.csv', sep=';')

# Drop missing values
umkm_clean = umkm.dropna()

# Combine relevant information into 'Deskripsi_Produk'
umkm_clean['Deskripsi_Produk'] = umkm_clean['Merk Produk'] + ' - ' + umkm_clean['Jenis Produk'] + ' - ' + umkm_clean['Jenis Produk2']
umkm_clean

# Menghitung vektor TF-IDF untuk deskripsi produk
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(umkm_clean['Deskripsi_Produk'])

# Melihat feature names (kata-kata) dari vektor TF-IDF
feature_names = tfidf_vectorizer.get_feature_names_out()

# Menampilkan hasil
print("TF-IDF Matrix Shape:", tfidf_matrix.shape)
print("Feature Names:", feature_names)

# Menghitung similarity score menggunakan dot product dari matriks TF-IDF
cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

# Menampilkan hasil
print("Cosine Similarities Shape:", cosine_similarities.shape)
print("Cosine Similarities Matrix:")
print(cosine_similarities)

# Tampilkan kolom 'Jenis Produk' dari dataset
print("Jenis Produk dalam Dataset:")
print(umkm_clean['Jenis Produk'].unique())

# Contoh menggunakan LabelEncoder yang sudah didefinisikan sebelumnya
label_encoder = LabelEncoder()

# Melakukan encoding
encoded_values = label_encoder.fit_transform(umkm_clean['Jenis Produk'].unique())

# Menampilkan mapping antara jenis produk dan nilai encode
mapping = dict(zip(encoded_values, umkm_clean['Jenis Produk'].unique()))
print("\nMapping Encode ke Jenis Produk:")
print(mapping)

# Menampilkan jenis produk untuk setiap nomor encode
for encode, jenis_produk in mapping.items():
    print(f"Encode {encode} -> Jenis Produk: {jenis_produk}")

# Split data menjadi train dan test
train_data, test_data = train_test_split(umkm_clean, test_size=0.2, random_state=42)

# X_train dan X_test berisi deskripsi produk
X_train = train_data['Deskripsi_Produk']
X_test = test_data['Deskripsi_Produk']

# Y_train dan Y_test berisi jenis produk
Y_train = train_data['Jenis Produk']
Y_test = test_data['Jenis Produk']

# Label encoding untuk jenis produk
label_encoder = LabelEncoder()
Y_train_encoded = label_encoder.fit_transform(Y_train)
Y_test_encoded = label_encoder.transform(Y_test)

# Tampilkan hasil label encoding
print("Encoded Labels (Y_train):")
print(Y_train_encoded)
print("\nEncoded Labels (Y_test):")
print(Y_test_encoded)

# Tokenization
tokenizer = Tokenizer()
tokenizer.fit_on_texts(X_train)

X_train_sequences = tokenizer.texts_to_sequences(X_train)
X_test_sequences = tokenizer.texts_to_sequences(X_test)

# Padding sequences to have consistent length
X_train_padded = pad_sequences(X_train_sequences)
X_test_padded = pad_sequences(X_test_sequences, maxlen=X_train_padded.shape[1])

# Define model
input_layer = Input(shape=(X_train_padded.shape[1],))
embedding_layer = Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=50)(input_layer)
flatten_layer = Flatten()(embedding_layer)
dense_layer = Dense(128, activation='relu')(flatten_layer)
output_layer = Dense(len(label_encoder.classes_), activation='softmax')(dense_layer)

content_based_model = Model(inputs=input_layer, outputs=output_layer)
content_based_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
content_based_model.fit(X_train_padded, Y_train_encoded, epochs=35, batch_size=32, validation_data=(X_test_padded, Y_test_encoded))

# Cetak ringkasan model
print(content_based_model.summary())

# Dapatkan model dan tokenizer yang sudah di-train
trained_model = content_based_model  # Ganti dengan model content-based yang sudah di-train
trained_tokenizer = tfidf_vectorizer  # Ganti dengan tokenizer yang sudah di-train

def get_recommendations_by_products(product_type, model, tokenizer, label_encoder, df=umkm_clean):
    # Konversi input ke huruf kecil
    product_type = product_type.lower()

    # Cek apakah input ada dalam kolom 'Jenis Produk' atau 'Jenis Produk2'
    filter_condition = (df['Jenis Produk'].str.lower().str.contains(product_type)) | (df['Jenis Produk2'].str.lower().str.contains(product_type))
    if not any(filter_condition):
        print(f"Tidak ditemukan produk dengan jenis {product_type}")
        return pd.DataFrame()

    # Ambil indeks produk dengan jenis produk yang sesuai (case-insensitive)
    product_indices = df[filter_condition].index.tolist()

    # Acak indeks produk yang sesuai dengan jenis produk
    random.shuffle(product_indices)

    # Ambil 5 produk dengan indeks yang telah diacak
    product_indices = product_indices[:5]

    # Buat DataFrame hasil rekomendasi
    recommendations_df = df.loc[product_indices, ['Alamat', 'Provinsi', 'Jenis Produk', 'Jenis Produk2', 'Deskripsi_Produk', 'Nomor Telepon / Faksimili']]

    return recommendations_df

product_type = 'roti'
recommendations_df = get_recommendations_by_products(product_type, content_based_model, tokenizer, label_encoder)
print(f"\nRekomendasi untuk Jenis Produk: {product_type}")
recommendations_df
