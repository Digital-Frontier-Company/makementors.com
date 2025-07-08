from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(200))
    avatar_url = db.Column(db.String(500))
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    total_sessions = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    
    # Learning preferences
    learning_style = db.Column(db.String(50))  # 'visual', 'auditory', 'kinesthetic', 'reading'
    communication_preference = db.Column(db.String(50))  # 'formal', 'casual', 'encouraging', 'direct'
    challenge_level = db.Column(db.String(50), default='balanced')  # 'gentle', 'balanced', 'intensive'
    
    # Relationships
    custom_mentors = db.relationship('CustomMentor', backref='user', lazy=True, cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('UserProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('UserGoal', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'total_sessions': self.total_sessions,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'learning_style': self.learning_style,
            'communication_preference': self.communication_preference,
            'challenge_level': self.challenge_level
        }
    
    def get_stats(self):
        completed_goals = len([g for g in self.goals if g.status == 'completed'])
        active_goals = len([g for g in self.goals if g.status in ['planning', 'in_progress']])
        
        return {
            'total_sessions': self.total_sessions,
            'current_streak': self.current_streak,
            'completed_goals': completed_goals,
            'active_goals': active_goals
        }

