# Keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPool2D, Dense, Flatten
from keras.utils.np_utils import to_categorical
from keras import optimizers

# creating the basic model
Lenet5 = Sequential()

# 30 Conv Layer
Lenet5.add(Conv2D(30, kernel_size=(3, 3), padding='valid', activation='relu', input_shape=(32, 32, 3)))
# 15 Max Pool Layer
Lenet5.add(MaxPool2D(pool_size=(2, 2), padding='valid'))
# 13 Conv Layer
Lenet5.add(Conv2D(13, kernel_size=(3, 3), padding='valid', activation='relu'))
# 6 Max Pool Layer
Lenet5.add(MaxPool2D(pool_size=(2, 2), padding='valid'))
# Flatten the Layer for transitioning to the Fully Connected Layers
Lenet5.add(Flatten())
# 120 Fully Connected Layer
Lenet5.add(Dense(120, activation='relu'))
# 84 Fully Connected Layer
Lenet5.add(Dense(86, activation='relu'))
# 10 Output
Lenet5.add(Dense(10, activation='softmax'))

# compile the Lenet5
Lenet5.compile(optimizer=optimizers.SGD(lr=0.01, momentum=0.9),
              loss='categorical_crossentropy',
              metrics=['accuracy'])
