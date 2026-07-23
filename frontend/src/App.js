import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import AudioRecorder from './AudioRecorder';
import Sidebar from './Sidebar';
import MeetingDetail from './MeetingDetail';
import AgentChat from './AgentChat';

const RELEASE_NOTES = [
  { version: '2.1', date: '2026-07-23', items: [
    'Gmail, Google Calendar, and Slack MCP connectors (Connect Services in agent chat)',
    'Cortex Search on meeting notes and summaries',
    'Agent can now search across all meeting content',
  ]},
  { version: '2.0', date: '2026-07-23', items: [
    'Converted all tables to standard (no more hybrid tables)',
    'Data-preserving DDL — safe to re-run without data loss',
    'Migration script (migrate_to_v2.sql) for existing deployments',
    '31 pre-loaded meeting notes with summaries',
  ]},
  { version: '1.0', date: '2026-07-21', items: [
    'Real-time audio transcription with ai_transcribe()',
    'AI extraction of action items, decisions, and topics',
    'Quilliam agent chat with transcript search + semantic view',
    'Meeting sidebar with full detail editing',
  ]},
];

function App() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [websocketStatus, setWebsocketStatus] = useState('Disconnected');
  const [websocket, setWebsocket] = useState(null);
  const [selectedMeetingId, setSelectedMeetingId] = useState(null);
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);
  const [chatOpen, setChatOpen] = useState(false);
  const [showReleaseNotes, setShowReleaseNotes] = useState(
    !localStorage.getItem('quilliam_rn_dismissed')
  );

  useEffect(() => {
    checkBackendHealth();
    connectWebSocket();
    return () => { if (websocket) websocket.close(); };
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/health');
      const data = await response.json();
      setBackendStatus(data);
    } catch (error) {
      setBackendStatus({ error: 'Connection failed' });
    }
  };

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8080/ws');
    ws.onopen = () => { setWebsocketStatus('Connected'); setWebsocket(ws); };
    ws.onmessage = (event) => { console.log('WebSocket message:', JSON.parse(event.data)); };
    ws.onclose = () => { setWebsocketStatus('Disconnected'); setWebsocket(null); };
    ws.onerror = () => { setWebsocketStatus('Error'); };
  };

  const handleNewMeeting = () => {
    setSelectedMeetingId(null);
  };

  const handleMeetingEnded = useCallback(() => {
    setSidebarRefreshKey(k => k + 1);
  }, []);

  const getStatusDot = (ok) => ok ? 'ok' : 'error';

  return (
    <div className="App">
      <header className="app-hero">
        <div className="hero-content">
          <div className="hero-title">
            <h1><img src="/icon.jpg" alt="Quilliam" className="app-logo" />Quilliam <span>Powered by Snowflake</span></h1>
            <p>Real-time transcription &bull; AI extraction &bull; Structured meeting notes</p>
          </div>
          <div className="hero-right">
            <div className="status-strip">
              <div className="status-pill">
                <div className={`status-dot ${backendStatus ? (backendStatus.error ? 'error' : 'ok') : 'loading'}`}></div>
                Backend
              </div>
              <div className="status-pill">
                <div className={`status-dot ${backendStatus?.snowflake_connected ? 'ok' : 'error'}`}></div>
                Snowflake
              </div>
              <div className="status-pill">
                <div className={`status-dot ${backendStatus?.audio_available ? 'ok' : 'error'}`}></div>
                Audio
              </div>
              <div className="status-pill">
                <div className={`status-dot ${getStatusDot(websocketStatus === 'Connected')}`}></div>
                WebSocket
              </div>
            </div>
            <button className="chat-toggle-btn" onClick={() => setChatOpen(!chatOpen)}>
              {chatOpen ? 'Close Chat' : 'Ask Quilliam'}
            </button>
            {!showReleaseNotes && (
              <button className="release-notes-toggle" onClick={() => setShowReleaseNotes(true)} title="What's New">
                v{RELEASE_NOTES[0].version}
              </button>
            )}
          </div>
        </div>
      </header>

      {showReleaseNotes && (
        <div className="release-notes-banner">
          <div className="release-notes-content">
            <div className="release-notes-header">
              <h3>What's New</h3>
              <button className="release-notes-close" onClick={() => {
                setShowReleaseNotes(false);
                localStorage.setItem('quilliam_rn_dismissed', RELEASE_NOTES[0].version);
              }}>&times;</button>
            </div>
            {RELEASE_NOTES.map(release => (
              <div key={release.version} className="release-version">
                <span className="release-tag">v{release.version}</span>
                <span className="release-date">{release.date}</span>
                <ul>
                  {release.items.map((item, i) => <li key={i}>{item}</li>)}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="app-layout">
        <Sidebar
          selectedMeetingId={selectedMeetingId}
          onSelectMeeting={setSelectedMeetingId}
          onNewMeeting={handleNewMeeting}
          refreshKey={sidebarRefreshKey}
        />
        <main className="app-main">
          {selectedMeetingId ? (
            <MeetingDetail meetingId={selectedMeetingId} />
          ) : (
            <AudioRecorder websocket={websocket} onMeetingEnded={handleMeetingEnded} />
          )}
        </main>
      </div>

      <AgentChat
        isOpen={chatOpen}
        onClose={() => setChatOpen(false)}
        meetingId={selectedMeetingId}
      />
    </div>
  );
}

export default App;
