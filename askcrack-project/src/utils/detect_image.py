import tensorflow as tf
import numpy as np
from PIL import Image
import os
import cv2
import sys
from datetime import datetime

from services.crack_service import add_crack_service

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
            
    def analyze_and_save(self, image_path: str, confidence_threshold: float = 0.4) -> str:
        """
        Analyzes image, draws crack contours if confidence > threshold,
        and saves with confidence in filename for proper history display.
        """
        prob = self.predict(image_path)  # 0.0 to 1.0

        # === Determine storage path (same as before) ===
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            storage_path = os.path.join(base_path, "storage", "data", "images", "detected")
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(os.path.dirname(current_dir))
            storage_path = os.path.join(src_dir, "storage", "data", "images", "detected")

        os.makedirs(storage_path, exist_ok=True)

        # === Generate clean, parseable filename ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Clean filename (remove special chars that might break parsing)
        safe_name = "".join(c for c in original_name if c.isalnum() or c in " _-")

        # NEW: Always include confidence in filename → _conf_0.87
        confidence_str = f"{prob:.4f}"
        save_filename = f"{timestamp}_{safe_name}_conf_{confidence_str}.jpg"
        save_path = os.path.join(storage_path, save_filename)

        # Load image once
    def analyze_and_save(self, image_path: str, confidence_threshold: float = 0.4) -> str:
        """
        Analyzes image, draws crack contours if confidence > threshold,
        and saves with confidence in filename for proper history display.
        """
        prob = self.predict(image_path)  # 0.0 to 1.0

        # === Determine storage path (same as before) ===
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            storage_path = os.path.join(base_path, "storage", "data", "images", "detected")
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.dirname(os.path.dirname(current_dir))
            storage_path = os.path.join(src_dir, "storage", "data", "images", "detected")

        os.makedirs(storage_path, exist_ok=True)

        # === Generate clean, parseable filename ===
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Clean filename (remove special chars that might break parsing)
        safe_name = "".join(c for c in original_name if c.isalnum() or c in " _-")

        # NEW: Always include confidence in filename → _conf_0.87
        confidence_str = f"{prob:.4f}"
        save_filename = f"{timestamp}_{safe_name}_conf_{confidence_str}.jpg"
        save_path = os.path.join(storage_path, save_filename)

        # Load image once
        img = cv2.imread(image_path)
        if img is None:
            raise RuntimeError(f"Failed to load image: {image_path}")

        output = img.copy()

        # === Only draw contours if confidence is meaningful ===
        if prob >= confidence_threshold:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 99, 15
            )
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 200]

            # Draw red contours + green bounding boxes
            cv2.drawContours(output, valid_contours, -1, (200, 0, 0), 3)  # Red outline
            for cnt in valid_contours:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(output, (x, y), (x + w, y + h), (100, 255, 100), 3)

            # Optional: Add confidence text on image
            cv2.putText(
                output,
                f"Crack: {prob*100:.1f}%",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 0, 255) if prob > 0.8 else (0, 165, 255) if prob > 0.4 else (0, 255, 0),
                2
            )
        else:
            # Low confidence → just show "No Crack" text
            cv2.putText(
                output,
                f"No Crack ({prob*100:.1f}%)",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2
            )

        # === Save final image ===
        success = cv2.imwrite(save_path, output)
        if not success:
            raise RuntimeError(f"Failed to save image to {save_path}")

        print(f"Image saved: {save_filename} | Confidence: {prob:.4f}")
        return save_path