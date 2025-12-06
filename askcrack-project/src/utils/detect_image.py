import tensorflow as tf
import numpy as np
from PIL import Image
import os

class CrackClassifier:
    def __init__(self, model_path: str):
        """
        Constructor: loads the TFLite model ONCE.
        """
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details  = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    # ---------- PREPROCESS FUNCTIONS ----------
    def _mobilenet_standard_scaling(self, image_array_rgb):
        x = image_array_rgb.astype(np.float32)
        x /= 127.5
        x -= 1.0
        return x

    def _preprocess_image(self, image_path, target_size=(128, 128)):
        img = Image.open(image_path).convert("RGB")
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        img_array = np.array(img)
        return self._mobilenet_standard_scaling(img_array)

    # ---------- PREDICT FUNCTION ----------
    def predict(self, image_path: str) -> float:
        """
        Returns a probability value between 0 and 1.
        """
        # Preprocess image
        img = self._preprocess_image(image_path)
        img = np.expand_dims(img, axis=0)

        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()

        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        probability = float(output[0][0])  # assuming sigmoid output

        return probability
