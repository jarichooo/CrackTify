import tensorflow as tf
import numpy as np
from PIL import Image
import os
import cv2
import sys
from datetime import datetime

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

        # Load and process image (same as before)
        img = cv2.imread(image_path)
        if img is None:
            raise RuntimeError("Failed to load image")
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 99, 15
        )
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        output = img.copy()
        valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 200]

        # Draw crack outlines + light boxes
        cv2.drawContours(output, valid_contours, -1, (0, 0, 255), 2)
        for cnt in valid_contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(output, (x, y), (x + w, y + h), (100, 255, 100), 2)

        # Get the correct path to your storage/ folder
        if getattr(sys, 'frozen', False):
            # Running as packaged app (Android APK or desktop exe)
            base_path = sys._MEIPASS
            storage_path = os.path.join(base_path, "storage")
        else:
            # Development mode
            current_dir = os.path.dirname(os.path.abspath(__file__))  # utils/detect_image.py
            src_dir = os.path.dirname(os.path.dirname(current_dir))  # src/
            storage_path = os.path.join(src_dir, "storage\data\images\detected")

        # Create storage folder if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = os.path.splitext(os.path.basename(image_path))[0]
        save_filename = f"{original_name}_crack_{timestamp}.jpg"
        save_path = os.path.join(storage_path, save_filename)

        # Save the image
        success = cv2.imwrite(save_path, output)
        if not success:
            raise RuntimeError(f"Failed to save to {save_path}")

        print(f"Crack image saved to storage/: {save_filename}")
        return save_path