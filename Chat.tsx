
import React, { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Send, Loader2 } from 'lucide-react';
import { useChat } from '@/hooks/useChat';

const Chat = () => {
  const [input, setInput] = useState('');
  const { messages, send, isLoading } = useChat();

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const messageToSend = input;
    setInput('');
    await send(messageToSend);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">AI Chat</h1>
        
        {/* Messages Container */}
        <div className="flex flex-col space-y-4 mb-6 max-h-[60vh] overflow-y-auto">
          {messages.length === 0 ? (
            <div className="text-center text-zinc-400 py-8">
              Start a conversation by typing a message below
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <Card className={`max-w-[70%] ${
                  message.role === 'user'
                    ? 'bg-lime-500 text-black' 
                    : 'bg-zinc-800 border-zinc-700'
                }`}>
                  <CardContent className="p-3">
                    <p className="text-sm">{message.content}</p>
                    <span className={`text-xs ${
                      message.role === 'user' ? 'text-black/70' : 'text-zinc-400'
                    } mt-1 block`}>
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                  </CardContent>
                </Card>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <Card className="bg-zinc-800 border-zinc-700">
                <CardContent className="p-3">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm text-zinc-400">AI is thinking...</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="flex space-x-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            className="flex-1 bg-zinc-900 border-zinc-700 text-white placeholder:text-zinc-400 resize-none"
            rows={3}
            disabled={isLoading}
          />
          <Button 
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="self-end"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
