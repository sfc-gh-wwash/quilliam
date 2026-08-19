import React, { useState, useEffect } from 'react';
import './Sidebar.css';

const Sidebar = ({ selectedMeetingId, onSelectMeeting, onNewMeeting, refreshKey }) => {
  const [meetings, setMeetings] = useState([]);
  const [deletedMeetings, setDeletedMeetings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDeleted, setShowDeleted] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [exportStart, setExportStart] = useState('');
  const [exportEnd, setExportEnd] = useState('');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadMeetings();
  }, [refreshKey]);

  const loadMeetings = async () => {
    setLoading(true);
    try {
      const [res, delRes] = await Promise.all([
        fetch('http://localhost:8080/api/meetings'),
        fetch('http://localhost:8080/api/meetings/deleted'),
      ]);
      if (res.ok) {
        const data = await res.json();
        setMeetings(data.meetings || []);
      }
      if (delRes.ok) {
        const data = await delRes.json();
        setDeletedMeetings(data.meetings || []);
      }
    } catch (error) {
      console.error('Failed to load meetings:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteMeeting = async (e, meetingId) => {
    e.stopPropagation();
    if (!window.confirm('Move this meeting to Deleted?')) return;
    try {
      const res = await fetch(`http://localhost:8080/api/meetings/${meetingId}`, { method: 'DELETE' });
      if (res.ok) {
        if (selectedMeetingId === meetingId) onSelectMeeting(null);
        loadMeetings();
      }
    } catch (err) {
      console.error('Failed to delete meeting:', err);
    }
  };

  const restoreMeeting = async (e, meetingId) => {
    e.stopPropagation();
    try {
      const res = await fetch(`http://localhost:8080/api/meetings/${meetingId}/restore`, { method: 'POST' });
      if (res.ok) loadMeetings();
    } catch (err) {
      console.error('Failed to restore meeting:', err);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const handleExport = async () => {
    if (!exportStart || !exportEnd) return;
    setExporting(true);
    try {
      const res = await fetch(`http://localhost:8080/api/meetings/export?start_date=${exportStart}&end_date=${exportEnd}`);
      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || 'Export failed');
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `meetings_${exportStart}_to_${exportEnd}.md`;
      a.click();
      URL.revokeObjectURL(url);
      setShowExport(false);
    } catch (err) {
      console.error('Export failed:', err);
      alert('Export failed');
    } finally {
      setExporting(false);
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Meetings</h2>
        <div className="sidebar-header-actions">
          <button className="export-btn" onClick={() => setShowExport(!showExport)} title="Export meetings">
            Export
          </button>
          <button className="new-meeting-btn" onClick={onNewMeeting}>
            + New
          </button>
        </div>
      </div>

      {showExport && (
        <div className="export-panel">
          <div className="export-field">
            <label>From</label>
            <input type="date" value={exportStart} onChange={(e) => setExportStart(e.target.value)} />
          </div>
          <div className="export-field">
            <label>To</label>
            <input type="date" value={exportEnd} onChange={(e) => setExportEnd(e.target.value)} />
          </div>
          <button className="export-download-btn" onClick={handleExport} disabled={exporting || !exportStart || !exportEnd}>
            {exporting ? 'Exporting...' : 'Download .md'}
          </button>
        </div>
      )}

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
              <button className="meeting-delete-btn" onClick={(e) => deleteMeeting(e, meeting.meeting_id)} title="Delete">
                &times;
              </button>
            </div>
          </div>
        ))}
      </div>

      {meetings.length === 0 && !loading && (
        <div className="sidebar-empty">No meetings yet</div>
      )}

      {/* Deleted meetings folder */}
      {deletedMeetings.length > 0 && (
        <div className="deleted-folder">
          <button className="deleted-folder-toggle" onClick={() => setShowDeleted(!showDeleted)}>
            <span className="deleted-folder-icon">{showDeleted ? '▼' : '▶'}</span>
            Deleted ({deletedMeetings.length})
          </button>
          {showDeleted && (
            <div className="deleted-list">
              {deletedMeetings.map((meeting) => (
                <div key={meeting.meeting_id} className="meeting-item deleted">
                  <div className="meeting-item-title">
                    {meeting.title || meeting.meeting_id}
                  </div>
                  <div className="meeting-item-meta">
                    <span className="meeting-date">{formatDate(meeting.started_at)}</span>
                    <button className="meeting-restore-btn" onClick={(e) => restoreMeeting(e, meeting.meeting_id)} title="Restore">
                      ↩
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </aside>
  );
};

export default Sidebar;
