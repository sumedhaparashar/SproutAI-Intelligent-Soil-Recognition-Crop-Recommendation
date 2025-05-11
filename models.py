from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SoilAnalysis(db.Model):
    """
    Model to store soil analysis results
    """
    id = db.Column(db.Integer, primary_key=True)
    soil_type = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    image_filename = db.Column(db.String(255), nullable=True)
    recommendations = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<SoilAnalysis {self.id}: {self.soil_type} ({self.confidence:.2f}%)>"

    @property
    def recommended_crops_list(self):
        if self.recommendations:
            return [crop.strip() for crop in self.recommendations.split(',')]
        return []

    @recommended_crops_list.setter
    def recommended_crops_list(self, crops_list):
        self.recommendations = ', '.join(crops_list) if crops_list else None
