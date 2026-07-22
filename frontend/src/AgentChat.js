import React, { useState, useRef, useEffect } from 'react';
import './AgentChat.css';

const API = 'http://localhost:8080/api';

const AgentChat = ({ isOpen, onClose, meetingId, meetingTitle }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const response = await fetch(`${API}/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, meeting_id: meetingId || null })
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { role: 'assistant', text: data.response }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', text: 'Error: Failed to get response from agent.' }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${error.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="agent-chat-panel">
      <div className="agent-chat-header">
        <div className="agent-chat-title">
          <h3>Quilliam Agent</h3>
          <span className="agent-chat-context">
            {meetingId ? `Meeting: ${meetingTitle || meetingId}` : 'All Meetings'}
          </span>
        </div>
        <button className="agent-chat-close" onClick={onClose}>&times;</button>
      </div>

      <div className="agent-chat-messages">
        {messages.length === 0 && (
          <div className="agent-chat-empty">
            <p>Ask me about your meetings.</p>
            <p className="agent-chat-hint">
              {meetingId
                ? 'Questions will be scoped to this meeting.'
                : 'Questions will search across all meetings.'}
            </p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <div className="chat-bubble">
              {msg.text.split('\n').map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant">
            <div className="chat-bubble loading">
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="agent-chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder={meetingId ? 'Ask about this meeting...' : 'Ask about your meetings...'}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};

export default AgentChat;
