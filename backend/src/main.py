import os
import sys
import requests
from datetime import datetime

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Load environment variables (optional for production)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import models after path setup
from src.models.user import db
from src.models.mentor import MentorTemplate, CustomMentor

static_folder = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, static_folder=static_folder)
secret_key = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['SECRET_KEY'] = secret_key

# Database Configuration
database_url = os.getenv('DATABASE_URL', 'sqlite:///makementors.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Enable CORS for all routes
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins)

# Import and register blueprints
from src.routes.user import user_bp
from src.routes.mentor import mentor_bp

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(mentor_bp, url_prefix='/api')

# Database initialization will be done after functions are defined

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    print("Please set OPENAI_API_KEY in your environment or .env file")

# Database-based storage is now configured

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

def get_mentor_templates():
    system_prompts = get_mentor_system_prompts()
    
    return [
        {
            'id': 'startup-advisor',
            'name': 'Startup Strategy Advisor',
            'category': 'Business',
            'description': 'Expert guidance for launching and scaling startups',
            'personality': 'Strategic, encouraging, data-driven',
            'gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': system_prompts['startup-advisor']
        },
        {
            'id': 'sales-coach',
            'name': 'Sales Performance Coach',
            'category': 'Business',
            'description': 'Master the art of selling and relationship building',
            'personality': 'Motivational, practical, results-focused',
            'gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': system_prompts['sales-coach']
        },
        {
            'id': 'leadership-mentor',
            'name': 'Leadership Development Mentor',
            'category': 'Business',
            'description': 'Develop authentic leadership skills and team management',
            'personality': 'Wise, supportive, challenging',
            'gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': system_prompts['leadership-mentor']
        },
        {
            'id': 'marketing-strategist',
            'name': 'Digital Marketing Strategist',
            'category': 'Business',
            'description': 'Navigate modern marketing channels and customer acquisition',
            'personality': 'Creative, analytical, trend-aware',
            'gradient': 'from-emerald-500 to-teal-700',
            'system_prompt': system_prompts['marketing-strategist']
        },
        {
            'id': 'study-coach',
            'name': 'Study Skills Coach',
            'category': 'Education',
            'description': 'Optimize learning techniques and academic performance',
            'personality': 'Patient, methodical, encouraging',
            'gradient': 'from-amber-500 to-orange-700',
            'system_prompt': system_prompts['study-coach']
        },
        {
            'id': 'career-counselor',
            'name': 'Career Development Counselor',
            'category': 'Education',
            'description': 'Navigate career transitions and professional growth',
            'personality': 'Insightful, supportive, forward-thinking',
            'gradient': 'from-amber-500 to-orange-700',
            'system_prompt': system_prompts['career-counselor']
        },
        {
            'id': 'creative-writing-mentor',
            'name': 'Creative Writing Mentor',
            'category': 'Creative',
            'description': 'Craft compelling stories and develop your unique voice',
            'personality': 'Imaginative, encouraging, literary',
            'gradient': 'from-pink-500 to-rose-700',
            'system_prompt': system_prompts['creative-writing-mentor']
        },
        {
            'id': 'coding-mentor',
            'name': 'Programming Mentor',
            'category': 'Technology',
            'description': 'Learn to code with personalized guidance and projects',
            'personality': 'Logical, patient, problem-solving focused',
            'gradient': 'from-blue-500 to-indigo-700',
            'system_prompt': system_prompts['coding-mentor']
        },
        {
            'id': 'mindfulness-guide',
            'name': 'Mindfulness & Meditation Guide',
            'category': 'Wellness',
            'description': 'Find inner peace and develop mindful awareness',
            'personality': 'Calm, wise, present-focused',
            'gradient': 'from-purple-500 to-violet-700',
            'system_prompt': system_prompts['mindfulness-guide']
        }
    ]

def get_ai_response(mentor_id, user_message, conversation_history):
    """Get AI response using OpenAI API via requests"""
    try:
        # Get mentor template
        templates = get_mentor_templates()
        mentor = next((t for t in templates if t['id'] == mentor_id), None)
        
        if not mentor:
            return "I'm sorry, I couldn't find the mentor information. Please try again."
        
        # Build conversation messages
        messages = [
            {"role": "system", "content": mentor['system_prompt']}
        ]
        
        # Add conversation history (last 10 messages to stay within token limits)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add current user message
        messages.append({
            "role": "user", 
            "content": user_message
        })
        
        # Call OpenAI API using requests
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"OpenAI API Error: {response.status_code} - {response.text}")
            raise Exception(f"API Error: {response.status_code}")
        
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        # Return a more helpful error message that still maintains mentor personality
        templates = get_mentor_templates()
        mentor = next((t for t in templates if t['id'] == mentor_id), None)
        
        if mentor and 'startup' in mentor_id:
            return "I'm experiencing a brief technical hiccup, but I'm here to help with your startup journey. What specific challenge are you facing with your business right now?"
        elif mentor and 'sales' in mentor_id:
            return "Technical glitch on my end, but let's keep the momentum going! What sales challenge can I help you tackle today?"
        elif mentor and 'leadership' in mentor_id:
            return "I'm having a momentary technical issue, but leadership is about adapting to challenges. What leadership situation would you like to discuss?"
        else:
            return f"I'm experiencing some technical difficulties, but I'm committed to helping you grow. Could you tell me more about what you'd like to work on today?"

