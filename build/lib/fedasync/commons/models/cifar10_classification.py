
from keras.models import Sequential
from keras.layers import MaxPool2D, Dense, Flatten, Dropout, Conv2D, BatchNormalization

cifar10_classification = Sequential()
cifar10_classification.add(
    Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same', input_shape=(32, 32, 3)))
cifar10_classification.add(BatchNormalization())
cifar10_classification.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
cifar10_classification.add(BatchNormalization())
cifar10_classification.add(MaxPool2D((2, 2)))
cifar10_classification.add(Dropout(0.2))
cifar10_classification.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
cifar10_classification.add(BatchNormalization())
cifar10_classification.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
cifar10_classification.add(BatchNormalization())
cifar10_classification.add(MaxPool2D((2, 2)))
cifar10_classification.add(Dropout(0.3))
cifar10_classification.add(Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
cifar10_classification.add(BatchNormalization())
cifar10_classification.add(Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_uniform', padding='same'))
cifar10_classification.add(BatchNormalization())
cifar10_classification.add(MaxPool2D((2, 2)))
cifar10_classification.add(Dropout(0.4))
cifar10_classification.add(Flatten())
cifar10_classification.add(Dense(128, activation='relu', kernel_initializer='he_uniform'))
cifar10_classification.add(BatchNormalization())
cifar10_classification.add(Dropout(0.5))
cifar10_classification.add(Dense(10, activation='softmax'))

cifar10_classification.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
