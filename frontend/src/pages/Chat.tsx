import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, UserIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline';
import CopilotChat from '../components/CopilotChat';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your SupplyMind AI assistant. I can help you with supply chain optimization, inventory management, demand forecasting, and more. How can I assist you today?',
      role: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    // Simulate AI response (in a real app, this would call your AI service)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: generateAIResponse(inputMessage),
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('inventory') || input.includes('stock')) {
      return 'I can help you with inventory management! Currently, your system shows 1,248 active SKUs with 85% stock availability. Would you like me to analyze specific products, check low-stock alerts, or optimize reorder points?';
    }
    
    if (input.includes('demand') || input.includes('forecast')) {
      return 'Based on historical data and seasonal trends, I can provide demand forecasting insights. Your electronics category shows a 15% increase expected next quarter. Would you like detailed forecasts for specific product categories?';
    }
    
    if (input.includes('supplier') || input.includes('vendor')) {
      return 'I can analyze your supplier performance. Currently tracking 45 active suppliers with an average delivery time of 5.2 days. Top performing supplier: TechCorp with 98.5% on-time delivery. Need supplier recommendations or performance analysis?';
    }
    
    if (input.includes('analytics') || input.includes('report')) {
      return 'I can generate comprehensive analytics reports. Recent highlights: Revenue up 12.5%, Order volume increased 8.3%, Average order value $365. What specific metrics would you like me to analyze?';
    }
    
    if (input.includes('optimization') || input.includes('improve')) {
      return 'I can suggest supply chain optimizations! Key recommendations: 1) Consolidate orders from TechCorp to reduce shipping costs, 2) Increase safety stock for iPhone 15 Pro (high demand, low stock), 3) Consider alternative suppliers for faster delivery. Which area would you like to focus on?';
    }
    
    return `I understand you're asking about "${userInput}". I can help with supply chain management, inventory optimization, demand forecasting, supplier analysis, and reporting. Could you provide more specific details about what you'd like assistance with?`;
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            SupplyMind AI Assistant
          </h1>
          <p className="text-gray-600">
            Get intelligent insights and recommendations for your supply chain
          </p>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-lg shadow-lg h-[600px] flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <ComputerDesktopIcon className="w-5 h-5 text-white" />
                    </div>
                  </div>
                )}
                
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                    }`}
                  >
                    {formatTimestamp(message.timestamp)}
                  </p>
                </div>
                
                {message.role === 'user' && (
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center">
                      <UserIcon className="w-5 h-5 text-white" />
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <ComputerDesktopIcon className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div className="bg-gray-100 px-4 py-2 rounded-lg">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <form onSubmit={handleSendMessage} className="flex space-x-3">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about inventory, demand forecasting, suppliers, or optimization..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <PaperAirplaneIcon className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>

        {/* Copilot Chat Integration */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Advanced AI Chat
          </h2>
          <div className="bg-white rounded-lg shadow p-6">
            <CopilotChat />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={() => setInputMessage('Show me inventory analytics')}
            className="p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            <h3 className="font-medium text-blue-900">Inventory Analytics</h3>
            <p className="text-sm text-blue-700 mt-1">View stock levels and turnover</p>
          </button>
          
          <button
            onClick={() => setInputMessage('Generate demand forecast')}
            className="p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
          >
            <h3 className="font-medium text-green-900">Demand Forecast</h3>
            <p className="text-sm text-green-700 mt-1">Predict future demand trends</p>
          </button>
          
          <button
            onClick={() => setInputMessage('Analyze supplier performance')}
            className="p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <h3 className="font-medium text-purple-900">Supplier Analysis</h3>
            <p className="text-sm text-purple-700 mt-1">Review vendor metrics</p>
          </button>
          
          <button
            onClick={() => setInputMessage('Suggest optimization opportunities')}
            className="p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
          >
            <h3 className="font-medium text-orange-900">Optimization</h3>
            <p className="text-sm text-orange-700 mt-1">Find improvement areas</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
