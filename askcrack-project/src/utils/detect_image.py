import tensorflow as tf
import numpy as np
from PIL import Image
import os
import cv2

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
            
    def analyze_and_save(self, image_path: str, confidence_threshold: float = 0.5) -> str:
        prob = self.predict(image_path)
        if prob <= confidence_threshold:
            return None

        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise RuntimeError("Failed to load image")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Adaptive threshold — magic for cracks
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 99, 15
        )

        # Clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create output copy
        output = img.copy()

        # Filter and draw actual contours (not boxes!)
        valid_contours = []
        crack_count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 200:  # ignore dust
                # Optional: filter very short or round blobs
                if cv2.arcLength(cnt, False) > 30:  # minimum length
                    valid_contours.append(cnt)
                    crack_count += 1

        # Draw beautiful green outlines (thickness = 4)
        cv2.drawContours(
            image=output,
            contours=valid_contours,
            contourIdx=-1,        # -1 = draw all
            color=(0, 0, 255),    # BGR green
            thickness=4
        )

        # Optional: also draw bounding boxes in lighter green (very professional look)
        for cnt in valid_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(output, (x, y), (x + w, y + h), (100, 255, 100), 2)  # light green

        # Save result
        dir_name = os.path.dirname(image_path)
        name, ext = os.path.splitext(os.path.basename(image_path))
        save_path = os.path.join(dir_name, f"{name}_crack_detected{ext}")
        cv2.imwrite(save_path, output)

        return save_path
