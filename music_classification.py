# -*- coding: utf-8 -*-
"""music_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xT4UVH9xkJ8snRnPYbvmprP9_zUQcKGz
"""

import json
import os
import math
import librosa

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import tensorflow.keras as keras
import matplotlib.pyplot as plt
import seaborn

"""# Pre Process Data"""
data_dir_path = 'drive/MyDrive/cs615_data/genres/'
data_json_path = 'drive/MyDrive/cs615_data/data.json'
sample_rate = 22050
track_duration = 30 #s
samples_per_track = sample_rate * track_duration

# preprocess data
def save_mfcc(dataset_path, json_path, num_mfcc=13, n_fft=2048, hop_length=512, num_segments=5):
  # we only have a 100 track per genre which is not a lot so we need 
  # to split up the data so we can have more than 100 per genre

  # dict to store data
  data = {
      'genres': [],
      'x': [],
      'y': []
  } 

  samples_per_seg = int(samples_per_track / num_segments)
  num_mfcc_vectors_per_seg = math.ceil(samples_per_seg / hop_length)


  # loop through all of the genres
  for dir_path, dir_name, fl_names in os.walk(data_dir_path):
    
    genre_name = dir_path.split('/')[-1]
    if not genre_name:
      continue

    data['genres'].append(genre_name)
    print("Processing", genre_name)

    for f in fl_names:
      fl_path = os.path.join(dir_path, f)
      signal, sr = librosa.load(fl_path, sr=sample_rate)

      # extract mfcc and store datsa
      for s in range(num_segments):
        start_sample = samples_per_seg * s
        end_sample = start_sample + samples_per_seg

        mfcc = librosa.feature.mfcc(signal[start_sample:end_sample],
                                    sr=sr,
                                    n_mfcc=num_mfcc,
                                    n_fft=n_fft,
                                    hop_length = hop_length)
        mfcc = mfcc.T
        
        # store mfcc for seg if it has the expected len
        if len(mfcc) == num_mfcc_vectors_per_seg:
          data['x'].append(mfcc.tolist())
          data['y'].append(data['genres'].index(genre_name))
          # print(fl_path, s)

  with open(json_path, "w") as fp:
    json.dump(data, fp, indent=4)


"""# Visualize Data"""
def visualize():
  import librosa, librosa.display
  data_dir_path = 'drive/MyDrive/cs615_data/genres/'

  for dir_path, dir_name, fl_names in os.walk(data_dir_path):
    genre_name = dir_path.split('/')[-1]
    if not genre_name:
      continue

    print(genre_name)
    fl_path = os.path.join(dir_path, fl_names[i])
    signal, sr = librosa.load(fl_path, sr=22050)

    # WAVEFORM
    # display waveform
    plt.figure(figsize=(15,10))
    librosa.display.waveplot(signal, sr, alpha=0.4)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Waveform")
    plt.show()

    # MFCCs
    # extract 13 MFCCs
    hop_length = 512 # in num. of samples
    n_fft = 2048 # window in num. of samples
    MFCCs = librosa.feature.mfcc(signal, sr, n_fft=n_fft, hop_length=hop_length, n_mfcc=13)

    # display MFCCs
    plt.figure(figsize=(15,10))
    librosa.display.specshow(MFCCs, sr=sr, hop_length=hop_length)
    plt.xlabel("Time")
    plt.ylabel("MFCC coefficients")
    plt.colorbar()
    plt.title("MFCCs")

    # show plots
    plt.show()


"""# General"""
def load_data(dataset_path):
  with open(dataset_path, 'r') as f:
    data = json.load(f)

    # convert lists to numpy arrays
    inputs = np.array(data['x'])
    targets = np.array(data['y'])

    return inputs, targets

def plot_history(history):  
  # create accuracy subplot
  plt.plot(history.history['accuracy'], label="train accuracy")
  plt.plot(history.history['val_accuracy'], label="test accuracy")
  plt.ylabel("Accuracy")
  plt.xlabel("Epoch")
  plt.legend(loc="lower right")
  plt.title("Accuracy eval")
  plt.show()

  # create loss subplot
  plt.plot(history.history['loss'], label="train error")
  plt.plot(history.history['val_loss'], label="test error")
  plt.ylabel("Error")
  plt.xlabel("Epoch")
  plt.legend(loc="upper right")
  plt.title("Error eval")
  plt.show()

