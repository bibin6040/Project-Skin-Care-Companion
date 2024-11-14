from django.core.management.base import BaseCommand
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from django.conf import settings

class Command(BaseCommand):
    help = 'Train the skin disease prediction model using VGG16'

    def handle(self, *args, **kwargs):
        # Image Data Generators
        train_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
        test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

        # Directories for training and test data
        train_dir = os.path.join(settings.DATASET_DIR, 'skin-disease-images/train')
        test_dir = os.path.join(settings.DATASET_DIR, 'skin-disease-images/test')

        # Load data
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical'
        )
        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical'
        )

        # Load the VGG16 model
        base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

        # Add custom top layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(128, activation='relu')(x)
        predictions = Dense(15, activation='softmax')(x)

        # Define the model
        model = Model(inputs=base_model.input, outputs=predictions)

        # Freeze the base model layers
        for layer in base_model.layers:
            layer.trainable = False

        # Compile the model
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

        # Train the model
        model.fit(train_generator, validation_data=test_generator, epochs=10)

        # Save the model
        model.save(os.path.join(settings.BASE_DIR, 'model', 'skin_disease_model.h5'))

        self.stdout.write(self.style.SUCCESS('Model training completed successfully.'))