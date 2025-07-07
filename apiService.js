// Determine the correct API base URL based on environment
const getApiBaseUrl = () => {
  // If we're in development (localhost), use localhost
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:5000/api';
  }
  // If we're in production, use the same domain as the frontend
  return `${window.location.protocol}//${window.location.host}/api`;
};

const API_BASE_URL = getApiBaseUrl();

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'API request failed');
      }
      
      return data;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  // User Management
  async createUser(userData) {
    return this.request('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getUser(userId) {
    return this.request(`/users/${userId}`);
  }

  async updateUser(userId, userData) {
    return this.request(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  // Mentor Templates
  async getMentorTemplates() {
    return this.request('/mentor-templates');
  }

  async getMentorTemplate(templateId) {
    return this.request(`/mentor-templates/${templateId}`);
  }

  // Custom Mentors
  async createCustomMentor(mentorData) {
    return this.request('/custom-mentors', {
      method: 'POST',
      body: JSON.stringify(mentorData),
    });
  }

  async getUserCustomMentors(userId) {
    return this.request(`/custom-mentors/${userId}`);
  }

  // Conversations
  async startConversation(conversationData) {
    return this.request('/chat/start', {
      method: 'POST',
      body: JSON.stringify(conversationData),
    });
  }

  async getConversationMessages(conversationId) {
    return this.request(`/chat/${conversationId}/messages`);
  }

  async sendMessage(conversationId, message, stream = false) {
    return this.request(`/chat/${conversationId}/send`, {
      method: 'POST',
      body: JSON.stringify({ message, stream }),
    });
  }

  async getUserConversations(userId) {
    return this.request(`/conversations/${userId}`);
  }

  // Progress Tracking
  async getUserProgress(userId) {
    return this.request(`/progress/${userId}`);
  }

  async updateUserProgress(userId, progressData) {
    return this.request(`/progress/${userId}/update`, {
      method: 'POST',
      body: JSON.stringify(progressData),
    });
  }

  // Goals
  async createUserGoal(userId, goalData) {
    return this.request(`/goals/${userId}`, {
      method: 'POST',
      body: JSON.stringify(goalData),
    });
  }

  // Demo data creation
  async createDemoUser() {
    const demoUser = {
      username: 'demo_user',
      email: 'demo@makementors.io',
      full_name: 'Demo User',
      learning_style: 'balanced',
      communication_preference: 'encouraging',
      challenge_level: 'balanced'
    };

    try {
      const response = await this.createUser(demoUser);
      return response.user;
    } catch (error) {
      // If user already exists, try to get existing user
      console.log('Demo user might already exist, attempting to fetch...');
      return null;
    }
  }

  async initializeDemoData(userId) {
    // Create some demo progress
    const subjects = [
      { subject: 'Python Programming', progress: 75 },
      { subject: 'Business Strategy', progress: 60 },
      { subject: 'Creative Writing', progress: 40 }
    ];

    for (const subjectData of subjects) {
      try {
        await this.updateUserProgress(userId, subjectData);
      } catch (error) {
        console.error('Error creating demo progress:', error);
      }
    }

    // Create some demo goals
    const goals = [
      {
        title: 'Build a Web Application',
        description: 'Complete a full-stack project using React and Node.js',
        status: 'in_progress',
        target_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      },
      {
        title: 'Write 10,000 Words',
        description: 'Complete a short story collection',
        status: 'planning',
        target_date: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      }
    ];

    for (const goalData of goals) {
      try {
        await this.createUserGoal(userId, goalData);
      } catch (error) {
        console.error('Error creating demo goal:', error);
      }
    }
  }
}

export const apiService = new ApiService();