def plot_confusion_matrix(model, x, y):
  layers = [ "reggae", "pop", "country", "blues", "disco", "rock", "hiphop", 
            "jazz", "classical", "metal" ]
  soft_out = model.predict(x)
  y_hat = np.argmax(soft_out, axis=1)

  print(y)
  mat = confusion_matrix(y, y_hat)

  seaborn.set(color_codes=True)
  plt.figure(1, figsize=(9, 6))

  plt.title("Confusion Matrix")

  seaborn.set(font_scale=1.4)
  ax = seaborn.heatmap(mat, annot=True, cmap="YlGnBu", cbar_kws={'label': 'Scale'})

  ax.set_xticklabels(labels)
  ax.set_yticklabels(labels)

  ax.set(ylabel="True Label", xlabel="Predicted Label")

  # plt.savefig(output_filename, bbox_inches='tight', dpi=300)
  plt.close()

def predict(model, x, y):
  y_hat = model.predict(x)

  # get the index where we have the max value
  y_hat = np.argmax(y_hat, axis=1)
  print(np.sum(y == y_hat), len(y_hat))


"""# MLP"""
def audio_classification_mlp(inputs, targets):
  # split the data into train and test
  x_train, x_test, y_train, y_test = train_test_split(inputs, targets, 
                                                      test_size=0.3)

  # build the network architecture
  model = keras.Sequential([
    # input layer
    keras.layers.Flatten(input_shape=(inputs.shape[1], inputs.shape[2])),
    
    # 1st hidden layer
    keras.layers.Dense(512, activation='relu'),
    
    # 2nd hidden layer
    keras.layers.Dense(256, activation='relu'),
    
    # 3rd hidden layer
    keras.layers.Dense(64, activation='relu'),

    # output layer
    keras.layers.Dense(10, activation='softmax')
  ])

  # compile network
  optimizer = keras.optimizers.Adam(learning_rate=.0001)
  model.compile(optimizer, loss='sparse_categorical_crossentropy', 
                metrics=['accuracy'])
  model.summary()

  # train network
  history = model.fit(x_train, y_train, 
            validation_data=(x_test, y_test),
            epochs=50,
            batch_size=32)
  
  # plot the confusion matrix
  # plot_confusion_matrix(model, x_test, y_test)
  
  # plot the accuracy and error over epochs
  plot_history(history)
def audio_classification_mlp_dropouts(inputs, targets, dropout=.3):
  # split the data into train and test
  x_train, x_test, y_train, y_test = train_test_split(inputs, targets, 
                                                      test_size=0.3)

  # build the network architecture
  model = keras.Sequential([
    # input layer
    keras.layers.Flatten(input_shape=(inputs.shape[1], inputs.shape[2])),
    
    # 1st hidden layer
    keras.layers.Dense(512, activation='relu',  kernel_regularizer=keras.regularizers.l2(.001)),
    keras.layers.Dropout(dropout),

    # 2nd hidden layer
    keras.layers.Dense(256, activation='relu',  kernel_regularizer=keras.regularizers.l2(.001)),
    keras.layers.Dropout(dropout),

    # 3rd hidden layer
    keras.layers.Dense(64, activation='relu',  kernel_regularizer=keras.regularizers.l2(.001)),
    keras.layers.Dropout(dropout),

    # output layer
    keras.layers.Dense(10, activation='softmax')
  ])

  # compile network
  optimizer = keras.optimizers.Adam(learning_rate=.0001)
  model.compile(optimizer, loss='sparse_categorical_crossentropy', 
                metrics=['accuracy'])
  model.summary()

  # train network
  history = model.fit(x_train, y_train, 
            validation_data=(x_test, y_test),
            epochs=50,
            batch_size=32)
  
  # eval the cnn on test set
  test_error, test_accuracy = model.evaluate(x_test, y_test, verbose=1)
  print('Accuracy on the test set is', test_accuracy, 'Error:', test_error)

  # plot the accuracy and error over epochs
  plot_history(history)


