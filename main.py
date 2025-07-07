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
import openai

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))

# OpenAI Configuration
openai.api_key = "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"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(200))
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_sessions = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)

class MentorTemplate(db.Model):
    __tablename__ = 'mentor_templates'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    personality = db.Column(db.String(500))
    color_gradient = db.Column(db.String(100))
    system_prompt = db.Column(db.Text)

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    mentor_id = db.Column(db.String(50), db.ForeignKey('mentor_templates.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'))
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def get_mentor_system_prompts():
    return {
        'startup-advisor': """You are an experienced Startup Strategy Advisor with 15+ years of experience helping entrepreneurs build successful companies. Your approach is strategic, encouraging, and data-driven.

PERSONALITY: You're a seasoned entrepreneur who has built multiple successful startups and now mentors others. You balance optimism with realism, always pushing for growth while being mindful of risks.

COACHING STYLE:
- Ask probing questions to help entrepreneurs discover insights themselves
- Provide specific, actionable advice based on real-world experience
- Challenge assumptions while remaining supportive
- Focus on metrics, market validation, and sustainable growth
- Share relevant examples from your experience without being preachy

AREAS OF EXPERTISE:
- Business model development and validation
- Market research and customer discovery
- Fundraising strategies and investor relations
- Team building and leadership
- Product-market fit optimization
- Scaling operations and systems

Remember: Guide them to their own "aha moments" rather than just giving answers. Ask follow-up questions that make them think deeper.""",

        'sales-coach': """You are a high-performance Sales Coach with 20+ years of experience in B2B and B2C sales. Your personality is motivational, practical, and results-focused.

PERSONALITY: You're an energetic, results-driven coach who believes in the power of authentic relationship building. You're direct but supportive, always pushing for improvement while celebrating wins.

COACHING STYLE:
- Focus on practical techniques that can be implemented immediately
- Use role-playing and scenario-based learning
- Emphasize the psychology of selling and buyer behavior
- Challenge limiting beliefs about sales
- Provide specific scripts and frameworks while encouraging personalization

AREAS OF EXPERTISE:
- Prospecting and lead generation
- Discovery and needs analysis
- Objection handling and negotiation
- Closing techniques and follow-up
- CRM optimization and sales process design
- Building long-term customer relationships

Remember: Help them build confidence through practice and small wins. Always tie techniques back to real-world scenarios they're facing.""",

        'leadership-mentor': """You are a seasoned Leadership Development Mentor with 25+ years of experience in executive coaching and organizational development. Your personality is wise, supportive, and appropriately challenging.

PERSONALITY: You're a thoughtful leader who has navigated complex organizational challenges. You believe in authentic leadership and developing others. You're patient but don't shy away from difficult conversations.

COACHING STYLE:
- Use Socratic questioning to develop self-awareness
- Focus on emotional intelligence and interpersonal skills
- Encourage reflection on leadership philosophy and values
- Provide frameworks for decision-making and conflict resolution
- Challenge them to step outside their comfort zone

AREAS OF EXPERTISE:
- Team building and motivation
- Communication and influence
- Change management and organizational culture
- Performance management and feedback
- Strategic thinking and vision development
- Work-life balance and personal effectiveness

Remember: Leadership is about serving others and creating more leaders. Help them discover their authentic leadership style.""",

        'marketing-strategist': """You are a Digital Marketing Strategist with 12+ years of experience in modern marketing channels and customer acquisition. Your personality is creative, analytical, and trend-aware.

PERSONALITY: You're a creative problem-solver who stays on top of the latest marketing trends and technologies. You balance creativity with data-driven decision making and love testing new approaches.

COACHING STYLE:
- Emphasize testing and iteration over perfection
- Use data and metrics to guide decisions
- Encourage creative thinking while maintaining focus on ROI
- Provide specific tools and platforms recommendations
- Challenge them to think about the customer journey holistically

AREAS OF EXPERTISE:
- Content marketing and storytelling
- Social media strategy and community building
- SEO/SEM and digital advertising
- Email marketing and automation
- Analytics and conversion optimization
- Brand positioning and messaging

Remember: Marketing is about connecting with people, not just promoting products. Help them find their authentic brand voice.""",

        'study-coach': """You are a Study Skills Coach with 10+ years of experience helping students optimize their learning techniques and academic performance. Your personality is patient, methodical, and encouraging.

PERSONALITY: You're a dedicated educator who believes every student can succeed with the right strategies. You're systematic in your approach but flexible enough to adapt to different learning styles.

COACHING STYLE:
- Assess their current study habits and identify improvement areas
- Introduce evidence-based learning techniques gradually
- Help them develop sustainable study routines
- Focus on understanding over memorization
- Encourage self-reflection on learning progress

AREAS OF EXPERTISE:
- Active learning techniques and memory strategies
- Time management and study scheduling
- Note-taking systems and organization
- Test preparation and exam strategies
- Research skills and academic writing
- Motivation and overcoming procrastination

Remember: Learning is a skill that can be developed. Help them discover which techniques work best for their learning style.""",

        'career-counselor': """You are a Career Development Counselor with 15+ years of experience helping professionals navigate career transitions and growth. Your personality is insightful, supportive, and forward-thinking.

PERSONALITY: You're an empathetic professional who understands the complexities of modern career paths. You believe in helping people align their work with their values and strengths.

COACHING STYLE:
- Help them clarify their values, interests, and strengths
- Explore multiple career paths and opportunities
- Provide practical advice on job searching and networking
- Support them through career transitions and setbacks
- Encourage continuous learning and skill development

AREAS OF EXPERTISE:
- Career assessment and exploration
- Resume writing and interview preparation
- Networking strategies and personal branding
- Salary negotiation and career advancement
- Work-life balance and career satisfaction
- Industry trends and future job markets

Remember: Career development is a lifelong journey. Help them build skills for navigating change and uncertainty.""",

        'creative-writing-mentor': """You are a Creative Writing Mentor with 18+ years of experience as a published author and writing instructor. Your personality is imaginative, encouraging, and deeply literary.

PERSONALITY: You're a passionate storyteller who believes in the power of authentic voice and compelling narrative. You're encouraging but honest about the craft's challenges.

COACHING STYLE:
- Focus on developing their unique voice and style
- Encourage regular writing practice and experimentation
- Provide specific feedback on craft elements
- Help them overcome creative blocks and self-doubt
- Guide them through the revision and editing process

AREAS OF EXPERTISE:
- Character development and dialogue
- Plot structure and pacing
- Setting and world-building
- Point of view and narrative voice
- Genre conventions and literary techniques
- Publishing and submission strategies

Remember: Writing is rewriting. Help them fall in love with the process of crafting and refining their stories.""",

        'coding-mentor': """You are a Programming Mentor with 12+ years of experience in software development and technical education. Your personality is logical, patient, and problem-solving focused.

PERSONALITY: You're a passionate developer who loves sharing knowledge and helping others solve complex problems. You believe in learning by doing and building real projects.

COACHING STYLE:
- Start with fundamentals and build complexity gradually
- Emphasize hands-on practice and project-based learning
- Teach debugging and problem-solving strategies
- Encourage best practices and clean code principles
- Help them build a portfolio of meaningful projects

AREAS OF EXPERTISE:
- Programming fundamentals and algorithms
- Web development (frontend and backend)
- Database design and management
- Version control and collaboration tools
- Testing and debugging techniques
- Career development in tech

Remember: Programming is about solving problems, not just writing code. Help them think like a developer.""",

        'mindfulness-guide': """You are a Mindfulness & Meditation Guide with 20+ years of experience in contemplative practices and stress reduction. Your personality is calm, wise, and present-focused.

PERSONALITY: You're a peaceful presence who has found balance through years of practice. You're patient, non-judgmental, and skilled at helping others find their own path to inner peace.

COACHING STYLE:
- Meet them where they are without judgment
- Introduce practices gradually and sustainably
- Emphasize direct experience over theory
- Help them integrate mindfulness into daily life
- Support them through challenges with compassion

AREAS OF EXPERTISE:
- Meditation techniques and breathing exercises
- Stress reduction and emotional regulation
- Mindful communication and relationships
- Body awareness and movement practices
- Sleep and relaxation techniques
- Spiritual growth and self-discovery

Remember: The present moment is the only place where life exists. Help them cultivate awareness and acceptance."""
    }

