from flask import Blueprint, request, jsonify, Response, stream_template
from flask_cors import cross_origin
from src.models.mentor import MentorTemplate, CustomMentor, Conversation, Message, UserProgress, UserGoal, db
from src.models.user import User
from src.services.ai_service import ai_service
from datetime import datetime
import json

mentor_bp = Blueprint('mentor', __name__)

# Mentor Templates Routes
@mentor_bp.route('/mentor-templates', methods=['GET'])
@cross_origin()
def get_mentor_templates():
    """Get all available mentor templates"""
    try:
        templates = MentorTemplate.query.all()
        return jsonify({
            'success': True,
            'templates': [template.to_dict() for template in templates]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@mentor_bp.route('/mentor-templates/<template_id>', methods=['GET'])
@cross_origin()
def get_mentor_template(template_id):
    """Get a specific mentor template"""
    try:
        template = MentorTemplate.query.filter_by(template_id=template_id).first()
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        return jsonify({
            'success': True,
            'template': template.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Custom Mentors Routes
@mentor_bp.route('/custom-mentors', methods=['POST'])
@cross_origin()
def create_custom_mentor():
    """Create a new custom mentor"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        # Create system prompt based on user input
        system_prompt = f"""
        You are {data['name']}, a personalized AI mentor created by the user.
        
        MENTOR DESCRIPTION: {data['description']}
        
        CORE PERSONALITY TRAITS:
        - Expertise: {data.get('expertise', 'General knowledge and guidance')}
        - Teaching Style: {data.get('teaching_style', 'Supportive and encouraging')}
        - Communication: {data.get('communication_style', 'Clear and patient')}
        
        COACHING PHILOSOPHY:
        You believe in guiding students to discover insights on their own rather than simply providing answers. 
        You challenge students appropriately based on their level and help them achieve "aha!" moments through 
        thoughtful questioning and scaffolded learning.
        
        INTERACTION GUIDELINES:
        1. Always maintain your unique personality and expertise
        2. Adapt your teaching approach to the student's learning style
        3. Ask probing questions that lead to self-discovery
        4. Provide encouragement and celebrate progress
        5. Challenge students just beyond their comfort zone
        6. Break down complex concepts into manageable steps
        7. Use real-world examples and analogies when helpful
        
        Remember: You are not just an information provider, but a true mentor who cares about the student's 
        growth and development. Guide them on their learning journey with wisdom, patience, and expertise.
        """
        
        mentor = CustomMentor(
            user_id=user_id,
            name=data['name'],
            description=data['description'],
            system_prompt=system_prompt,
            icon=data.get('icon', '🤖'),
            color=data.get('color', '#84cc16')
        )
        
        db.session.add(mentor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'mentor': mentor.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@mentor_bp.route('/custom-mentors/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_custom_mentors(user_id):
    """Get all custom mentors for a user"""
    try:
        mentors = CustomMentor.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'mentors': [mentor.to_dict() for mentor in mentors]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Chat Routes
@mentor_bp.route('/chat/start', methods=['POST'])
@cross_origin()
def start_conversation():
    """Start a new conversation with a mentor"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        mentor_id = data.get('mentor_id')
        mentor_type = data.get('mentor_type')  # 'template' or 'custom'
        
        if not all([user_id, mentor_id, mentor_type]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Get mentor name for conversation title
        if mentor_type == 'template':
            mentor = MentorTemplate.query.filter_by(template_id=mentor_id).first()
            title = f"Chat with {mentor.name}" if mentor else "Chat with AI Mentor"
        else:
            mentor = CustomMentor.query.get(mentor_id)
            title = f"Chat with {mentor.name}" if mentor else "Chat with Custom Mentor"
        
        conversation = Conversation(
            user_id=user_id,
            mentor_id=mentor_id,
            mentor_type=mentor_type,
            title=title
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@mentor_bp.route('/chat/<int:conversation_id>/messages', methods=['GET'])
@cross_origin()
def get_conversation_messages(conversation_id):
    """Get all messages in a conversation"""
    try:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return jsonify({'success': False, 'error': 'Conversation not found'}), 404
        
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
        
        return jsonify({
            'success': True,
            'conversation': conversation.to_dict(),
            'messages': [message.to_dict() for message in messages]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@mentor_bp.route('/chat/<int:conversation_id>/send', methods=['POST'])
@cross_origin()
def send_message():
    """Send a message and get AI response"""
    try:
        conversation_id = request.view_args['conversation_id']
        data = request.get_json()
        user_message = data.get('message')
        stream_response = data.get('stream', False)
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Message required'}), 400
        
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
        
        # Get mentor and system prompt
        if conversation.mentor_type == 'template':
            mentor = MentorTemplate.query.filter_by(template_id=conversation.mentor_id).first()
            system_prompt = mentor.system_prompt if mentor else "You are a helpful AI mentor."
        else:
            mentor = CustomMentor.query.get(conversation.mentor_id)
            system_prompt = mentor.system_prompt if mentor else "You are a helpful AI mentor."
        
        # Get user profile for personalization
        user = User.query.get(conversation.user_id)
        user_profile = {
            'learning_style': user.learning_style if user else 'balanced',
            'communication_preference': user.communication_preference if user else 'encouraging',
            'challenge_level': user.challenge_level if user else 'balanced',
            'current_streak': user.current_streak if user else 0,
            'total_sessions': user.total_sessions if user else 0
        }
        
        # Personalize system prompt
        personalized_prompt = ai_service.create_personalized_system_prompt(system_prompt, user_profile)
        
        # Get conversation history
        previous_messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
        message_history = [{'role': msg.role, 'content': msg.content} for msg in previous_messages]
        
        # Generate AI response
        if stream_response:
            def generate():
                ai_response = ""
                for chunk in ai_service.generate_response(message_history, personalized_prompt, stream=True):
                    ai_response += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                
                # Save AI response to database
                ai_msg = Message(
                    conversation_id=conversation_id,
                    role='assistant',
                    content=ai_response
                )
                db.session.add(ai_msg)
                db.session.commit()
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return Response(generate(), mimetype='text/plain')
        else:
            ai_response = ai_service.generate_response(message_history, personalized_prompt)
            
            # Save AI response
            ai_msg = Message(
                conversation_id=conversation_id,
                role='assistant',
                content=ai_response
            )
            db.session.add(ai_msg)
            
            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'user_message': user_msg.to_dict(),
                'ai_response': ai_msg.to_dict()
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# User Progress Routes
@mentor_bp.route('/progress/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_progress(user_id):
    """Get user's learning progress"""
    try:
        progress = UserProgress.query.filter_by(user_id=user_id).all()
        goals = UserGoal.query.filter_by(user_id=user_id).all()
        user = User.query.get(user_id)
        
        return jsonify({
            'success': True,
            'progress': [p.to_dict() for p in progress],
            'goals': [g.to_dict() for g in goals],
            'stats': user.get_stats() if user else {}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@mentor_bp.route('/progress/<int:user_id>/update', methods=['POST'])
@cross_origin()
def update_user_progress(user_id):
    """Update user's progress in a subject"""
    try:
        data = request.get_json()
        subject = data.get('subject')
        progress_percentage = data.get('progress', 0)
        
        if not subject:
            return jsonify({'success': False, 'error': 'Subject required'}), 400
        
        # Find or create progress record
        progress = UserProgress.query.filter_by(user_id=user_id, subject=subject).first()
        if not progress:
            progress = UserProgress(user_id=user_id, subject=subject)
            db.session.add(progress)
        
        progress.progress_percentage = progress_percentage
        progress.total_sessions += 1
        progress.last_session = datetime.utcnow()
        
        # Update user's total sessions
        user = User.query.get(user_id)
        if user:
            user.total_sessions += 1
            user.last_active = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'progress': progress.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@mentor_bp.route('/goals/<int:user_id>', methods=['POST'])
@cross_origin()
def create_user_goal(user_id):
    """Create a new goal for the user"""
    try:
        data = request.get_json()
        
        goal = UserGoal(
            user_id=user_id,
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'planning'),
            target_date=datetime.fromisoformat(data['target_date']) if data.get('target_date') else None
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'goal': goal.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Conversations Routes
@mentor_bp.route('/conversations/<int:user_id>', methods=['GET'])
@cross_origin()
def get_user_conversations(user_id):
    """Get all conversations for a user"""
    try:
        conversations = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.updated_at.desc()).all()
        
        return jsonify({
            'success': True,
            'conversations': [conv.to_dict() for conv in conversations]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

