import React, { useState, useEffect, useCallback } from 'react';
import './AudioRecorder.css';

const AudioRecorder = ({ websocket, onMeetingEnded }) => {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);

  const [meetingId, setMeetingId] = useState('');
  const [transcriptChunks, setTranscriptChunks] = useState([]);
  const [actionItems, setActionItems] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [topics, setTopics] = useState([]);
  const [attendees, setAttendees] = useState([]);
  const [blockers, setBlockers] = useState([]);
  const [meetingTitle, setMeetingTitle] = useState('');

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

        if (msg.action_items?.length) {
          setActionItems(msg.action_items);
        }

        if (msg.decisions?.length) {
          setDecisions(msg.decisions);
        }

        if (msg.topics?.length) {
          setTopics(prev => {
            const existing = new Set(prev);
            return [...prev, ...msg.topics.filter(t => !existing.has(t))];
          });
        }

        if (msg.attendees?.length) {
          setAttendees(prev => {
            const existing = new Set(prev);
            return [...prev, ...msg.attendees.filter(a => !existing.has(a))];
          });
        }

        if (msg.blockers?.length) {
          setBlockers(msg.blockers);
        }

        if (msg.meeting_title) {
          setMeetingTitle(msg.meeting_title);
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
      setActionItems([]);
      setDecisions([]);
      setTopics([]);
      setAttendees([]);
      setBlockers([]);
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
                  {meetingTitle && <div className="info-item"><strong>Title:</strong> {meetingTitle}</div>}
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

      {/* Action Items */}
      {actionItems.length > 0 && (
        <div className="action-items-section">
          <h2>Action Items <span className="count-badge">{actionItems.length}</span></h2>
          <div className="action-items-table">
            <div className="action-table-header">
              <div className="col-owner">Owner</div>
              <div className="col-task">Task</div>
              <div className="col-due">Due Date</div>
            </div>
            {actionItems.map((item) => (
              <div key={item.id} className="action-table-row">
                <div className="col-owner">{item.owner || '—'}</div>
                <div className="col-task">{item.task}</div>
                <div className="col-due">{item.due_date || '—'}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decisions */}
      {decisions.length > 0 && (
        <div className="decisions-section">
          <h2>Decisions <span className="count-badge">{decisions.length}</span></h2>
          <ul className="decisions-list">
            {decisions.map((d) => (
              <li key={d.id} className="decision-item">{d.text}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Topics & Attendees */}
      {(topics.length > 0 || attendees.length > 0) && (
        <div className="tags-section">
          {attendees.length > 0 && (
            <div className="tags-group">
              <h3>Attendees</h3>
              <div className="tag-list">
                {attendees.map((a, i) => (
                  <span key={i} className="tag attendee-tag">{a}</span>
                ))}
              </div>
            </div>
          )}
          {topics.length > 0 && (
            <div className="tags-group">
              <h3>Topics</h3>
              <div className="tag-list">
                {topics.map((t, i) => (
                  <span key={i} className="tag topic-tag">{t}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Blockers */}
      {blockers.length > 0 && (
        <div className="blockers-section">
          <h2>Blockers / Risks <span className="count-badge alert-badge">{blockers.length}</span></h2>
          <ul className="blockers-list">
            {blockers.map((b, i) => (
              <li key={i} className="blocker-item">{b}</li>
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
