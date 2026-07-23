import React, { useState, useEffect, useCallback } from 'react';
import './AudioRecorder.css';

const AudioRecorder = ({ websocket, onMeetingEnded }) => {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);

  const [meetingId, setMeetingId] = useState('');
  const [meetingTitle, setMeetingTitle] = useState('');
  const [editingTitle, setEditingTitle] = useState(false);
  const [transcriptChunks, setTranscriptChunks] = useState([]);
  const [questions, setQuestions] = useState([]);

  const [recorderCollapsed, setRecorderCollapsed] = useState(false);

  const loadAudioDevices = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8080/api/audio/devices');
      const deviceData = await response.json();
      setDevices(deviceData);
      if (deviceData.length > 0 && !selectedDevice) {
        setSelectedDevice(deviceData[0].index.toString());
      }
    } catch (error) {
      console.error('Failed to load audio devices:', error);
    }
  }, [selectedDevice]);

  const checkRecordingStatus = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/meetings/status');
      const status = await response.json();
      setIsRecording(status.is_recording);
      if (status.current_meeting_id) setMeetingId(status.current_meeting_id);
    } catch (error) {
      console.error('Failed to check recording status:', error);
    }
  };

  useEffect(() => {
    loadAudioDevices();
    checkRecordingStatus();
  }, [loadAudioDevices]);

  // Merge incoming WebSocket data into running state arrays (union by text)
  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type !== 'meeting_updated') return;
        if (msg.meeting_id !== meetingId) return;

        if (msg.transcript_chunks?.length) {
          setTranscriptChunks(msg.transcript_chunks);
        }

        if (msg.questions?.length) {
          setQuestions(prev => {
            const existing = new Set(prev);
            return [...prev, ...msg.questions.filter(q => !existing.has(q))];
          });
        }

      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    websocket.onmessage = handleMessage;
    return () => { if (websocket) websocket.onmessage = null; };
  }, [websocket, meetingId]);

  const startRecording = async () => {
    if (!selectedDevice) { alert('Please select an audio device'); return; }
    setLoading(true);
    try {
      // Reset all state for new meeting
      setTranscriptChunks([]);
      setQuestions([]);
      setMeetingTitle('');

      const response = await fetch('http://localhost:8080/api/meetings/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_index: parseInt(selectedDevice) })
      });
      const data = await response.json();
      if (response.ok) {
        setMeetingId(data.meeting_id);
        setIsRecording(true);
        setRecorderCollapsed(true);

        // Poll for auto-detected title from calendar (agent runs async on backend)
        const pollTitle = (id, attempts = 0) => {
          if (attempts >= 10) return;
          setTimeout(async () => {
            try {
              const res = await fetch('http://localhost:8080/api/meetings');
              if (res.ok) {
                const d = await res.json();
                const m = (d.meetings || []).find(x => x.meeting_id === id);
                if (m && m.title) {
                  setMeetingTitle(m.title);
                } else {
                  pollTitle(id, attempts + 1);
                }
              }
            } catch (e) { /* ignore */ }
          }, 3000);
        };
        pollTitle(data.meeting_id);
      } else {
        throw new Error(data.detail || 'Failed to start recording');
      }
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Failed to start recording: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const stopRecording = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/meetings/stop', { method: 'POST' });
      if (response.ok) {
        setIsRecording(false);
        if (onMeetingEnded) onMeetingEnded();
      } else {
        throw new Error('Failed to stop recording');
      }
    } catch (error) {
      console.error('Failed to stop recording:', error);
      alert('Failed to stop recording');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="audio-recorder">

      {/* Meeting Recorder Controls */}
      <div className="recorder-section">
        <div className="section-header" onClick={() => setRecorderCollapsed(!recorderCollapsed)}>
          <h2>Meeting Recorder</h2>
          <span className={`collapse-chevron ${recorderCollapsed ? 'collapsed' : ''}`}>&#8964;</span>
        </div>

        {!recorderCollapsed && (
          <>
            <div className="device-phone-row">
              <div className="control-group">
                <label htmlFor="device-select">Microphone Device:</label>
                <div className="input-row">
                  <select
                    id="device-select"
                    value={selectedDevice}
                    onChange={(e) => setSelectedDevice(e.target.value)}
                    disabled={isRecording}
                    className="device-select"
                  >
                    <option value="">Select a device...</option>
                    {devices.map((device) => (
                      <option key={device.index} value={device.index}>
                        {device.name} ({device.max_input_channels} ch)
                      </option>
                    ))}
                  </select>
                  <button onClick={loadAudioDevices} className="refresh-btn" disabled={loading}>
                    Refresh
                  </button>
                </div>
              </div>
            </div>

            <div className="recording-controls">
              <div className="status-indicator">
                <div className={`status-light ${isRecording ? 'recording' : 'stopped'}`}></div>
                <span className="status-text">
                  {isRecording ? 'Recording...' : 'Stopped'}
                </span>
              </div>
              <div className="control-buttons">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={loading || !selectedDevice}
                  className={`record-btn ${isRecording ? 'stop' : 'start'}`}
                >
                  {loading ? 'Processing...' : (isRecording ? 'End Meeting' : 'Start Meeting')}
                </button>
              </div>
            </div>

            {meetingId && (
              <div className="session-info">
                <div className="info-grid">
                  <div className="info-item"><strong>Meeting ID:</strong> {meetingId}</div>
                  <div className="info-item">
                    <strong>Title:</strong>
                    {editingTitle ? (
                      <input
                        className="inline-title-input"
                        value={meetingTitle}
                        onChange={(e) => setMeetingTitle(e.target.value)}
                        onBlur={() => {
                          setEditingTitle(false);
                          if (meetingTitle.trim()) {
                            fetch(`http://localhost:8080/api/meetings/${meetingId}`, {
                              method: 'PUT',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ title: meetingTitle })
                            });
                          }
                        }}
                        onKeyDown={(e) => e.key === 'Enter' && e.target.blur()}
                        autoFocus
                        placeholder="Enter meeting title..."
                      />
                    ) : (
                      <span className="editable-title" onClick={() => setEditingTitle(true)}>
                        {meetingTitle || 'Click to add title'}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {recorderCollapsed && meetingId && (
          <div className="collapsed-status">
            <div className={`status-light ${isRecording ? 'recording' : 'stopped'}`}></div>
            <span>{isRecording ? 'Recording' : 'Stopped'} — {meetingId}</span>
            {isRecording && (
              <button onClick={stopRecording} disabled={loading} className="record-btn stop inline-stop">
                {loading ? 'Stopping...' : 'End Meeting'}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Live Transcript */}
      {transcriptChunks.length > 0 && (
        <div className="transcript-section">
          <h2>Live Transcript</h2>
          <div className="transcript-feed">
            {[...transcriptChunks].reverse().map((chunk, idx) => (
              <div key={transcriptChunks.length - idx} className="transcript-chunk">
                <span className="chunk-num">{transcriptChunks.length - idx}</span>
                <span className="chunk-text">{chunk}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Questions Detected */}
      {questions.length > 0 && (
        <div className="questions-section">
          <h2>Questions Asked <span className="count-badge">{questions.length}</span></h2>
          <ul className="questions-list">
            {[...questions].reverse().map((q, i) => (
              <li key={i} className="question-item">{q}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Empty state */}
      {!isRecording && !meetingId && (
        <div className="empty-state">
          <p>Select a microphone and click <strong>Start Meeting</strong> to begin recording.</p>
          <p className="empty-hint">
            Audio is transcribed live by <strong>ai_transcribe()</strong> and structured notes are
            extracted using <strong>ai_extract()</strong> — all inside Snowflake.
          </p>
        </div>
      )}

      {isRecording && transcriptChunks.length === 0 && (
        <div className="waiting-state">
          <div className="pulse-dot"></div>
          <p>Recording... notes will appear as each audio chunk is processed.</p>
        </div>
      )}

    </div>
  );
};

export default AudioRecorder;