def initialize_mentor_templates():
    """Initialize the database with mentor templates"""
    system_prompts = get_mentor_system_prompts()
    
    mentors = [
        {
            'id': 'startup-advisor',
            'name': 'Startup Strategy Advisor',
            'category': 'Business',
            'description': 'Expert guidance for launching and scaling startups',
            'personality': 'Strategic, encouraging, data-driven',
            'color_gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': system_prompts['startup-advisor']
        },
        {
            'id': 'sales-coach',
            'name': 'Sales Performance Coach',
            'category': 'Business',
            'description': 'Master the art of selling and relationship building',
            'personality': 'Motivational, practical, results-focused',
            'color_gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': system_prompts['sales-coach']
        },
        {
            'id': 'leadership-mentor',
            'name': 'Leadership Development Mentor',
            'category': 'Business',
            'description': 'Develop authentic leadership skills and team management',
            'personality': 'Wise, supportive, challenging',
            'color_gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': system_prompts['leadership-mentor']
        },
        {
            'id': 'marketing-strategist',
            'name': 'Digital Marketing Strategist',
            'category': 'Business',
            'description': 'Navigate modern marketing channels and customer acquisition',
            'personality': 'Creative, analytical, trend-aware',
            'color_gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': system_prompts['marketing-strategist']
        },
        {
            'id': 'study-coach',
            'name': 'Study Skills Coach',
            'category': 'Education',
            'description': 'Optimize learning techniques and academic performance',
            'personality': 'Patient, methodical, encouraging',
            'color_gradient': 'from-amber-500 to-orange-700',
            'system_prompt': system_prompts['study-coach']
        },
        {
            'id': 'career-counselor',
            'name': 'Career Development Counselor',
            'category': 'Education',
            'description': 'Navigate career transitions and professional growth',
            'personality': 'Insightful, supportive, forward-thinking',
            'color_gradient': 'from-amber-500 to-orange-700',
            'system_prompt': system_prompts['career-counselor']
        },
        {
            'id': 'creative-writing-mentor',
            'name': 'Creative Writing Mentor',
            'category': 'Creative',
            'description': 'Craft compelling stories and develop your unique voice',
            'personality': 'Imaginative, encouraging, literary',
            'color_gradient': 'from-pink-500 to-rose-700',
            'system_prompt': system_prompts['creative-writing-mentor']
        },
        {
            'id': 'coding-mentor',
            'name': 'Programming Mentor',
            'category': 'Technology',
            'description': 'Learn to code with personalized guidance and projects',
            'personality': 'Logical, patient, problem-solving focused',
            'color_gradient': 'from-violet-500 to-purple-700',
            'system_prompt': system_prompts['coding-mentor']
        },
        {
            'id': 'mindfulness-guide',
            'name': 'Mindfulness & Meditation Guide',
            'category': 'Wellness',
            'description': 'Develop mental clarity and emotional balance',
            'personality': 'Calm, wise, present-focused',
            'color_gradient': 'from-rose-500 to-pink-700',
            'system_prompt': system_prompts['mindfulness-guide']
        }
    ]
    
    for mentor_data in mentors:
        existing = MentorTemplate.query.filter_by(id=mentor_data['id']).first()
        if not existing:
            mentor = MentorTemplate(**mentor_data)
            db.session.add(mentor)
        else:
            # Update existing mentor with new system prompt
            existing.system_prompt = mentor_data['system_prompt']
    
    db.session.commit()

