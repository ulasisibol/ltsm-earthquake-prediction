# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1elfIRHrmtyfbyp5a4Ll-7kQcGDcPs3MG
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Conv1D, MaxPooling1D, Flatten
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Veri setini yükleme ve ön işlemler
data = pd.read_csv('query3.csv')
data['time'] = pd.to_datetime(data['time'])
data['rms'] = data['rms'].fillna(data['rms'].median())
columns_to_drop = ['magType', 'nst', 'gap', 'dmin', 'rms', 'updated', 'place', 'type', 'horizontalError', 'depthError', 'magError', 'magNst', 'status', 'locationSource', 'magSource']
data = data.drop(columns=columns_to_drop)

data.head()

# Özellik mühendisliği uygulaması
data['rolling_mag_avg'] = data['mag'].rolling(window=3).mean().shift(1)
data.fillna(method='bfill', inplace=True)  # Başlangıçta NaN değerleri doldurmak için

# Eğitim ve test setlerine bölme
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# Özellikler ve hedef değişkenleri ayırma
features = train_data[['latitude', 'longitude', 'depth', 'rolling_mag_avg']]
target = train_data['mag']
test_features = test_data[['latitude', 'longitude', 'depth', 'rolling_mag_avg']]
test_target = test_data['mag']

# İki farklı scaler kullanımı
feature_scaler = MinMaxScaler(feature_range=(0, 1))
target_scaler = MinMaxScaler(feature_range=(0, 1))

# Eğitim ve test verilerini normalleştirme
features_scaled = feature_scaler.fit_transform(features)
target_scaled = target_scaler.fit_transform(np.array(target).reshape(-1, 1))
test_features_scaled = feature_scaler.transform(test_features)
test_target_scaled = target_scaler.transform(np.array(test_target).reshape(-1, 1))

# LSTM modelini kurma ve eğitme
model = Sequential()
model.add(LSTM(100, activation='relu', input_shape=(features_scaled.shape[1], 1), return_sequences=True))
model.add(LSTM(50, activation='relu', return_sequences=False))
model.add(Dense(1))
model.compile(optimizer='adam', loss='mean_squared_error')
X_train = features_scaled.reshape((features_scaled.shape[0], features_scaled.shape[1], 1))
y_train = target_scaled
history = model.fit(X_train, y_train, epochs=200, batch_size=64, validation_split=0.1)

# Tahmin ve hata metriklerini hesaplama
X_test = test_features_scaled.reshape((test_features_scaled.shape[0], test_features_scaled.shape[1], 1))
predictions_scaled = model.predict(X_test)
predictions = target_scaler.inverse_transform(predictions_scaled)
actuals = target_scaler.inverse_transform(test_target_scaled)
mse = mean_squared_error(actuals, predictions)
print(f'Mean Squared Error: {mse}')

# Gerçek değerler ve tahminleri grafik üzerinde gösterme
plt.figure(figsize=(10, 6))
plt.plot(actuals, label='Actual Magnitudes')
plt.plot(predictions, label='Predicted Magnitudes')
plt.title('Comparison of Actual and Predicted Earthquake Magnitudes')
plt.xlabel('Sample Index')
plt.ylabel('Magnitude')
plt.legend()
plt.show()

# Hataların hesaplanması
errors = actuals - predictions

# Hata dağılımını histogram olarak gösterme
plt.figure(figsize=(10, 6))
plt.hist(errors, bins=30, alpha=0.7, color='red')
plt.title('Distribution of Prediction Errors')
plt.xlabel('Prediction Error')
plt.ylabel('Frequency')
plt.show()

future_data = data[['latitude', 'longitude', 'depth', 'rolling_mag_avg']].copy()

# Modeli test etmek için bir gelecek senaryosu hazırlama
average_rolling_mag = data['rolling_mag_avg'].mean()
future_data['rolling_mag_avg'] = average_rolling_mag

# Özellikleri ölçeklendirme
future_features_scaled = feature_scaler.transform(future_data)

# Gerekirse veriyi modelin beklediği forma sokma
X_future = future_features_scaled.reshape((future_features_scaled.shape[0], future_features_scaled.shape[1], 1))

# Modelden tahmin yapma
future_predictions_scaled = model.predict(X_future)

# Tahminleri orijinal ölçeğe dönüştürme
future_predictions = target_scaler.inverse_transform(future_predictions_scaled)

# Tahminleri görselleştirme
plt.figure(figsize=(10, 6))
plt.plot(future_predictions, label='Predicted Future Magnitudes')
plt.title('Predicted Future Earthquake Magnitudes')
plt.xlabel('Sample Index')
plt.ylabel('Magnitude')
plt.legend()
plt.show()