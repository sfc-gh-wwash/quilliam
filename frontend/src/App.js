import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import AudioRecorder from './AudioRecorder';
import Sidebar from './Sidebar';
import MeetingDetail from './MeetingDetail';

function App() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [websocketStatus, setWebsocketStatus] = useState('Disconnected');
  const [websocket, setWebsocket] = useState(null);
  const [selectedMeetingId, setSelectedMeetingId] = useState(null);
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);

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
          </div>
        </div>
      </header>

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
    </div>
  );
}

export default App;
