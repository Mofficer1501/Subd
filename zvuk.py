import librosa
import soundfile as sf
import numpy as np
'''import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical'''
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, utils
import os
import argparse
from tqdm import tqdm

def extract_audio(file_path):
  """Извлекает аудио из видеофайла или возвращает путь к аудиофайлу."""
  if file_path.lower().endswith(('.mp3', '.wav')):
    return file_path
  else:
    try:
      audio_data, sr = librosa.load(file_path)
      return audio_data, sr
    except:
      print(f"Ошибка при извлечении аудио из {file_path}")
      return None

def split_audio(audio_data, sr, frame_size=2048, hop_length=1024):
  """Разделяет аудио на фрагменты."""
  frames = librosa.util.frame(audio_data, frame_length=frame_size, hop_length=hop_length)
  return frames, sr

def create_dataset(audio_dir, labels_file):
  """Создает набор данных для обучения модели."""
  labels = {}
  with open(labels_file, 'r') as f:
    for line in f:
      file_name, start_time, end_time = line.strip().split(',')
      if file_name not in labels:
        labels[file_name] = []
      labels[file_name].append((float(start_time), float(end_time)))

  X = []
  y = []

  for file_name in tqdm(os.listdir(audio_dir)):
    if not file_name.lower().endswith(('.mp3', '.wav', '.mp4', '.avi')):
      continue
    file_path = os.path.join(audio_dir, file_name)
    audio_data, sr = extract_audio(file_path)

    if audio_data is None:
      continue

    frames, sr = split_audio(audio_data, sr)

    for i, frame in enumerate(frames):
      if file_name in labels:
        for start_time, end_time in labels[file_name]:
          # Проверка, находится ли кадр в интервале уведомления
          if i * sr / frames.shape[1] >= start_time and i * sr / frames.shape[1] <= end_time:
            X.append(frame)
            y.append(1)
            break
        else:
          X.append(frame)
          y.append(0)
      else:
        X.append(frame)
        y.append(0)

  return np.array(X), np.array(y)

def create_model(input_shape):
  """Создает модель нейронной сети."""
  model = Sequential()
  model.add(Conv1D(filters=32, kernel_size=5, activation='relu', input_shape=input_shape))
  model.add(MaxPooling1D(pool_size=2))
  model.add(Conv1D(filters=64, kernel_size=5, activation='relu'))
  model.add(MaxPooling1D(pool_size=2))
  model.add(Flatten())
  model.add(Dense(128, activation='relu'))
  model.add(Dense(2, activation='softmax'))
  model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
  return model

def train_model(X, y, epochs=10):
  """Обучает модель."""
  X = X.reshape(X.shape[0], X.shape[1], 1)
  y = to_categorical(y, num_classes=2)
  model = create_model(X.shape[1:])
  model.fit(X, y, epochs=epochs)
  return model

def detect_notifications(audio_data, sr, model, frame_size=2048, hop_length=1024, threshold=0.8):
  """Обнаруживает звуки уведомлений."""
  frames, sr = split_audio(audio_data, sr, frame_size, hop_length)
  frames = frames.reshape(frames.shape[0], frames.shape[1], 1)
  predictions = model.predict(frames)
  notification_intervals = []
  start_time = None
  for i, prediction in enumerate(predictions):
    if prediction[1] > threshold:
      if start_time is None:
        start_time = i * sr / frames.shape[1]
    else:
      if start_time is not None:
        end_time = i * sr / frames.shape[1]
        notification_intervals.append((start_time, end_time))
        start_time = None
  return notification_intervals

def remove_notifications(audio_data, sr, notification_intervals):
  """Удаляет звуки уведомлений из аудио."""
  audio_without_notifications = audio_data.copy()
  for start_time, end_time in notification_intervals:
    start_sample = int(start_time * sr)
    end_sample = int(end_time * sr)
    audio_without_notifications[start_sample:end_sample] = np.zeros(end_sample - start_sample)
  return audio_without_notifications

def save_audio(audio_data, sr, file_path):
  """Сохраняет аудио."""
  sf.write(file_path, audio_data, sr)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--audio_dir', help='Путь к папке с аудиофайлами', required=True)
  parser.add_argument('--labels_file', help='Путь к файлу с метками', required=True)
  parser.add_argument('--mode', choices=['train', 'detect', 'remove'], help='Режим работы (train, detect, remove)', required=True)
  parser.add_argument('--output_file', help='Путь к выходному файлу (для режима remove)', default=None)
  args = parser.parse_args()

  if args.mode == 'train':
    X, y = create_dataset(args.audio_dir, args.labels_file)
    model = train_model(X, y)
    model.save('notification_detection_model.h5')
  elif args.mode == 'detect':
    model = tf.keras.models.load_model('notification_detection_model.h5')
    for file_name in tqdm(os.listdir(args.audio_dir)):
      if not file_name.lower().endswith(('.mp3', '.wav', '.mp4', '.avi')):
        continue
      file_path = os.path.join(args.audio_dir, file_name)
      audio_data, sr = extract_audio(file_path)
      if audio_data is None:
        continue
      notification_intervals = detect_notifications(audio_data, sr, model)
      print(f"Файл: {file_name}, Интервалы уведомлений: {notification_intervals}")
  elif args.mode == 'remove':
    model = tf.keras.models.load_model('notification_detection_model.h5')
    for file_name in tqdm(os.listdir(args.audio_dir)):
      if not file_name.lower().endswith(('.mp3', '.wav', '.mp4', '.avi')):
        continue
      file_path = os.path.join(args.audio_dir, file_name)
      audio_data, sr = extract_audio(file_path)
      if audio_data is None:
        continue
      notification_intervals = detect_notifications(audio_data, sr, model)
      audio_without_notifications = remove_notifications(audio_data, sr, notification_intervals)
      output_file_path = os.path.join(args.output_file, file_name)
      save_audio(audio_without_notifications, sr, output_file_path)

if __name__ == '__main__':
  main()