"""# mlp - 5"""
def audio_classification_mlp5_dropouts(inputs, targets, dropout=.3):
  # split the data into train and test
  x_train, x_test, y_train, y_test = train_test_split(inputs, targets, 
                                                      test_size=0.3)

  # build the network architecture
  model = keras.Sequential([
    # input layer
    keras.layers.Flatten(input_shape=(inputs.shape[1], inputs.shape[2])),
    
    # 1st hidden layer
    keras.layers.Dense(800, activation='relu',  kernel_regularizer=keras.regularizers.l2(.001)),
    keras.layers.Dropout(dropout),

    # 2nd hidden layer
    keras.layers.Dense(400, activation='relu',  kernel_regularizer=keras.regularizers.l2(.001)),
    keras.layers.Dropout(dropout),

    # 3rd hidden layer
    keras.layers.Dense(200, activation='relu',  kernel_regularizer=keras.regularizers.l2(.001)),
    keras.layers.Dropout(dropout),

    # 3rd hidden layer
    keras.layers.Dense(100, activation='relu',  kernel_regularizer=keras.regularizers.l2(.001)),
    keras.layers.Dropout(dropout),

    # 3rd hidden layer
    keras.layers.Dense(50, activation='relu',  kernel_regularizer=keras.regularizers.l2(.001)),
    keras.layers.Dropout(dropout),

    # output layer
    keras.layers.Dense(10, activation='softmax')
  ])

  # compile network
  optimizer = keras.optimizers.Adam(learning_rate=.0001)
  model.compile(optimizer, loss='sparse_categorical_crossentropy', 
                metrics=['accuracy'])
  model.summary()

  # train network
  history = model.fit(x_train, y_train, 
            validation_data=(x_test, y_test),
            epochs=50,
            batch_size=32)
  
  # eval the cnn on test set
  test_error, test_accuracy = model.evaluate(x_test, y_test, verbose=1)
  print('Accuracy on the test set is', test_accuracy, 'Error:', test_error)

  # plot the accuracy and error over epochs
  plot_history(history)


"""# MPL - 1"""
def audio_classification_mlp1_dropouts(inputs, targets, dropout=.3):
  # split the data into train and test
  x_train, x_test, y_train, y_test = train_test_split(inputs, targets, 
                                                      test_size=0.3)

  # build the network architecture
  model = keras.Sequential([
    # input layer
    keras.layers.Flatten(input_shape=(inputs.shape[1], inputs.shape[2])),
    
    # 1st hidden layer
    keras.layers.Dense(528, activation='relu',  kernel_regularizer=keras.regularizers.l2(.001)),
    keras.layers.Dropout(dropout),

    # output layer
    keras.layers.Dense(10, activation='softmax')
  ])

  # compile network
  optimizer = keras.optimizers.Adam(learning_rate=.0001)
  model.compile(optimizer, loss='sparse_categorical_crossentropy', 
                metrics=['accuracy'])
  model.summary()

  # train network
  history = model.fit(x_train, y_train, 
            validation_data=(x_test, y_test),
            epochs=50,
            batch_size=32)
  
  # eval the cnn on test set
  test_error, test_accuracy = model.evaluate(x_test, y_test, verbose=1)
  print('Accuracy on the test set is', test_accuracy, 'Error:', test_error)

  # plot the accuracy and error over epochs
  plot_history(history)


"""# CNN"""
def prepare_datasets(x, y, test_size, val_size):
  # test_size - how much of the training set do we want for testing
  # val_size - how much of the train set do we want for validation

  # create train test split
  x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size)

  # create train validation split
  x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=val_size)

  x_train = x_train[..., np.newaxis]
  x_val = x_val[..., np.newaxis]
  x_test = x_test[..., np.newaxis]

  return x_train, x_val, x_test, y_train, y_val, y_test

