import os
import openai
from typing import List, Dict, Any, Generator
import json
from datetime import datetime

class AIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
        )
        self.model = "gpt-4o-mini"
    
    def create_personalized_system_prompt(self, base_prompt: str, user_profile: Dict[str, Any]) -> str:
        """
        Enhance the base mentor prompt with user-specific personalization
        """
        personalization = f"""
        
PERSONALIZATION CONTEXT:
- User's learning style: {user_profile.get('learning_style', 'balanced')}
- Communication preference: {user_profile.get('communication_preference', 'encouraging')}
- Challenge level: {user_profile.get('challenge_level', 'balanced')}
- Current streak: {user_profile.get('current_streak', 0)} days
- Total sessions: {user_profile.get('total_sessions', 0)}

ADAPTIVE COACHING INSTRUCTIONS:
1. LEARNING STYLE ADAPTATION:
   - Visual learners: Use analogies, mental models, and suggest visual aids
   - Auditory learners: Encourage discussion, verbal repetition, and sound-based mnemonics
   - Kinesthetic learners: Suggest hands-on practice, physical movement, and experiential learning
   - Reading/Writing learners: Provide written summaries, note-taking strategies, and text-based exercises

2. COMMUNICATION ADAPTATION:
   - Formal: Use professional language, structured responses, and academic tone
   - Casual: Use friendly, conversational language with appropriate humor
   - Encouraging: Focus on positive reinforcement, celebrate small wins, build confidence
   - Direct: Be concise, straightforward, and focus on actionable advice

3. CHALLENGE CALIBRATION:
   - Gentle: Provide smaller steps, more support, frequent check-ins
   - Balanced: Mix challenging and supportive elements, moderate pacing
   - Intensive: Push boundaries, accelerated learning, higher expectations

4. SOCRATIC METHOD IMPLEMENTATION:
   - Ask thought-provoking questions that lead to self-discovery
   - Guide users to their own "aha!" moments rather than giving direct answers
   - Use the "5 Whys" technique to deepen understanding
   - Encourage critical thinking and reflection

5. PROGRESSIVE DIFFICULTY:
   - Start with current knowledge level and gradually increase complexity
   - Monitor comprehension and adjust difficulty in real-time
   - Provide scaffolding when needed, remove it as competence grows
   - Challenge users just beyond their comfort zone (Zone of Proximal Development)

6. EMOTIONAL INTELLIGENCE:
   - Recognize signs of frustration, confusion, or disengagement
   - Provide appropriate encouragement and motivation
   - Celebrate breakthroughs and progress milestones
   - Maintain patience and supportive presence throughout the journey

Remember: Your goal is to be the mentor this specific user needs, adapting your approach based on their unique profile while maintaining your core personality and expertise.
        """
        
        return base_prompt + personalization
    
    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str, stream: bool = False) -> str:
        """
        Generate AI response using OpenAI API
        """
        try:
            formatted_messages = [{"role": "system", "content": system_prompt}]
            formatted_messages.extend(messages)
            
            if stream:
                return self._stream_response(formatted_messages)
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=formatted_messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "I apologize, but I'm experiencing some technical difficulties. Please try again in a moment."
    
    def _stream_response(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Stream AI response for real-time chat experience
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"Error streaming AI response: {e}")
            yield "I apologize, but I'm experiencing some technical difficulties. Please try again in a moment."
    
    def analyze_conversation_for_insights(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze conversation to extract learning insights and progress indicators
        """
        try:
            analysis_prompt = """
            Analyze this conversation between a mentor and student. Provide insights in JSON format:
            {
                "learning_progress": "description of student's progress",
                "key_concepts_covered": ["concept1", "concept2"],
                "areas_of_strength": ["strength1", "strength2"],
                "areas_for_improvement": ["area1", "area2"],
                "engagement_level": "high/medium/low",
                "comprehension_level": "high/medium/low",
                "suggested_next_steps": ["step1", "step2"],
                "breakthrough_moments": ["moment1", "moment2"]
            }
            """
            
            conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": analysis_prompt},
                    {"role": "user", "content": conversation_text}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error analyzing conversation: {e}")
            return {
                "learning_progress": "Analysis unavailable",
                "key_concepts_covered": [],
                "areas_of_strength": [],
                "areas_for_improvement": [],
                "engagement_level": "medium",
                "comprehension_level": "medium",
                "suggested_next_steps": [],
                "breakthrough_moments": []
            }
    
    def generate_learning_path(self, subject: str, current_level: str, goals: List[str]) -> List[Dict[str, Any]]:
        """
        Generate a personalized learning path based on subject, level, and goals
        """
        try:
            path_prompt = f"""
            Create a personalized learning path for:
            Subject: {subject}
            Current Level: {current_level}
            Goals: {', '.join(goals)}
            
            Provide a structured learning path in JSON format with 8-12 steps:
            {{
                "learning_path": [
                    {{
                        "step": 1,
                        "title": "Step Title",
                        "description": "What the student will learn",
                        "estimated_duration": "time estimate",
                        "key_concepts": ["concept1", "concept2"],
                        "practical_exercises": ["exercise1", "exercise2"],
                        "success_criteria": ["criteria1", "criteria2"]
                    }}
                ]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": path_prompt}],
                temperature=0.5,
                max_tokens=1500
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating learning path: {e}")
            return {"learning_path": []}

# Initialize the AI service
ai_service = AIService()

