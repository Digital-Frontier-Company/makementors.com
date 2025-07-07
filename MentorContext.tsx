import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

export interface MentorType {
  id: string;
  name: string;
  icon: string;
  description: string;
  gradient: string;
  category: string;
  expertise: string;
  learningPath: Array<{
    name: string;
  }>;
}

export interface UserPreferences {
  name: string;
  goal: string;
  experience: 'Beginner' | 'Intermediate' | 'Advanced';
  mentorName?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

// Update the interface to include mentor_type
interface ChatSession {
  id: string;
  name: string;
  mentor_id: string;
  mentor_type: string;
}

interface MentorContextType {
  currentStep: 'select' | 'customize' | 'chat';
  mentors: MentorType[];
  userMentors: MentorType[];
  selectedMentor: MentorType | null;
  userPreferences: UserPreferences;
  messages: Message[];
  isTyping: boolean;
  chatSessionId: string | null;
  setCurrentStep: (step: 'select' | 'customize' | 'chat') => void;
  setSelectedMentor: (mentor: MentorType) => void;
  setUserPreferences: (preferences: UserPreferences) => void;
  addMessage: (content: string, role: 'user' | 'assistant') => void;
  setIsTyping: (isTyping: boolean) => void;
  resetChat: () => void;
  loadChatSession: (sessionId: string) => Promise<boolean>;
  userSessions: ChatSession[];
  refreshUserSessions: () => Promise<void>;
  setChatSessionId: (id: string | null) => void;
  createCustomMentor: (mentorData: { name: string, description: string, icon: string, color: string, customPrompt?: string }) => Promise<MentorType | null>;
  loadUserMentors: () => Promise<void>;
  refreshMentorTemplates: () => Promise<void>;
}

export const MentorContext = createContext<MentorContextType | null>(null);

export const MentorProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentStep, setCurrentStep] = useState<'select' | 'customize' | 'chat'>('select');
  const [selectedMentor, setSelectedMentor] = useState<MentorType | null>(null);
  const [userPreferences, setUserPreferences] = useState<UserPreferences>({
    name: '',
    goal: '',
    experience: 'Beginner',
    mentorName: ''
  });
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [userSessions, setUserSessions] = useState<ChatSession[]>([]);
  const [userMentors, setUserMentors] = useState<MentorType[]>([]);
  const [mentors, setMentors] = useState<MentorType[]>([]);
  const { user } = useAuth();
  const { toast } = useToast();

  // Load initial data when component mounts or user changes
  useEffect(() => {
    refreshMentorTemplates();
    
    if (user) {
      refreshUserSessions();
      loadUserMentors();
    }
  }, [user]);

  // Enhanced mentor template loading with better error handling and logging
  const refreshMentorTemplates = async () => {
    try {
      console.log("Loading mentor templates from database...");
      
      const { data, error } = await supabase
        .from('mentor_templates')
        .select('*')
        .order('category, display_name');
      
      if (error) {
        console.error("Error loading mentor templates:", error);
        throw error;
      }
      
      console.log("Raw mentor templates data:", data);
      
      if (data && data.length > 0) {
        // Transform to MentorType format with better field mapping
        const transformedMentors = data.map(template => {
          const mentor = {
            id: template.template_id,
            name: template.display_name || template.default_mentor_name || 'Unnamed Mentor',
            icon: template.icon || '🧠',
            description: template.description_for_user || 'No description available',
            gradient: getCategoryGradient(template.category),
            category: template.category || 'general',
            expertise: template.default_mentor_name || template.display_name || 'General Expertise',
            learningPath: generateLearningPath(template.category || 'general'),
          };
          
          console.log(`Processed mentor template: ${mentor.name} (${mentor.id})`);
          return mentor;
        });
        
        console.log(`Successfully loaded ${transformedMentors.length} mentor templates`);
        setMentors(transformedMentors);
      } else {
        console.log("No mentor templates found in database");
        setMentors([]);
      }
    } catch (error) {
      console.error('Error loading mentor templates:', error);
      toast({
        title: "Error loading mentor templates",
        description: "Failed to load mentor templates from database. Using fallback data.",
        variant: "destructive",
      });
      
      // Set empty array as fallback
      setMentors([]);
    }
  };

  const refreshUserSessions = async () => {
    if (!user) return;
    
    try {
      const { data, error } = await supabase
        .from('chat_sessions')
        .select('id, name, mentor_id, mentor_type')
        .eq('user_id', user.id)
        .order('updated_at', { ascending: false });
      
      if (error) throw error;
      
      // The mentor_type column now exists in the database
      const sessionsWithType = data || [];
      
      setUserSessions(sessionsWithType);
    } catch (error) {
      console.error('Error loading user sessions:', error);
      toast({
        title: "Error",
        description: "Failed to load your previous chat sessions",
        variant: "destructive",
      });
    }
  };

  const loadUserMentors = async () => {
    if (!user) return;
    
    try {
      const { data, error } = await supabase
        .from('mentors')
        .select('*')
        .eq('user_id', user.id);
        
      if (error) throw error;
      
      if (data && data.length > 0) {
        // Transform to MentorType format
        const transformedMentors = data.map(mentor => ({
          id: mentor.id,
          name: mentor.name,
          icon: mentor.avatar_url || '🧠', // Use avatar_url as icon or default to 🧠 emoji
          description: mentor.description,
          gradient: getCategoryGradient('custom'), // Custom gradient for user mentors
          category: 'custom',
          expertise: mentor.name,
          learningPath: [], // Empty learning path for custom mentors
        }));
        
        setUserMentors(transformedMentors);
      }
    } catch (error) {
      console.error('Error loading user mentors:', error);
      toast({
        title: "Error",
        description: "Failed to load your custom mentors",
        variant: "destructive",
      });
    }
  };

  const createCustomMentor = async (mentorData: { 
    name: string, 
    description: string, 
    icon: string, 
    color: string,
    customPrompt?: string 
  }): Promise<MentorType | null> => {
    if (!user) {
      toast({
        title: "Authentication required",
        description: "Please sign in to create a custom mentor",
        variant: "destructive",
      });
      return null;
    }
    
    try {
      // Call our edge function to create the mentor
      const response = await fetch('https://bapditcjlxctrisoixpg.supabase.co/functions/v1/create-mentor', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`
        },
        body: JSON.stringify({
          name: mentorData.name,
          description: mentorData.description,
          icon: mentorData.icon,
          color: mentorData.color,
          customPrompt: mentorData.customPrompt,
          userId: user.id
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create mentor');
      }
      
      const { mentor } = await response.json();
      
      if (!mentor) {
        throw new Error('No mentor data returned');
      }
      
      // Format the mentor to match our MentorType
      const newMentor: MentorType = {
        id: mentor.id,
        name: mentor.name,
        icon: mentor.icon || '🧠',
        description: mentor.description,
        gradient: getCategoryGradient('custom'),
        category: 'custom',
        expertise: mentor.name,
        learningPath: [],
      };
      
      // Add to our userMentors state
      setUserMentors(prev => [...prev, newMentor]);
      
      toast({
        title: "Success!",
        description: "Your custom mentor has been created",
        variant: "default",
      });
      
      return newMentor;
    } catch (error) {
      console.error('Error creating custom mentor:', error);
      toast({
        title: "Failed to create mentor",
        description: error instanceof Error ? error.message : 'An unexpected error occurred',
        variant: "destructive",
      });
      return null;
    }
  };

  const loadChatSession = async (sessionId: string) => {
    if (!user) return false;
    
    try {
      // Get session details
      const { data: sessionData, error: sessionError } = await supabase
        .from('chat_sessions')
        .select('*, mentors(*)')
        .eq('id', sessionId)
        .single();
      
      if (sessionError) throw sessionError;
      
      // Get messages for this session
      const { data: messagesData, error: messagesError } = await supabase
        .from('chat_messages')
        .select('*')
        .eq('chat_session_id', sessionId)
        .order('created_at', { ascending: true });
      
      if (messagesError) throw messagesError;
      
      // Use mentor_type from the database, with fallback to inference if needed
      let mentorType = sessionData.mentor_type || 'template';
      
      // If still null or undefined, try to infer
      if (!mentorType && await isMentorCustom(sessionData.mentor_id)) {
        mentorType = 'custom';
      }
      
      // Determine mentor data based on mentor type
      let mentor: MentorType;
      
      // Check if this is a template mentor
      if (mentorType === 'template') {
        // Try to get the mentor template
        const { data: template, error: templateError } = await supabase
          .from('mentor_templates')
          .select('*')
          .eq('template_id', sessionData.mentor_id)
          .single();
        
        if (templateError && !templateError.message.includes("No rows found")) {
          console.error('Error loading template mentor:', templateError);
        }
        
        if (template) {
          mentor = {
            id: template.template_id,
            name: template.display_name,
            icon: template.icon,
            description: template.description_for_user,
            gradient: getCategoryGradient(template.category),
            category: template.category,
            expertise: template.default_mentor_name,
            learningPath: generateLearningPath(template.category),
          };
        } else {
          // Fallback if template not found
          mentor = {
            id: sessionData.mentor_id,
            name: sessionData.name || 'Unknown Mentor',
            icon: '🤖',
            description: 'Description not available',
            gradient: 'from-gray-500 to-gray-700',
            category: 'unknown',
            expertise: 'Unknown',
            learningPath: [],
          };
        }
      } else {
        // This is a custom mentor
        if (sessionData.mentors) {
          mentor = {
            id: sessionData.mentor_id,
            name: sessionData.mentors.name,
            icon: sessionData.mentors.avatar_url || '🤖',
            description: sessionData.mentors.description,
            gradient: getCategoryGradient('custom'),
            category: 'custom',
            expertise: sessionData.mentors.name,
            learningPath: [],
          };
        } else {
          // Fallback if mentor not found
          mentor = {
            id: sessionData.mentor_id,
            name: sessionData.name?.replace('Chat with ', '') || 'Custom Mentor',
            icon: '🤖',
            description: 'Custom mentor',
            gradient: getCategoryGradient('custom'),
            category: 'custom',
            expertise: 'Custom expertise',
            learningPath: [],
          };
        }
      }
      
      // Format messages
      const formattedMessages = messagesData ? messagesData.map((msg) => ({
        id: msg.id,
        role: msg.role as 'user' | 'assistant',
        content: msg.content
      })) : [];
      
      // Update state
      setSelectedMentor(mentor);
      setMessages(formattedMessages);
      setChatSessionId(sessionId);
      setCurrentStep('chat');
      
      return true;
    } catch (error) {
      console.error('Error loading chat session:', error);
      toast({
        title: "Error",
        description: "Failed to load the chat session",
        variant: "destructive",
      });
      return false;
    }
  };

  // Helper function to check if a mentor is custom
  const isMentorCustom = async (mentorId: string): Promise<boolean> => {
    try {
      const { data, error } = await supabase
        .from('mentors')
        .select('id')
        .eq('id', mentorId)
        .single();
      
      if (error || !data) {
        return false;
      }
      return true;
    } catch (error) {
      return false;
    }
  };

  const addMessage = async (content: string, role: 'user' | 'assistant') => {
    if (!content.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      role,
      content
    };

    // Add to local state
    setMessages(prev => [...prev, newMessage]);

    // If authenticated, save to database
    if (user && chatSessionId) {
      try {
        const { error } = await supabase
          .from('chat_messages')
          .insert({
            chat_session_id: chatSessionId,
            user_id: user.id,
            role,
            content
          });
        
        if (error) throw error;
      } catch (error) {
        console.error('Error saving message:', error);
        toast({
          title: "Warning",
          description: "Message saved locally but failed to sync to cloud",
          variant: "default",
        });
      }
    }
  };

  const resetChat = async () => {
    setMessages([]);
    setCurrentStep('select');
    setSelectedMentor(null);
    setChatSessionId(null);
    setUserPreferences({
      name: '',
      goal: '',
      experience: 'Beginner',
      mentorName: ''
    });
  };

  // Helper function for mentor templates
  const getCategoryGradient = (category: string) => {
    switch (category) {
      case 'technology': return 'from-violet-500 to-purple-700';
      case 'business': return 'from-emerald-500 to-teal-700';
      case 'creative': return 'from-pink-500 to-rose-700';
      case 'language': return 'from-blue-500 to-indigo-700';
      case 'education': return 'from-amber-500 to-orange-700';
      case 'finance': return 'from-green-500 to-emerald-700';
      case 'custom': return 'from-lime-500 to-lime-700';
      default: return 'from-gray-500 to-gray-700';
    }
  };

  // Generate sample learning paths based on category
  const generateLearningPath = (category: string) => {
    const paths: Record<string, Array<{name: string}>> = {
      'technology': [
        { name: 'Programming Basics' },
        { name: 'Data Structures' },
        { name: 'Algorithms' },
        { name: 'Object-Oriented Programming' },
        { name: 'File Handling' },
        { name: 'Error Handling' },
        { name: 'Modules & Packages' },
        { name: 'Project Development' },
      ],
      'business': [
        { name: 'Goal Setting' },
        { name: 'Time Management' },
        { name: 'Habit Formation' },
        { name: 'Task Prioritization' },
        { name: 'Focus Techniques' },
        { name: 'Progress Tracking' },
        { name: 'Accountability Systems' },
        { name: 'Continuous Improvement' },
      ],
      'creative': [
        { name: 'Creative Foundations' },
        { name: 'Story Structure' },
        { name: 'Character Development' },
        { name: 'Scene Building' },
        { name: 'Dialog Techniques' },
        { name: 'Plot Development' },
        { name: 'Editing Skills' },
        { name: 'Publishing Guidance' },
      ],
      'language': [
        { name: 'Basic Vocabulary' },
        { name: 'Common Phrases' },
        { name: 'Grammar Fundamentals' },
        { name: 'Conversation Practice' },
        { name: 'Listening Skills' },
        { name: 'Reading Comprehension' },
        { name: 'Cultural Context' },
        { name: 'Advanced Expression' },
      ],
      'education': [
        { name: 'Key Events & Figures' },
        { name: 'Historical Context' },
        { name: 'Cultural Developments' },
        { name: 'Political Systems' },
        { name: 'Economic Factors' },
        { name: 'Social Movements' },
        { name: 'Technological Advances' },
        { name: 'Historical Analysis' },
      ],
      'finance': [
        { name: 'Market Fundamentals' },
        { name: 'Risk Assessment' },
        { name: 'Technical Analysis' },
        { name: 'Portfolio Theory' },
        { name: 'Risk Management' },
        { name: 'Trading Psychology' },
        { name: 'Advanced Strategies' },
        { name: 'Performance Review' },
      ],
    };
    
    return paths[category] || paths['technology'];
  };

  return (
    <MentorContext.Provider
      value={{
        currentStep,
        mentors,
        userMentors,
        selectedMentor,
        userPreferences,
        messages,
        isTyping,
        chatSessionId,
        setCurrentStep,
        setSelectedMentor,
        setUserPreferences,
        addMessage,
        setIsTyping,
        resetChat,
        loadChatSession,
        userSessions,
        refreshUserSessions,
        setChatSessionId,
        createCustomMentor,
        loadUserMentors,
        refreshMentorTemplates,
      }}
    >
      {children}
    </MentorContext.Provider>
  );
};

export const useMentor = () => {
  const context = useContext(MentorContext);
  if (!context) {
    throw new Error('useMentor must be used within a MentorProvider');
  }
  return context;
};
