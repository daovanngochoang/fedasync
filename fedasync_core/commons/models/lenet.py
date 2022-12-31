from tensorflow.keras.models import Sequential
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.layers import Dense, Flatten, Conv2D, AveragePooling2D

'''
Model: Lenet

Total params: 207,406
Trainable params: 207,406
Non-trainable params: 0

'''

class LeNet(Sequential):
    def __init__(self, input_shape = (48, 48, 1), nb_classes = 30):
        super().__init__()
        self.add(Conv2D(6, kernel_size=(5, 5), strides=(1, 1), activation= 'relu', input_shape= input_shape, padding="same"))
        self.add(AveragePooling2D(pool_size=(2, 2), strides=(2, 2), padding= 'valid'))
        
        self.add(Conv2D(16, kernel_size=(5, 5), strides=(1, 1), activation= 'relu', padding= 'valid'))
        self.add(AveragePooling2D(pool_size=(2, 2), strides=(2, 2), padding= 'valid'))
        
        self.add(Flatten())

        self.add(Dense(120, activation= 'relu'))
        self.add(Dense(84, activation= 'relu'))
        self.add(Dense(nb_classes, activation= 'softmax'))

        self.compile(optimizer= 'adam',
                    loss= categorical_crossentropy,
                    metrics= ['accuracy'])
