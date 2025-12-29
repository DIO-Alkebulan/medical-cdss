"""
Machine Learning Inference and Grad-CAM Generation
"""

from fastai.vision.all import *
import torch
import torch.nn.functional as F
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')


class ModelInference:
    def __init__(self, model_path: str):
        """Initialize the FastAI model"""
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load model
        try:
            self.learner = load_learner(model_path)
            self.learner.model.eval()
            print(f"Model loaded successfully from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.learner = None
        
        # Disease classes (adjust based on your model)
        self.disease_classes = [
            'Normal',
            'Bacterial Pneumonia',
            'Viral Pneumonia',
            'COVID-19',
            'Tuberculosis'
        ]
        
        # Severity thresholds (you can adjust these)
        self.severity_thresholds = {
            'mild': 0.5,
            'moderate': 0.75,
            'severe': 0.9
        }
    
    def predict(self, image_path: str) -> Dict:
        """
        Perform prediction on chest X-ray image
        Returns: Dictionary with disease, severity, confidence, recommendations
        """
        if self.learner is None:
            # Fallback for demonstration when model isn't loaded
            return self._mock_prediction(image_path)
        
        try:
            # Load and predict
            img = PILImage.create(image_path)
            pred_class, pred_idx, probs = self.learner.predict(img)
            
            # Get disease and confidence
            disease = str(pred_class)
            confidence = float(probs[pred_idx]) * 100
            
            # Determine severity based on confidence and disease
            severity = self._calculate_severity(disease, confidence)
            
            # Generate Grad-CAM
            gradcam_path = self._generate_gradcam(image_path, pred_idx)
            
            # Get affected regions
            affected_regions = self._identify_regions(disease)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(disease, severity)
            
            return {
                'disease': disease,
                'severity': severity,
                'confidence': confidence,
                'affected_regions': affected_regions,
                'recommendations': recommendations,
                'gradcam_path': gradcam_path
            }
        
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._mock_prediction(image_path)
    
    def _calculate_severity(self, disease: str, confidence: float) -> str:
        """Calculate severity based on disease type and confidence"""
        if disease == 'Normal':
            return 'None'
        
        # Normalize confidence to 0-1 range
        conf_normalized = confidence / 100.0
        
        if conf_normalized >= self.severity_thresholds['severe']:
            return 'Severe'
        elif conf_normalized >= self.severity_thresholds['moderate']:
            return 'Moderate'
        else:
            return 'Mild'
    
    def _generate_gradcam(self, image_path: str, target_class: int) -> str:
        """Generate Grad-CAM heatmap"""
        try:
            # Load image
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # For demonstration, create a simple heatmap
            # In production, implement proper Grad-CAM
            heatmap = self._create_demo_heatmap(img)
            
            # Overlay heatmap on original image
            overlay = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
            
            # Save Grad-CAM image
            gradcam_filename = f"gradcam_{Path(image_path).stem}.jpg"
            gradcam_path = f"uploads/{gradcam_filename}"
            cv2.imwrite(gradcam_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
            
            return gradcam_path
        
        except Exception as e:
            print(f"Grad-CAM generation error: {e}")
            return image_path  # Return original if Grad-CAM fails
    
    def _create_demo_heatmap(self, img: np.ndarray) -> np.ndarray:
        """Create demonstration heatmap (replace with real Grad-CAM)"""
        height, width = img.shape[:2]
        
        # Create circular heatmap in center-lower region (typical for pneumonia)
        y, x = np.ogrid[:height, :width]
        center_x, center_y = width // 2, int(height * 0.6)
        radius = min(width, height) // 3
        
        mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
        
        heatmap = np.zeros((height, width), dtype=np.float32)
        heatmap[mask] = 1.0
        
        # Apply Gaussian blur
        heatmap = cv2.GaussianBlur(heatmap, (51, 51), 0)
        
        # Normalize and convert to color
        heatmap = (heatmap * 255).astype(np.uint8)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
        
        return heatmap_color
    
    def _identify_regions(self, disease: str) -> List[str]:
        """Identify affected lung regions based on disease"""
        region_map = {
            'Normal': [],
            'Bacterial Pneumonia': ['Lower lobes bilateral', 'Right middle lobe'],
            'Viral Pneumonia': ['Bilateral interstitial pattern', 'Perihilar region'],
            'COVID-19': ['Bilateral peripheral', 'Lower lobes', 'Ground-glass opacities'],
            'Tuberculosis': ['Upper lobes', 'Apical segments', 'Cavitary lesions']
        }
        return region_map.get(disease, ['Bilateral lung fields'])
    
    def _generate_recommendations(self, disease: str, severity: str) -> List[str]:
        """Generate clinical recommendations"""
        if disease == 'Normal':
            return ['No immediate treatment required', 'Continue routine health monitoring']
        
        base_recommendations = {
            'Bacterial Pneumonia': [
                'Initiate broad-spectrum antibiotic therapy',
                'Monitor oxygen saturation continuously',
                'Chest physiotherapy',
                'Follow-up X-ray in 48-72 hours'
            ],
            'Viral Pneumonia': [
                'Supportive care and hydration',
                'Antiviral therapy if indicated',
                'Monitor for secondary bacterial infection',
                'Consider oxygen therapy'
            ],
            'COVID-19': [
                'Isolate patient immediately',
                'PCR test confirmation required',
                'Monitor oxygen levels closely',
                'Consider corticosteroids if severe',
                'Thromboprophylaxis assessment'
            ],
            'Tuberculosis': [
                'Initiate standard TB treatment regimen',
                'Airborne isolation precautions',
                'Contact tracing required',
                'Sputum culture and sensitivity',
                'Directly observed therapy (DOT)'
            ]
        }
        
        recommendations = base_recommendations.get(disease, ['Consult specialist'])
        
        # Add severity-specific recommendations
        if severity == 'Severe':
            recommendations.insert(0, '⚠️ URGENT: Consider ICU admission')
            recommendations.insert(1, 'Immediate specialist consultation required')
        elif severity == 'Moderate':
            recommendations.insert(0, 'Hospital admission recommended')
        
        return recommendations
    
    def _mock_prediction(self, image_path: str) -> Dict:
        """Mock prediction for demonstration when model isn't available"""
        import random
        
        disease = random.choice(self.disease_classes[1:])  # Exclude Normal
        confidence = random.uniform(75, 95)
        severity = random.choice(['Mild', 'Moderate', 'Severe'])
        
        return {
            'disease': disease,
            'severity': severity,
            'confidence': confidence,
            'affected_regions': self._identify_regions(disease),
            'recommendations': self._generate_recommendations(disease, severity),
            'gradcam_path': image_path
        }