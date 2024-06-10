# -*- coding: utf-8 -*-
"""Digit_Recognizer.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1k4qUn5pjnuUGw22s0pbrPI-dshJXWgQD

## Import Libraries
"""

import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
import os
import shutil
from google.colab import drive, files
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.applications import VGG16
from tensorflow.keras import regularizers

"""## Import Datasets"""

train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')

# Showing first 5 elements from train set
train.head()

# Showing first 5 elements from test set
test.head()

# Printing number of samples
print('Number of Train Sample: ', train.shape[0])
print('Number of Test Sample: ', test.shape[0])

"""## Preprocessing"""

# Preparing the target variable
Y_train = train["label"]

# Preparing the feature set
X_train = train.drop(labels = ["label"],axis = 1)

# Visualize distribution of target variable
sns.countplot(x=Y_train) # Bar plot
Y_train.value_counts() # Count of each class in y-axis

# Check missing values
print('Missing Values Train-set :',train.isnull().values.any())
print('Missing Values Test-set :',test.isnull().values.any())

# Data Normalization
X_train = X_train / 255.0
X_test = test / 255.0

# Data Reshape
X_train = X_train.values.reshape(-1,28,28,1)
X_test = X_test.values.reshape(-1,28,28,1)

# Encoding
Y_train = tf.keras.utils.to_categorical(Y_train, num_classes = 10)

# Data Splitting
X_train, X_val, Y_train, Y_val = train_test_split(X_train, Y_train, test_size=.1, random_state=7)

# Preview the first 30 images
plt.figure(figsize=(15,4.5))
for i in range(30):
    plt.subplot(3, 10, i+1)
    plt.imshow(X_train[i].reshape((28,28)),cmap=plt.cm.binary)
    plt.axis('off')
plt.subplots_adjust(wspace=-0.1, hspace=-0.1)
plt.show()

# Image augmentaion for better learning and performance of model
train_datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.05,
    height_shift_range=0.05,
    zoom_range=0.1,
)

train_datagen.fit(X_train)

# Preview 30 augmented images (10 augmented images for 3 original images in train set, each)
X_train3 = X_train[9,].reshape((1,28,28,1))
Y_train3 = Y_train[9,].reshape((1,10))
plt.figure(figsize=(15,4.5))
for i in range(30):
    plt.subplot(3, 10, i+1)
    X_train2, Y_train2 = train_datagen.flow(X_train3,Y_train3).next()
    plt.imshow(X_train2[0].reshape((28,28)),cmap=plt.cm.binary)
    plt.axis('off')
    if i==9: X_train3 = X_train[11,].reshape((1,28,28,1))
    if i==19: X_train3 = X_train[18,].reshape((1,28,28,1))
plt.subplots_adjust(wspace=-0.1, hspace=-0.1)
plt.show()

"""## Define Model Architecture"""

model = Sequential()

model.add(Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(28,28,1)))
model.add(BatchNormalization())
model.add(Conv2D(32, (3, 3), activation='relu', padding='same'))
model.add(BatchNormalization())
model.add(MaxPooling2D((2,2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(BatchNormalization())
model.add(Conv2D(128, (3, 3), activation='relu', padding='same', kernel_regularizer='l2'))
model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(BatchNormalization())
model.add(MaxPooling2D((2,2)))
model.add(Dropout(0.25))

model.add(Flatten())

model.add(Dense(256, activation='relu',kernel_regularizer=regularizers.l2(0.01)))
model.add(Dropout(0.4))
model.add(Dense(10, activation='softmax'))

"""## Model Compilation"""

early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(initial_learning_rate=0.001,decay_steps=10000,decay_rate=0.9,staircase=True)
optimizer = tf.keras.optimizers.Adam(learning_rate=lr_schedule)

model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

model.summary()

"""## Model Training"""

batch_size = 82
epochs = 50

history = model.fit(train_datagen.flow(X_train,Y_train, batch_size=batch_size),
                              epochs = epochs, validation_data = (X_val,Y_val),
                              verbose = 2, steps_per_epoch=X_train.shape[0] // batch_size
                              , callbacks=early_stop)

"""## Model Evaluation"""

results = np.zeros((X_test.shape[0],10))
results = results + model.predict(X_test)
results = np.argmax(results,axis = 1)
results = pd.Series(results,name="Label")
submission = pd.concat([pd.Series(range(1,28001),name = "ImageId"),results],axis = 1)
submission.to_csv("mnist_digit_recognizer.csv",index=False)

"""## Predictions"""

# Preview Predictions
plt.figure(figsize=(15,6))
for i in range(40):
    plt.subplot(4, 10, i+1)
    plt.imshow(X_test[i].reshape((28,28)),cmap=plt.cm.binary)
    plt.title("predict=%d" % results[i],y=0.9)
    plt.axis('off')
plt.subplots_adjust(wspace=0.3, hspace=-0.1)
plt.show()

model.save("model.h5")

# Evaluate the model
# test_loss, test_accuracy = model.evaluate(X_test, test, verbose=2)
# print(f"Test Loss: {test_loss}")
# print(f"Test Accuracy: {test_accuracy}")

# # Predict the labels for the test set
# predictions = model.predict(X_test)

# # Convert the predictions from one-hot encoded format to class labels
# predicted_labels = np.argmax(predictions, axis=1)

# # Convert the true labels from one-hot encoded format to class labels (if Y_test is one-hot encoded)
# true_labels = np.argmax(test, axis=1)

# # Calculate accuracy
# accuracy = accuracy_score(true_labels, predicted_labels)
# print(f"Computed Test Accuracy: {accuracy}")

# # Number of samples to visualize
# num_samples = 20

# # Plot the first 'num_samples' test images and their predicted labels
# plt.figure(figsize=(15, 6))
# for i in range(num_samples):
#     plt.subplot(2, num_samples // 2, i + 1)
#     plt.imshow(X_test[i].reshape(28, 28), cmap=plt.cm.binary)
#     plt.title(f"Pred: {predicted_labels[i]}")
#     plt.axis('off')
# plt.subplots_adjust(wspace=0.3, hspace=-0.1)
# plt.show()

"""### Testing custom input under process"""

import cv2

test_img = cv2.imread("/content/img.png")
test_img = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
test_img = cv2.resize(test_img, (28, 28))
test_input = np.expand_dims(test_img, axis=0)

plt.imshow(test_img)

test_input = test_img.reshape((1,28,28,1))

model.predict(test_input)

var = (model.predict(test_input) > 0.5).astype("int32")

# Define the class labels
class_labels = ["class_0", "class_1", "class_2", "class_3", "class_4",
                "class_5", "class_6", "class_7", "class_8", "class_9"]

# Get the predicted class index
predicted_class_index = np.argmax(var)

# Map the class index to the class label
predicted_class_label = class_labels[predicted_class_index]

# Print the predicted class label
print(f"Predicted class: {predicted_class_label}")