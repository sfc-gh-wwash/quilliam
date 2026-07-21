import React, { useState, useEffect } from 'react';
import './Sidebar.css';

const Sidebar = ({ selectedMeetingId, onSelectMeeting, onNewMeeting, refreshKey }) => {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadMeetings();
  }, [refreshKey]);

  const loadMeetings = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8080/api/meetings');
      if (response.ok) {
        const data = await response.json();
        setMeetings(data.meetings || []);
      }
    } catch (error) {
      console.error('Failed to load meetings:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Meetings</h2>
        <button className="new-meeting-btn" onClick={onNewMeeting}>
          + New
        </button>
      </div>

      {loading && meetings.length === 0 && (
        <div className="sidebar-loading">Loading...</div>
      )}

      <div className="meeting-list">
        {meetings.map((meeting) => (
          <div
            key={meeting.meeting_id}
            className={`meeting-item ${selectedMeetingId === meeting.meeting_id ? 'active' : ''} ${meeting.status === 'IN_PROGRESS' ? 'recording' : ''}`}
            onClick={() => onSelectMeeting(meeting.meeting_id)}
          >
            <div className="meeting-item-title">
              {meeting.title || meeting.meeting_id}
            </div>
            <div className="meeting-item-meta">
              <span className="meeting-date">{formatDate(meeting.started_at)}</span>
              <span className={`meeting-status-badge ${meeting.status?.toLowerCase()}`}>
                {meeting.status === 'IN_PROGRESS' ? 'Live' : 'Done'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {meetings.length === 0 && !loading && (
        <div className="sidebar-empty">No meetings yet</div>
      )}
    </aside>
  );
};

export default Sidebar;
