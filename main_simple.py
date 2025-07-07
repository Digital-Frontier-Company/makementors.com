import os
import sys

# Load environment variables (optional for production)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Simple User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(200))
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_sessions = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)

# Simple MentorTemplate model
class MentorTemplate(db.Model):
    __tablename__ = 'mentor_templates'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    personality = db.Column(db.String(500))
    color_gradient = db.Column(db.String(100))
    system_prompt = db.Column(db.Text)

def initialize_mentor_templates():
    """Initialize the database with mentor templates"""
    
    mentors = [
        {
            'id': 'startup-advisor',
            'name': 'Startup Strategy Advisor',
            'category': 'Business',
            'description': 'Expert guidance for launching and scaling startups',
            'personality': 'Strategic, encouraging, data-driven',
            'color_gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': 'You are an experienced Startup Strategy Advisor...'
        },
        {
            'id': 'sales-coach',
            'name': 'Sales Performance Coach',
            'category': 'Business',
            'description': 'Master the art of selling and relationship building',
            'personality': 'Motivational, practical, results-focused',
            'color_gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': 'You are a high-performance Sales Coach...'
        },
        {
            'id': 'leadership-mentor',
            'name': 'Leadership Development Mentor',
            'category': 'Business',
            'description': 'Develop authentic leadership skills and team management',
            'personality': 'Wise, supportive, challenging',
            'color_gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': 'You are a seasoned Leadership Development Mentor...'
        },
        {
            'id': 'marketing-strategist',
            'name': 'Digital Marketing Strategist',
            'category': 'Business',
            'description': 'Navigate modern marketing channels and customer acquisition',
            'personality': 'Creative, analytical, trend-aware',
            'color_gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': 'You are a Digital Marketing Strategist...'
        },
        {
            'id': 'study-coach',
            'name': 'Study Skills Coach',
            'category': 'Education',
            'description': 'Optimize learning techniques and academic performance',
            'personality': 'Patient, methodical, encouraging',
            'color_gradient': 'from-amber-500 to-orange-700',
            'system_prompt': 'You are a Study Skills Coach...'
        },
        {
            'id': 'career-counselor',
            'name': 'Career Development Counselor',
            'category': 'Education',
            'description': 'Navigate career transitions and professional growth',
            'personality': 'Insightful, supportive, forward-thinking',
            'color_gradient': 'from-amber-500 to-orange-700',
            'system_prompt': 'You are a Career Development Counselor...'
        },
        {
            'id': 'creative-writing-mentor',
            'name': 'Creative Writing Mentor',
            'category': 'Creative',
            'description': 'Craft compelling stories and develop your unique voice',
            'personality': 'Imaginative, encouraging, literary',
            'color_gradient': 'from-pink-500 to-rose-700',
            'system_prompt': 'You are a Creative Writing Mentor...'
        },
        {
            'id': 'coding-mentor',
            'name': 'Programming Mentor',
            'category': 'Technology',
            'description': 'Learn to code with personalized guidance and projects',
            'personality': 'Logical, patient, problem-solving focused',
            'color_gradient': 'from-violet-500 to-purple-700',
            'system_prompt': 'You are a Programming Mentor...'
        },
        {
            'id': 'mindfulness-guide',
            'name': 'Mindfulness & Meditation Guide',
            'category': 'Wellness',
            'description': 'Develop mental clarity and emotional balance',
            'personality': 'Calm, wise, present-focused',
            'color_gradient': 'from-rose-500 to-pink-700',
            'system_prompt': 'You are a Mindfulness & Meditation Guide...'
        }
    ]
    
    for mentor_data in mentors:
        existing = MentorTemplate.query.filter_by(id=mentor_data['id']).first()
        if not existing:
            mentor = MentorTemplate(**mentor_data)
            db.session.add(mentor)
    
    db.session.commit()

# API Routes
@app.route('/api/mentor-templates')
def get_mentor_templates():
    templates = MentorTemplate.query.all()
    return jsonify({
        'success': True,
        'templates': [{
            'id': t.id,
            'name': t.name,
            'category': t.category,
            'description': t.description,
            'personality': t.personality,
            'gradient': t.color_gradient
        } for t in templates]
    })

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(
        username=data.get('username'),
        email=data.get('email'),
        full_name=data.get('full_name'),
        total_sessions=data.get('total_sessions', 0),
        current_streak=data.get('current_streak', 0)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'join_date': user.join_date.isoformat(),
            'total_sessions': user.total_sessions,
            'current_streak': user.current_streak
        }
    })

@app.route('/api/chat/start', methods=['POST'])
def start_conversation():
    return jsonify({
        'success': True,
        'conversation': {
            'id': 1,
            'mentor_id': request.json.get('mentor_id'),
            'user_id': request.json.get('user_id')
        }
    })

@app.route('/api/chat/<int:conversation_id>/messages')
def get_messages(conversation_id):
    return jsonify({
        'success': True,
        'messages': []
    })

@app.route('/api/chat/<int:conversation_id>/send', methods=['POST'])
def send_message(conversation_id):
    message = request.json.get('message')
    return jsonify({
        'success': True,
        'ai_response': {
            'role': 'assistant',
            'content': f"Thank you for your message: '{message}'. I'm here to help guide your learning journey. While the full AI capabilities are being set up, I can still provide guidance and support. What specific area would you like to focus on?",
            'timestamp': datetime.utcnow().isoformat()
        }
    })

@app.route('/api/progress/<int:user_id>')
def get_user_progress(user_id):
    return jsonify({
        'success': True,
        'progress': [
            {'subject': 'Python Programming', 'progress': 75, 'total_sessions': 12},
            {'subject': 'Business Strategy', 'progress': 60, 'total_sessions': 8},
            {'subject': 'Creative Writing', 'progress': 40, 'total_sessions': 5}
        ],
        'goals': [
            {'id': 1, 'title': 'Build a Web Application', 'description': 'Complete a full-stack project using React and Node.js', 'status': 'in_progress'},
            {'id': 2, 'title': 'Write 10,000 Words', 'description': 'Complete a short story collection', 'status': 'planning'}
        ],
        'stats': {
            'total_sessions': 24,
            'current_streak': 7,
            'completed_goals': 3,
            'active_goals': 2
        }
    })

# Catch-all routes for other API endpoints
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_fallback(path):
    return jsonify({'success': True, 'message': 'API endpoint working'})

with app.app_context():
    db.create_all()
    initialize_mentor_templates()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