# Legacy API fallback for routes not handled by blueprints
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_fallback(path):
    return jsonify({'success': False, 'error': 'API endpoint not found'}), 404

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

# Initialize database tables and default data
def initialize_database():
    with app.app_context():
        db.create_all()
        
        # Add default mentor templates if they don't exist
        if MentorTemplate.query.count() == 0:
            system_prompts = get_mentor_system_prompts()
            default_templates = [
                {
                    'template_id': 'startup-advisor',
                    'name': 'Startup Strategy Advisor',
                    'category': 'business',
                    'description': 'Expert guidance for entrepreneurs building successful startups',
                    'personality': 'Strategic, encouraging, and data-driven',
                    'system_prompt': system_prompts['startup-advisor'],
                    'icon': '🚀',
                    'color_gradient': 'from-blue-500 to-purple-600'
                },
                {
                    'template_id': 'sales-coach',
                    'name': 'Sales Performance Coach',
                    'category': 'business',
                    'description': 'High-performance sales coaching for B2B and B2C',
                    'personality': 'Motivational, practical, and results-focused',
                    'system_prompt': system_prompts['sales-coach'],
                    'icon': '💼',
                    'color_gradient': 'from-green-500 to-blue-600'
                },
                {
                    'template_id': 'leadership-mentor',
                    'name': 'Leadership Development Mentor',
                    'category': 'leadership',
                    'description': 'Executive coaching and organizational development',
                    'personality': 'Wise, supportive, and challenging',
                    'system_prompt': system_prompts['leadership-mentor'],
                    'icon': '👑',
                    'color_gradient': 'from-purple-500 to-pink-600'
                },
                {
                    'template_id': 'marketing-strategist',
                    'name': 'Digital Marketing Strategist',
                    'category': 'marketing',
                    'description': 'Modern marketing channels and customer acquisition',
                    'personality': 'Creative, analytical, and trend-aware',
                    'system_prompt': system_prompts['marketing-strategist'],
                    'icon': '📈',
                    'color_gradient': 'from-orange-500 to-red-600'
                },
                {
                    'template_id': 'study-coach',
                    'name': 'Study Skills Coach',
                    'category': 'education',
                    'description': 'Optimize learning techniques and academic performance',
                    'personality': 'Patient, methodical, and encouraging',
                    'system_prompt': system_prompts['study-coach'],
                    'icon': '📚',
                    'color_gradient': 'from-indigo-500 to-blue-600'
                },
                {
                    'template_id': 'career-counselor',
                    'name': 'Career Development Counselor',
                    'category': 'career',
                    'description': 'Navigate career transitions and professional growth',
                    'personality': 'Insightful, supportive, and forward-thinking',
                    'system_prompt': system_prompts['career-counselor'],
                    'icon': '🎯',
                    'color_gradient': 'from-teal-500 to-green-600'
                },
                {
                    'template_id': 'creative-writing-mentor',
                    'name': 'Creative Writing Mentor',
                    'category': 'creative',
                    'description': 'Develop storytelling skills and authentic voice',
                    'personality': 'Imaginative, encouraging, and literary',
                    'system_prompt': system_prompts['creative-writing-mentor'],
                    'icon': '✍️',
                    'color_gradient': 'from-pink-500 to-purple-600'
                },
                {
                    'template_id': 'coding-mentor',
                    'name': 'Programming Mentor',
                    'category': 'technology',
                    'description': 'Software development and technical education',
                    'personality': 'Logical, patient, and problem-solving focused',
                    'system_prompt': system_prompts['coding-mentor'],
                    'icon': '💻',
                    'color_gradient': 'from-gray-500 to-blue-600'
                }
            ]
            
            for template_data in default_templates:
                template = MentorTemplate(**template_data)
                db.session.add(template)
            
            db.session.commit()
            print("Default mentor templates added to database")

if __name__ == '__main__':
    initialize_database()
    app.run(host='0.0.0.0', port=5000, debug=True)