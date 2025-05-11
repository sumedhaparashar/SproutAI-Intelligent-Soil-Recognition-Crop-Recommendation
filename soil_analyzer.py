import os
import logging
import random
from PIL import Image

# Import conditionally
try:
    import numpy as np
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

class SoilAnalyzer:
    def __init__(self, model_path='soil_model.h5'):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.use_demo_mode = True

        if TENSORFLOW_AVAILABLE and os.path.exists(model_path):
            try:
                self.load_model(model_path)
                self.use_demo_mode = False
            except Exception as e:
                self.logger.warning(f"Model could not be loaded, using demo mode: {str(e)}")
        else:
            self.logger.warning("TensorFlow/NumPy not available or model file missing, using demo mode")

        self.soil_types = ['Red soil', 'Clay soil', 'Black soil', 'Alluvial soil']
        self.crop_recommendations = {
            'Red soil': ['Groundnut', 'Potato', 'Cotton', 'Millet', 'Tobacco', 'Pulses', 'Oilseeds', 'Sorghum'],
            'Clay soil': ['Rice', 'Wheat', 'Oats', 'Beans', 'Lettuce', 'Cabbage', 'Broccoli', 'Brussels Sprouts'],
            'Black soil': ['Cotton', 'Sugarcane', 'Cereals', 'Wheat', 'Corn', 'Sorghum', 'Sunflower', 'Soybeans', 'Peanuts', 'Most vegetables'],
            'Alluvial soil': ['Rice', 'Wheat', 'Sugarcane', 'Maize', 'Pulses', 'Oilseeds', 'Fruits', 'Vegetables', 'Jute', 'Cotton']
        }

    def load_model(self, model_path):
        self.logger.info(f"Loading model from {model_path}")
        try:
            self.model = keras.models.load_model(model_path)
            self.logger.info("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}")

    def preprocess_image(self, image_path):
        if not TENSORFLOW_AVAILABLE:
            raise RuntimeError("TensorFlow/NumPy not available")

        try:
            img = Image.open(image_path).resize((224, 224)).convert('RGB')
            img_array = np.array(img) / 255.0
            return np.expand_dims(img_array, axis=0)
        except Exception as e:
            self.logger.error(f"Image preprocessing failed: {str(e)}")
            raise ValueError(f"Image preprocessing error: {str(e)}")

    def analyze_image(self, image_path):
        try:
            img = None
            try:
                img = Image.open(image_path).resize((100, 100)).convert('RGB')
            except Exception as e:
                self.logger.warning(f"Color analysis failed: {str(e)}")

            if self.use_demo_mode:
                self.logger.info("Running in demo mode")
                soil_type = self._demo_predict(img)
                confidence = random.uniform(70.0, 95.0)
                recommended_crops = self.crop_recommendations[soil_type]
                self.logger.info(f"Demo prediction: {soil_type} ({confidence:.2f}%)")
                return soil_type, confidence, recommended_crops

            processed_image = self.preprocess_image(image_path)
            predictions = self.model.predict(processed_image)
            predicted_class_index = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_index] * 100)
            soil_type = self.soil_types[predicted_class_index]
            recommended_crops = self.crop_recommendations[soil_type]
            self.logger.info(f"Model prediction: {soil_type} ({confidence:.2f}%)")
            return soil_type, confidence, recommended_crops

        except Exception as e:
            self.logger.error(f"Soil analysis failed: {str(e)}")
            raise RuntimeError(f"Image analysis error: {str(e)}")

    def _demo_predict(self, img):
        if img:
            try:
                pixels = list(img.getdata())
                avg_r = sum(p[0] for p in pixels) / len(pixels)
                avg_g = sum(p[1] for p in pixels) / len(pixels)
                avg_b = sum(p[2] for p in pixels) / len(pixels)

                weights = {soil: 0.25 for soil in self.soil_types}

                if avg_r > 150 and avg_b < 100:
                    weights['Red soil'] += 0.3
                    weights['Black soil'] += 0.2
                if avg_g > 150:
                    weights['Clay soil'] += 0.3
                if avg_b > 150 or (avg_r > 150 and avg_g > 150):
                    weights['Alluvial soil'] += 0.3

                total = sum(weights.values())
                weights = {k: v / total for k, v in weights.items()}
                return random.choices(self.soil_types, weights=[weights[st] for st in self.soil_types])[0]

            except Exception as e:
                self.logger.warning(f"Fallback to random due to color analysis error: {str(e)}")

        return random.choice(self.soil_types)