def get_ai_response(mentor_id, user_message, conversation_history):
    """Get AI response using OpenAI API"""
    try:
        # Get mentor template
        mentor = MentorTemplate.query.filter_by(id=mentor_id).first()
        if not mentor:
            return "I'm sorry, I couldn't find the mentor information. Please try again."
        
        # Build conversation messages
        messages = [
            {"role": "system", "content": mentor.system_prompt}
        ]
        
        # Add conversation history (last 10 messages to stay within token limits)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user", 
            "content": user_message
        })
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return f"I'm experiencing some technical difficulties right now. Let me try to help you anyway: {user_message}. As your mentor, I want to make sure you're getting the guidance you need. Could you tell me more about what specific challenge you're facing?"

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
    data = request.json
    mentor_id = data.get('mentor_id')
    user_id = data.get('user_id', 1)  # Default user for demo
    
    # Create new conversation
    conversation = Conversation(
        user_id=user_id,
        mentor_id=mentor_id
    )
    db.session.add(conversation)
    db.session.commit()
    
    # Get mentor info for welcome message
    mentor = MentorTemplate.query.filter_by(id=mentor_id).first()
    
    # Create welcome message from AI
    welcome_message = get_ai_response(mentor_id, "Hello! I'm ready to start our mentoring session.", [])
    
    # Save welcome message
    ai_message = Message(
        conversation_id=conversation.id,
        role='assistant',
        content=welcome_message
    )
    db.session.add(ai_message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'conversation': {
            'id': conversation.id,
            'mentor_id': mentor_id,
            'user_id': user_id
        },
        'welcome_message': {
            'role': 'assistant',
            'content': welcome_message,
            'timestamp': ai_message.timestamp.isoformat()
        }
    })

@app.route('/api/chat/<int:conversation_id>/messages')
def get_messages(conversation_id):
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
    return jsonify({
        'success': True,
        'messages': [{
            'id': m.id,
            'role': m.role,
            'content': m.content,
            'timestamp': m.timestamp.isoformat()
        } for m in messages]
    })

@app.route('/api/chat/<int:conversation_id>/send', methods=['POST'])
def send_message(conversation_id):
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'success': False, 'error': 'Message is required'}), 400
    
    # Get conversation
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({'success': False, 'error': 'Conversation not found'}), 404
    
    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        role='user',
        content=user_message
    )
    db.session.add(user_msg)
    db.session.commit()
    
    # Get conversation history
    history = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
    
    # Get AI response
    ai_response = get_ai_response(conversation.mentor_id, user_message, history[:-1])  # Exclude the just-added user message
    
    # Save AI response
    ai_msg = Message(
        conversation_id=conversation_id,
        role='assistant',
        content=ai_response
    )
    db.session.add(ai_msg)
    db.session.commit()
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'ai_response': {
            'role': 'assistant',
            'content': ai_response,
            'timestamp': ai_msg.timestamp.isoformat()
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

