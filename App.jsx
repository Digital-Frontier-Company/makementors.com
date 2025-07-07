import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Avatar, AvatarFallback } from '@/components/ui/avatar.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  Brain, 
  MessageCircle, 
  User, 
  Settings, 
  TrendingUp, 
  BookOpen, 
  Palette, 
  DollarSign, 
  Globe, 
  Code, 
  Heart,
  Sparkles,
  Target,
  Award,
  Clock,
  BarChart3,
  Loader2
} from 'lucide-react'
import { apiService } from './services/apiService.js'
import logoTransparent from './assets/logo-transparent.png'
import logoNavy from './assets/logo-navy.png'
import astronautRocket from './assets/astronaut-rocket.png'
import astronautsTeam from './assets/astronauts-team.png'
import astronautsProgression from './assets/astronauts-progression.png'
import astronautsSpace from './assets/astronauts-space.png'
import './App.css'

// Main App Component
function App() {
  const [currentUser, setCurrentUser] = useState(null)
  const [selectedMentor, setSelectedMentor] = useState(null)
  const [currentView, setCurrentView] = useState('home') // home, mentors, chat, profile
  const [mentorTemplates, setMentorTemplates] = useState([])
  const [userProgress, setUserProgress] = useState([])
  const [userGoals, setUserGoals] = useState([])
  const [userStats, setUserStats] = useState({})
  const [currentConversation, setCurrentConversation] = useState(null)
  const [chatMessages, setChatMessages] = useState([])
  const [loading, setLoading] = useState(true)
  const [chatLoading, setChatLoading] = useState(false)

  // Initialize app data
  useEffect(() => {
    initializeApp()
  }, [])

  const initializeApp = async () => {
    try {
      setLoading(true)
      
      // Create or get demo user
      let user = await apiService.createDemoUser()
      if (!user) {
        // If demo user creation failed, create a mock user for demo
        user = {
          id: 1,
          username: 'demo_user',
          email: 'demo@makementors.io',
          full_name: 'Demo User',
          join_date: '2024-01-15T00:00:00',
          total_sessions: 24,
          current_streak: 7,
          learning_style: 'balanced',
          communication_preference: 'encouraging',
          challenge_level: 'balanced'
        }
      }
      
      setCurrentUser(user)
      
      // Initialize demo data if user was just created
      if (user.id) {
        await apiService.initializeDemoData(user.id)
      }
      
      // Load mentor templates
      const templatesResponse = await apiService.getMentorTemplates()
      if (templatesResponse.success) {
        setMentorTemplates(templatesResponse.templates)
      }
      
      // Load user progress and goals
      if (user.id) {
        await loadUserData(user.id)
      }
      
    } catch (error) {
      console.error('Error initializing app:', error)
      // Set fallback data for demo
      setCurrentUser({
        id: 1,
        username: 'demo_user',
        full_name: 'Demo User',
        email: 'demo@makementors.io',
        join_date: '2024-01-15T00:00:00',
        total_sessions: 24,
        current_streak: 7
      })
      setMentorTemplates(getMockMentorTemplates())
    } finally {
      setLoading(false)
    }
  }

  const loadUserData = async (userId) => {
    try {
      const progressResponse = await apiService.getUserProgress(userId)
      if (progressResponse.success) {
        setUserProgress(progressResponse.progress || [])
        setUserGoals(progressResponse.goals || [])
        setUserStats(progressResponse.stats || {})
      }
    } catch (error) {
      console.error('Error loading user data:', error)
      // Set fallback data
      setUserProgress([
        { subject: 'Python Programming', progress: 75, total_sessions: 12 },
        { subject: 'Business Strategy', progress: 60, total_sessions: 8 },
        { subject: 'Creative Writing', progress: 40, total_sessions: 5 }
      ])
      setUserGoals([
        { id: 1, title: 'Build a Web Application', description: 'Complete a full-stack project using React and Node.js', status: 'in_progress' },
        { id: 2, title: 'Write 10,000 Words', description: 'Complete a short story collection', status: 'planning' }
      ])
      setUserStats({ total_sessions: 24, current_streak: 7, completed_goals: 3, active_goals: 2 })
    }
  }

  const getMockMentorTemplates = () => {
    return [
      {
        id: 'startup-advisor',
        name: 'Startup Strategy Advisor',
        category: 'Business',
        description: 'Expert guidance for launching and scaling startups',
        personality: 'Strategic, encouraging, data-driven',
        gradient: 'from-emerald-500 to-teal-700'
      },
      {
        id: 'creative-writing-mentor',
        name: 'Creative Writing Mentor',
        category: 'Creative',
        description: 'Craft compelling stories and develop your unique voice',
        personality: 'Imaginative, encouraging, literary',
        gradient: 'from-pink-500 to-rose-700'
      },
      {
        id: 'coding-mentor',
        name: 'Programming Mentor',
        category: 'Technology',
        description: 'Learn to code with personalized guidance and projects',
        personality: 'Logical, patient, problem-solving focused',
        gradient: 'from-violet-500 to-purple-700'
      }
    ]
  }

  const groupMentorsByCategory = (mentors) => {
    const categories = {}
    mentors.forEach(mentor => {
      if (!categories[mentor.category]) {
        categories[mentor.category] = {
          name: mentor.category,
          mentors: [],
          icon: getCategoryIcon(mentor.category),
          color: getCategoryColor(mentor.category)
        }
      }
      categories[mentor.category].mentors.push(mentor)
    })
    return Object.values(categories)
  }

  const getCategoryIcon = (category) => {
    const icons = {
      'Business': TrendingUp,
      'Education': BookOpen,
      'Creative': Palette,
      'Finance': DollarSign,
      'Language': Globe,
      'Technology': Code,
      'Wellness': Heart
    }
    return icons[category] || Brain
  }

  const getCategoryColor = (category) => {
    const colors = {
      'Business': 'from-emerald-500 to-teal-700',
      'Education': 'from-amber-500 to-orange-700',
      'Creative': 'from-pink-500 to-rose-700',
      'Finance': 'from-green-500 to-emerald-700',
      'Language': 'from-blue-500 to-indigo-700',
      'Technology': 'from-violet-500 to-purple-700',
      'Wellness': 'from-rose-500 to-pink-700'
    }
    return colors[category] || 'from-lime-500 to-green-600'
  }

  const startChatWithMentor = async (mentor) => {
    try {
      setChatLoading(true)
      setSelectedMentor(mentor)
      setCurrentView('chat')
      
      // Start a new conversation
      const conversationData = {
        user_id: currentUser.id,
        mentor_id: mentor.id,
        mentor_type: 'template'
      }
      
      const response = await apiService.startConversation(conversationData)
      if (response.success) {
        setCurrentConversation(response.conversation)
        
        // Load existing messages or start with welcome message
        const messagesResponse = await apiService.getConversationMessages(response.conversation.id)
        if (messagesResponse.success) {
          setChatMessages(messagesResponse.messages || [])
        }
        
        // If no messages, add welcome message
        if (!messagesResponse.messages || messagesResponse.messages.length === 0) {
          const welcomeMessage = {
            role: 'assistant',
            content: `Hello! I'm ${mentor.name}. I'm here to guide you on your learning journey. I believe in challenging you just enough to help you grow, while ensuring you discover insights on your own. What would you like to work on today?`,
            timestamp: new Date().toISOString()
          }
          setChatMessages([welcomeMessage])
        }
      }
    } catch (error) {
      console.error('Error starting chat:', error)
      // Fallback to mock conversation
      setSelectedMentor(mentor)
      setCurrentView('chat')
      setChatMessages([
        {
          role: 'assistant',
          content: `Hello! I'm ${mentor.name}. I'm here to guide you on your learning journey. I believe in challenging you just enough to help you grow, while ensuring you discover insights on your own. What would you like to work on today?`,
          timestamp: new Date().toISOString()
        }
      ])
    } finally {
      setChatLoading(false)
    }
  }

  const sendChatMessage = async (message) => {
    if (!message.trim()) return

    try {
      setChatLoading(true)
      
      // Add user message to chat immediately
      const userMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      }
      setChatMessages(prev => [...prev, userMessage])
      
      // Send message to backend if conversation exists
      if (currentConversation) {
        const response = await apiService.sendMessage(currentConversation.id, message)
        if (response.success && response.ai_response) {
          setChatMessages(prev => [...prev, response.ai_response])
        } else {
          // Add fallback response if API call succeeds but no AI response
          const aiResponse = {
            role: 'assistant',
            content: "Thank you for your message! I'm here to help guide your learning journey. What specific area would you like to focus on today?",
            timestamp: new Date().toISOString()
          }
          setChatMessages(prev => [...prev, aiResponse])
        }
      } else {
        // If no conversation, create a demo response
        const aiResponse = {
          role: 'assistant',
          content: `Thank you for sharing: "${message}". I'm here to help guide your learning journey. While I'm getting my full capabilities set up, I can still provide guidance and support. What specific area would you like to focus on today?`,
          timestamp: new Date().toISOString()
        }
        setChatMessages(prev => [...prev, aiResponse])
      }
    } catch (error) {
      console.error('Error sending message:', error)
      // Add fallback AI response
      const aiResponse = {
        role: 'assistant',
        content: "I appreciate your message! While I'm experiencing some technical difficulties connecting to my full capabilities right now, I'm still here to help guide your learning. Could you tell me more about what specific area you'd like to focus on today?",
        timestamp: new Date().toISOString()
      }
      setChatMessages(prev => [...prev, aiResponse])
    } finally {
      setChatLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="cosmic-bg min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-lime-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Loading Make Mentors</h2>
          <p className="text-gray-300">Preparing your personalized coaching experience...</p>
        </div>
      </div>
    )
  }

  const renderHome = () => (
    <div className="cosmic-bg min-h-screen relative">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-20"
        style={{ backgroundImage: `url(${astronautsProgression})` }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/50 to-background"></div>
      
      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-6 gradient-text">
            Make Mentors
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Create your own AI mentors and coaches for whatever you want to learn or practice. 
            Get personalized guidance that adapts to your learning style and pushes you to achieve breakthrough moments.
          </p>
          <div className="flex gap-4 justify-center">
            <Button 
              size="lg" 
              className="glow-button bg-lime-500 hover:bg-lime-600 text-black font-semibold px-8 py-3"
              onClick={() => setCurrentView('mentors')}
            >
              <Sparkles className="mr-2 h-5 w-5" />
              Explore Mentors
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="border-lime-500 text-lime-500 hover:bg-lime-500 hover:text-black px-8 py-3"
              onClick={() => setCurrentView('profile')}
            >
              <User className="mr-2 h-5 w-5" />
              My Profile
            </Button>
          </div>
        </div>

        {/* How it Works */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Card className="mentor-card bg-card/50 backdrop-blur-sm">
            <CardHeader className="text-center">
              <div className="w-16 h-16 bg-lime-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="h-8 w-8 text-lime-500" />
              </div>
              <CardTitle className="text-xl">Choose Your Path</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300 text-center">
                Select from expertly crafted mentor templates or create your own custom AI coach tailored to your specific goals.
              </p>
            </CardContent>
          </Card>

          <Card className="mentor-card bg-card/50 backdrop-blur-sm">
            <CardHeader className="text-center">
              <div className="w-16 h-16 bg-lime-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="h-8 w-8 text-lime-500" />
              </div>
              <CardTitle className="text-xl">Personalized Coaching</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300 text-center">
                Your mentor adapts to your learning style, challenges you appropriately, and guides you to discover insights on your own.
              </p>
            </CardContent>
          </Card>

          <Card className="mentor-card bg-card/50 backdrop-blur-sm">
            <CardHeader className="text-center">
              <div className="w-16 h-16 bg-lime-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Award className="h-8 w-8 text-lime-500" />
              </div>
              <CardTitle className="text-xl">Track Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-300 text-center">
                Monitor your growth, celebrate achievements, and maintain momentum with detailed progress tracking and insights.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Featured Mentor Categories */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4 text-white">Explore Mentor Categories</h2>
          <p className="text-gray-300 text-lg">Choose from expertly designed mentors across various domains</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {groupMentorsByCategory(mentorTemplates).slice(0, 4).map((category) => {
            const IconComponent = category.icon
            return (
              <Card 
                key={category.name} 
                className="mentor-card bg-card/50 backdrop-blur-sm cursor-pointer"
                onClick={() => setCurrentView('mentors')}
              >
                <CardHeader className="text-center">
                  <div className={`w-16 h-16 bg-gradient-to-br ${category.color} rounded-full flex items-center justify-center mx-auto mb-4`}>
                    <IconComponent className="h-8 w-8 text-white" />
                  </div>
                  <CardTitle className="text-xl">{category.name}</CardTitle>
                  <CardDescription className="text-gray-300">
                    {category.mentors.length} mentors available
                  </CardDescription>
                </CardHeader>
              </Card>
            )
          })}
        </div>

        <div className="text-center mt-12">
          <Button 
            size="lg" 
            variant="outline" 
            className="border-lime-500 text-lime-500 hover:bg-lime-500 hover:text-black"
            onClick={() => setCurrentView('mentors')}
          >
            View All Categories
          </Button>
        </div>
        </div>
      </div>
    </div>
  )

  const renderMentors = () => (
    <div className="cosmic-bg min-h-screen relative">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-15"
        style={{ backgroundImage: `url(${astronautsTeam})` }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/60 to-background"></div>
      
      {/* Content */}
      <div className="relative z-10">
        <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2 gradient-text">Choose Your Mentor</h1>
            <p className="text-gray-300">Select a mentor template to begin your personalized coaching journey</p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => setCurrentView('home')}
            className="border-lime-500 text-lime-500 hover:bg-lime-500 hover:text-black"
          >
            Back to Home
          </Button>
        </div>

        {groupMentorsByCategory(mentorTemplates).map((category) => {
          const IconComponent = category.icon
          return (
            <div key={category.name} className="mb-12">
              <div className="flex items-center mb-6">
                <div className={`w-12 h-12 bg-gradient-to-br ${category.color} rounded-lg flex items-center justify-center mr-4`}>
                  <IconComponent className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white">{category.name}</h2>
                  <p className="text-gray-300">{category.mentors.length} expert mentors available</p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {category.mentors.map((mentor) => (
                  <Card 
                    key={mentor.id} 
                    className="mentor-card bg-card/50 backdrop-blur-sm cursor-pointer"
                    onClick={() => startChatWithMentor(mentor)}
                  >
                    <CardHeader>
                      <div className="flex items-center justify-between mb-2">
                        <Avatar className="h-12 w-12">
                          <AvatarFallback className={`bg-gradient-to-br ${category.color} text-white font-bold`}>
                            {mentor.name.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <Badge variant="secondary" className="bg-lime-500/20 text-lime-500">
                          {category.name}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg">{mentor.name}</CardTitle>
                      <CardDescription className="text-gray-300 text-sm">
                        {mentor.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="text-xs text-gray-400">Personality:</div>
                        <div className="text-sm text-lime-400">{mentor.personality}</div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )
        })}
        </div>
      </div>
    </div>
  )

  const renderChat = () => (
    <div className="cosmic-bg min-h-screen relative">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-10"
        style={{ backgroundImage: `url(${astronautRocket})` }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/70 to-background"></div>
      
      {/* Content */}
      <div className="relative z-10">
        <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <Button 
              variant="outline" 
              onClick={() => setCurrentView('mentors')}
              className="mr-4 border-lime-500 text-lime-500 hover:bg-lime-500 hover:text-black"
            >
              ← Back
            </Button>
            <div className="flex items-center">
              <Avatar className="h-12 w-12 mr-3">
                <AvatarFallback className="bg-gradient-to-br from-lime-500 to-green-600 text-white font-bold">
                  {selectedMentor?.name.split(' ').map(n => n[0]).join('') || 'AI'}
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-2xl font-bold text-white">{selectedMentor?.name || 'AI Mentor'}</h1>
                <p className="text-gray-300 text-sm">{selectedMentor?.category || 'General'} • Online</p>
              </div>
            </div>
          </div>
        </div>

        <Card className="bg-card/50 backdrop-blur-sm h-[600px] flex flex-col">
          <CardContent className="flex-1 p-6 overflow-y-auto">
            <div className="space-y-4">
              {chatMessages.map((message, index) => (
                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`rounded-lg p-4 max-w-[80%] message-appear ${
                    message.role === 'user' 
                      ? 'bg-lime-500 text-black' 
                      : 'bg-secondary/50 text-white'
                  }`}>
                    <p>{message.content}</p>
                  </div>
                </div>
              ))}
              
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-secondary/50 rounded-lg p-4 max-w-[80%]">
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin text-lime-500" />
                      <span className="text-gray-300">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
          
          <div className="p-4 border-t border-border">
            <ChatInput onSendMessage={sendChatMessage} disabled={chatLoading} />
          </div>
        </Card>
        </div>
      </div>
    </div>
  )

  const renderProfile = () => (
    <div className="cosmic-bg min-h-screen relative">
      {/* Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-15"
        style={{ backgroundImage: `url(${astronautsSpace})` }}
      ></div>
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/60 to-background"></div>
      
      {/* Content */}
      <div className="relative z-10">
        <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold gradient-text">My Profile</h1>
          <Button 
            variant="outline" 
            onClick={() => setCurrentView('home')}
            className="border-lime-500 text-lime-500 hover:bg-lime-500 hover:text-black"
          >
            Back to Home
          </Button>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Profile Info */}
          <div className="lg:col-span-1">
            <Card className="bg-card/50 backdrop-blur-sm">
              <CardHeader className="text-center">
                <Avatar className="h-24 w-24 mx-auto mb-4">
                  <AvatarFallback className="bg-gradient-to-br from-lime-500 to-green-600 text-white text-2xl font-bold">
                    {currentUser?.full_name?.split(' ').map(n => n[0]).join('') || currentUser?.username?.slice(0, 2).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <CardTitle className="text-xl text-white">{currentUser?.full_name || currentUser?.username}</CardTitle>
                <CardDescription className="text-gray-300">{currentUser?.email}</CardDescription>
                <Badge className="bg-lime-500/20 text-lime-500 mt-2">
                  Member since {new Date(currentUser?.join_date || '2024-01-01').toLocaleDateString()}
                </Badge>
              </CardHeader>
            </Card>

            <Card className="bg-card/50 backdrop-blur-sm mt-6">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Settings className="mr-2 h-5 w-5" />
                  Quick Stats
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-300">Total Sessions</span>
                  <span className="text-lime-500 font-bold">{userStats.total_sessions || currentUser?.total_sessions || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Current Streak</span>
                  <span className="text-lime-500 font-bold">{userStats.current_streak || currentUser?.current_streak || 0} days</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Goals Completed</span>
                  <span className="text-lime-500 font-bold">{userStats.completed_goals || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Active Goals</span>
                  <span className="text-lime-500 font-bold">{userStats.active_goals || 0}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Progress & Goals */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <BarChart3 className="mr-2 h-5 w-5" />
                  Learning Progress
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {userProgress.map((progress, index) => (
                  <div key={index}>
                    <div className="flex justify-between mb-2">
                      <span className="text-gray-300">{progress.subject}</span>
                      <span className="text-lime-500">{progress.progress}%</span>
                    </div>
                    <Progress value={progress.progress} className="progress-glow" />
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Target className="mr-2 h-5 w-5" />
                  Current Goals
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {userGoals.map((goal) => (
                  <div key={goal.id} className="flex items-center justify-between p-4 bg-secondary/30 rounded-lg">
                    <div>
                      <h4 className="text-white font-medium">{goal.title}</h4>
                      <p className="text-gray-300 text-sm">{goal.description}</p>
                    </div>
                    <Badge className={`${
                      goal.status === 'in_progress' ? 'bg-lime-500/20 text-lime-500' :
                      goal.status === 'completed' ? 'bg-green-500/20 text-green-500' :
                      'bg-blue-500/20 text-blue-500'
                    }`}>
                      {goal.status === 'in_progress' ? 'In Progress' :
                       goal.status === 'completed' ? 'Completed' : 'Planning'}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Clock className="mr-2 h-5 w-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center space-x-3 p-3 bg-secondary/20 rounded-lg">
                  <div className="w-2 h-2 bg-lime-500 rounded-full"></div>
                  <span className="text-gray-300">Started conversation with {selectedMentor?.name || 'AI Mentor'}</span>
                  <span className="text-gray-500 text-sm ml-auto">Just now</span>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-secondary/20 rounded-lg">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-gray-300">Updated learning progress</span>
                  <span className="text-gray-500 text-sm ml-auto">1 hour ago</span>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-secondary/20 rounded-lg">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-gray-300">Achieved {currentUser?.current_streak || 7}-day learning streak</span>
                  <span className="text-gray-500 text-sm ml-auto">2 days ago</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div 
              className="flex items-center cursor-pointer" 
              onClick={() => setCurrentView('home')}
            >
              <img 
                src={logoTransparent} 
                alt="Make Mentors" 
                className="h-10 w-auto mr-3"
              />
              <span className="text-2xl font-bold gradient-text">Make Mentors</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button 
                variant={currentView === 'home' ? 'default' : 'ghost'} 
                onClick={() => setCurrentView('home')}
                className={currentView === 'home' ? 'bg-lime-500 text-black' : 'text-gray-300 hover:text-white'}
              >
                Home
              </Button>
              <Button 
                variant={currentView === 'mentors' ? 'default' : 'ghost'} 
                onClick={() => setCurrentView('mentors')}
                className={currentView === 'mentors' ? 'bg-lime-500 text-black' : 'text-gray-300 hover:text-white'}
              >
                Mentors
              </Button>
              <Button 
                variant={currentView === 'profile' ? 'default' : 'ghost'} 
                onClick={() => setCurrentView('profile')}
                className={currentView === 'profile' ? 'bg-lime-500 text-black' : 'text-gray-300 hover:text-white'}
              >
                Profile
              </Button>
              
              <Avatar className="h-8 w-8 cursor-pointer" onClick={() => setCurrentView('profile')}>
                <AvatarFallback className="bg-lime-500 text-black font-bold text-sm">
                  {currentUser?.full_name?.split(' ').map(n => n[0]).join('') || currentUser?.username?.slice(0, 2).toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      {currentView === 'home' && renderHome()}
      {currentView === 'mentors' && renderMentors()}
      {currentView === 'chat' && renderChat()}
      {currentView === 'profile' && renderProfile()}
    </div>
  )
}

// Chat Input Component
function ChatInput({ onSendMessage, disabled }) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message)
      setMessage('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input 
        type="text" 
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
        disabled={disabled}
        className="flex-1 bg-input border border-border rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-lime-500 disabled:opacity-50"
      />
      <Button 
        type="submit" 
        disabled={disabled || !message.trim()}
        className="bg-lime-500 hover:bg-lime-600 text-black disabled:opacity-50"
      >
        {disabled ? <Loader2 className="h-4 w-4 animate-spin" /> : <MessageCircle className="h-4 w-4" />}
      </Button>
    </form>
  )
}

export default App

