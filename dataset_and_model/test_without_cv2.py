import tensorflow as tf
import numpy as np
from PIL import Image
import os # Helps manage file paths better

# --------------------------------------------------------------
# 1. Load the TFLite model
# --------------------------------------------------------------
# IMPORTANT: Adjust these paths for your Android App's asset management later
model_path = r"C:/Users/Admin/School/Coding Course/Application Development And Emerging Technologies/CCCS_106/final_project/AskCrack/dataset_and_model/mobilenet_wall_crack_detection.tflite"

interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

input_details  = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Model loaded!")
print(f"Input shape  : {input_details[0]['shape']}  (should be [1, 128, 128, 3])")
print(f"Input dtype  : {input_details[0]['dtype']}")

# --------------------------------------------------------------
# 2. Preprocessing function using Pillow and Numpy
# --------------------------------------------------------------

def mobilenet_standard_scaling(image_array_rgb):
    """
    Manually replicates the Keras preprocess_input(mobilenet) function:
    Scales pixel values from [0, 255] to [-1, 1].
    """
    # Convert to float
    x = image_array_rgb.astype(np.float32)
    # Scale from [0, 255] to [-1, 1]
    x /= 127.5
    x -= 1.0
    return x

def preprocess_image_pillow(image_path, target_size=(128, 128)):
    # Use Pillow instead of cv2
    try:
        # Open image, Pillow reads in RGB by default
        img = Image.open(image_path).convert('RGB')
    except IOError:
        raise FileNotFoundError(f"Cannot read image: {image_path}")
    
    # Resize image
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    
    # Convert PIL image object to numpy array
    img_array = np.array(img) # shape (128, 128, 3), dtype=uint8
    
    # Apply MobileNet specific scaling manually
    img_processed = mobilenet_standard_scaling(img_array)
    
    return img_processed

# --------------------------------------------------------------
# 3. Test on your image
# --------------------------------------------------------------
test_image_path = r"C:/Users/Admin/Downloads/download (1).jpg"

# Preprocess
# Use the new pillow function:
input_array = preprocess_image_pillow(test_image_path)    # shape (128,128,3)
input_array = np.expand_dims(input_array, axis=0)         # shape (1,128,128,3)
# Data is already float32 from the scaling function

# Run inference
interpreter.set_tensor(input_details[0]['index'], input_array)
interpreter.invoke()

# Get result
output = interpreter.get_tensor(output_details[0]['index'])
probability = float(output[0][0])   # sigmoid output

print(f"/nPrediction probability: {probability:.4f}")
if probability > 0.5:
    print("Crack detected (Positive)")
else:
    print("No crack (Negative)")
