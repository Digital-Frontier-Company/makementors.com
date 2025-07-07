
import { useState, useCallback } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useMentor } from '@/contexts/MentorContext';
import { useAuth } from '@/contexts/AuthContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { selectedMentor, chatSessionId, setChatSessionId } = useMentor();
  const { user } = useAuth();

  const send = useCallback(async (content: string) => {
    if (!selectedMentor || !user) {
      throw new Error('Mentor and user must be selected');
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Prepare the messages array for the API call
      const conversationMessages = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      // Add the new user message
      conversationMessages.push({
        role: 'user',
        content
      });

      console.log("Sending chat request with mentor ID:", selectedMentor.id);
      console.log("Selected mentor details:", { id: selectedMentor.id, name: selectedMentor.name, category: selectedMentor.category });

      // Call the chat-with-mentor edge function with streaming
      const response = await fetch(`https://bapditcjlxctrisoixpg.supabase.co/functions/v1/chat-with-mentor`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${(await supabase.auth.getSession()).data.session?.access_token}`
        },
        body: JSON.stringify({
          mentorId: selectedMentor.id,
          messages: conversationMessages,
          chatSessionId: chatSessionId,
          userId: user.id,
          stream: true
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response from chat-with-mentor:", response.status, errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      // Get session ID from response headers if available
      const sessionId = response.headers.get('X-Chat-Session-Id');
      if (sessionId && sessionId !== chatSessionId) {
        console.log("Setting new chat session ID:", sessionId);
        setChatSessionId(sessionId);
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) {
        throw new Error('No response body');
      }

      let assistantContent = '';
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      };

      // Add empty assistant message that we'll update
      setMessages(prev => [...prev, assistantMessage]);

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n').filter(line => line.trim().startsWith('data: '));
          
          for (const line of lines) {
            const data = line.replace(/^data: /, '').trim();
            
            if (data === '[DONE]') {
              continue;
            }
            
            try {
              const json = JSON.parse(data);
              const content = json.choices?.[0]?.delta?.content || '';
              
              if (content) {
                assistantContent += content;
                
                // Update the assistant message in real-time
                setMessages(prev => prev.map(msg => 
                  msg.id === assistantMessage.id 
                    ? { ...msg, content: assistantContent }
                    : msg
                ));
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e, 'Data:', data);
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [selectedMentor, user, messages, chatSessionId, setChatSessionId]);

  return { messages, send, isLoading };
};
