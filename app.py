import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from soil_analyzer import SoilAnalyzer
from models import db, SoilAnalysis

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soil_analysis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}

# Initialize the database
db.init_app(app)

# Configure upload settings
UPLOAD_FOLDER = 'tmp/uploads'  # Relative to current directory
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize soil analyzer
soil_analyzer = SoilAnalyzer()

# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created")


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        if 'soil_image' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['soil_image']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                soil_type, confidence, recommended_crops = soil_analyzer.analyze_image(filepath)
                analysis = SoilAnalysis(
                    soil_type=soil_type,
                    confidence=confidence,
                )
                analysis.recommended_crops_list = recommended_crops

                db.session.add(analysis)
                db.session.commit()
                logger.info(f"Saved soil analysis to database with ID: {analysis.id}")

                result = {
                    'soil_type': soil_type,
                    'confidence': confidence,
                    'recommended_crops': recommended_crops,
                    'demo_mode': soil_analyzer.use_demo_mode,
                    'id': analysis.id
                }
                os.remove(filepath)
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                flash(f'Error processing image: {str(e)}', 'danger')
                db.session.rollback()
        else:
            flash('File type not allowed. Please upload a valid image (PNG, JPG, JPEG).', 'danger')

    return render_template('index.html', result=result, demo_mode=soil_analyzer.use_demo_mode)


@app.route('/history', methods=['GET'])
def history():
    analyses = SoilAnalysis.query.order_by(SoilAnalysis.created_at.desc()).all()
    return render_template('history.html', analyses=analyses)


@app.route('/analysis/<int:analysis_id>', methods=['GET'])
def view_analysis(analysis_id):
    analysis = SoilAnalysis.query.get_or_404(analysis_id)
    result = {
        'soil_type': analysis.soil_type,
        'confidence': analysis.confidence,
        'recommended_crops': analysis.recommended_crops_list,
        'created_at': analysis.created_at,
        'id': analysis.id
    }
    return render_template('view_analysis.html', result=result)


@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large. Maximum file size is 16MB.', 'danger')
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_server_error(error):
    flash('An unexpected error occurred. Please try again later.', 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