def build_cnn_model(input_shape, dropout):
  # create the model
  model = keras.Sequential()

  # 1st conv layer
  model.add(keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
  model.add(keras.layers.MaxPool2D((3, 3), strides=(2, 2), padding='same'))
  model.add(keras.layers.BatchNormalization())

  # 2nd conv layer
  model.add(keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
  model.add(keras.layers.MaxPool2D((3, 3), strides=(2, 2), padding='same'))

  # 3rd conv layer
  model.add(keras.layers.Conv2D(32, (2, 2), activation='relu', input_shape=input_shape))
  model.add(keras.layers.MaxPool2D((2, 2), strides=(2, 2), padding='same'))

  # flatten the output and feed into the dense layer
  model.add(keras.layers.Flatten())
  model.add(keras.layers.Dense(64, activation='relu'))
  model.add(keras.layers.Dropout(dropout))

  # output layer
  model.add(keras.layers.Dense(10, activation='softmax'))

  model.summary()

  return model

def audio_classification_cnn(x, y, dropout=0.3):
  # create train, validation and test sets
  x_train, x_val, x_test, y_train, y_val, y_test = prepare_datasets(x, y, .25, .2)

  # build cnn network
  input_shape = (x_train.shape[1], x_train.shape[2], x_train.shape[3])
  model = build_cnn_model(input_shape, dropout)

  # compile cnn
  opt = keras.optimizers.Adam(learning_rate=.001)
  model.compile(optimizer=opt, loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

  # train the cnn
  history = model.fit(x_train, y_train, validation_data=(x_val, y_val), batch_size=32, 
            epochs=30)

  # eval the cnn on test set
  test_error, test_accuracy = model.evaluate(x_test, y_test, verbose=1)
  print('Accuracy on the test set is', test_accuracy, "Error:", test_error)

  # make predistions on model
  # x = x_test(100)
  # y = y_test(100)

  # plot the accuracy and error over epochs
  plot_history(history)

  predict(model, x_test, y_test)
  return test_error, test_accuracy


"""# RNN"""
def prepare_rnn_datasets(x, y, test_size, val_size):
  # test_size - how much of the training set do we want for testing
  # val_size - how much of the train set do we want for validation

  # create train test and validation split
  x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size)
  x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=val_size)

  return x_train, x_val, x_test, y_train, y_val, y_test

def build_rnn_lstm_model(input_shape, dropout):
  model = keras.Sequential()

  # 2 LSTM Layers
  model.add(keras.layers.LSTM(64, input_shape=input_shape, return_sequences=True))
  model.add(keras.layers.LSTM(64))

  # dense layer
  model.add(keras.layers.Dense(64, activation='relu'))
  model.add(keras.layers.Dropout(dropout))

  # output layer
  model.add(keras.layers.Dense(10, activation='softmax'))

  return model

def audio_classification_rnn_lstm(x, y, dropout):
  # create train, validation and test sets
  x_train, x_val, x_test, y_train, y_val, y_test = prepare_rnn_datasets(x, y, .25, .2)

  # build cnn network
  input_shape = (x_train.shape[1], x_train.shape[2])
  model = build_rnn_lstm_model(input_shape, dropout)

  # compile cnn
  opt = keras.optimizers.Adam(learning_rate=.001)
  model.compile(optimizer=opt, loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])
  
  # model.summary()

  # train the rnn
  history = model.fit(x_train, y_train, validation_data=(x_val, y_val), batch_size=32, 
            epochs=30)
  
  # plot the history
  plot_history(history)

  # eval the rnn on test set
  test_error, test_accuracy = model.evaluate(x_test, y_test, verbose=1)
  print('Accuracy on the test set is', test_accuracy)

  # make predistions on model
  predict(model, x_test, y_test)

  return test_error, test_accuracy



# save_mfcc(data_dir_path, data_json_path, num_segments=10)

# # load data from saved file
# data_json_path = 'drive/MyDrive/cs615_data/data.json'
# inputs, targets = load_data(data_json_path)

# audio_classification_mlp(inputs, targets)

# drop = 0.1
# audio_classification_mlp_dropouts(inputs, targets, dropout=drop)
# audio_classification_mlp5_dropouts(inputs, targets, dropout=drop)
# audio_classification_mlp1_dropouts(inputs, targets, dropout=drop)
# audio_classification_cnn(inputs, targets, dropout=drop)
# audio_classification_rnn_lstm(inputs, targets, dropout=drop)

