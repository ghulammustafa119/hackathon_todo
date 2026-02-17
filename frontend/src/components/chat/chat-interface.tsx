'use client';

import { useState, useRef, useEffect } from 'react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  isError?: boolean;
}

interface ChatInterfaceProps {
  userId: string | null;
  token: string | null;
  onTaskUpdate: () => void;
}

export default function ChatInterface({ userId, token, onTaskUpdate }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message to chat
    const userMessage: Message = { id: Date.now(), text: inputValue, sender: 'user', timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Add debug log
      console.log('Chat request sending with auth header:', token ? 'present' : 'absent');

      // Send request to backend AI chatbot endpoint using /api/{user_id}/chat pattern
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000/api';
      const response = await fetch(`${backendUrl}/${userId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`, // Pass the JWT token
        },
        body: JSON.stringify({
          message: inputValue,
          user_id: userId
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Not authenticated. Please log in again.');
        } else if (response.status === 404) {
          throw new Error('Chat endpoint not found');
        } else if (response.status === 500) {
          // Try to get the error message from the response
          try {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Server error: ${response.status}`);
          } catch (e) {
            // If we can't parse the error response, use a generic message
            throw new Error(`Server error: ${response.status}`);
          }
        } else {
          throw new Error(`Chat request failed: ${response.status}`);
        }
      }

      const data = await response.json();

      // Format the bot response to show clean UI text
      let displayText = data.response || 'I received your message.';

      // The backend should return properly formatted responses, not raw JSON
      // If we receive raw JSON, it indicates a backend issue
      try {
        // Check if the response is raw JSON (which shouldn't happen in proper implementation)
        if (typeof displayText === 'string' &&
            displayText.trim().startsWith('{') &&
            displayText.trim().endsWith('}') &&
            displayText.includes('"tool"')) {

          console.warn('Received raw JSON from backend - this indicates a backend issue:', displayText);
          // Try to parse and format it nicely, but this shouldn't happen normally
          const jsonResponse = JSON.parse(displayText);
          if (jsonResponse.tool && jsonResponse.arguments) {
            if (jsonResponse.tool === 'create_task' && jsonResponse.arguments.title) {
              displayText = `Created task: "${jsonResponse.arguments.title}"`;
            } else if (jsonResponse.tool === 'list_tasks') {
              displayText = 'Retrieved your tasks.';
            } else if (jsonResponse.tool === 'update_task') {
              displayText = 'Updated the task successfully.';
            } else if (jsonResponse.tool === 'delete_task') {
              displayText = 'Deleted the task successfully.';
            } else if (jsonResponse.tool === 'complete_task') {
              displayText = 'Updated task completion status.';
            } else {
              // For other tool calls, try to create a meaningful message
              displayText = `Executed: ${jsonResponse.tool}`;
            }
          } else {
            // If it's JSON but not a tool call, show a generic message
            displayText = 'Processed your request.';
          }
        }
      } catch (e) {
        // If parsing fails, it means it's not JSON, so keep the original response
        // This is expected behavior for properly formatted responses
      }

      // Add bot response to chat
      const botMessage: Message = {
        id: Date.now() + 1,
        text: displayText,
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);

      // Check if the response indicates a task operation and trigger refresh
      const responseText = displayText;
      if (responseText.toLowerCase().includes('task') ||
          responseText.toLowerCase().includes('created') ||
          responseText.toLowerCase().includes('updated') ||
          responseText.toLowerCase().includes('deleted') ||
          responseText.toLowerCase().includes('completed')) {
        // Notify parent component that a task operation occurred
        if (onTaskUpdate && typeof onTaskUpdate === 'function') {
          onTaskUpdate();
        }
      }
    } catch (error: any) {
      console.error('Error sending message:', error);

      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: `Sorry, I encountered an error: ${error.message}`,
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col bg-white rounded-xl shadow-sm p-5 border border-gray-200 min-h-[320px] max-h-[400px]">
      <div className="overflow-y-auto max-h-60 mb-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-indigo-500 text-white'
                    : message.isError
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-200 text-gray-800'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.text}</div>
                <div className={`text-xs mt-1 ${message.sender === 'user' ? 'text-indigo-200' : 'text-gray-500'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg max-w-xs">
                <div className="flex space-x-1">
                  <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                  <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex space-x-3">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your task request..."
          className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || isLoading}
          className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 disabled:opacity-50 transition-all duration-200"
        >
          Send
        </button>
      </form>
    </div>
  );
}