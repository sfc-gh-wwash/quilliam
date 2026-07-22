import React, { useState, useEffect, useCallback } from 'react';
import './MeetingDetail.css';

const API = 'http://localhost:8080/api';

const MeetingDetail = ({ meetingId }) => {
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [summary, setSummary] = useState('');
  const [transcriptChunks, setTranscriptChunks] = useState([]);
  const [actionItems, setActionItems] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [topics, setTopics] = useState([]);
  const [attendees, setAttendees] = useState([]);
  const [blockers, setBlockers] = useState([]);
  const [meetingMeta, setMeetingMeta] = useState({});

  const [editingTitle, setEditingTitle] = useState(false);
  const [newAction, setNewAction] = useState({ owner: '', task: '', due_date: '' });
  const [newDecision, setNewDecision] = useState('');
  const [editingItemId, setEditingItemId] = useState(null);
  const [editingDecisionId, setEditingDecisionId] = useState(null);

  const loadMeeting = useCallback(async () => {
    setLoading(true);
    try {
      const [extRes, transRes, meetingsRes] = await Promise.all([
        fetch(`${API}/meetings/${meetingId}/extractions`),
        fetch(`${API}/meetings/${meetingId}/transcript`),
        fetch(`${API}/meetings`),
      ]);

      if (extRes.ok) {
        const ext = await extRes.json();
        setActionItems(ext.action_items || []);
        setDecisions(ext.decisions || []);
        setTopics(ext.topics || []);
        setAttendees(ext.attendees || []);
        setBlockers(ext.blockers || []);
        if (ext.meeting_title && !title) setTitle(ext.meeting_title);
      }

      if (transRes.ok) {
        const trans = await transRes.json();
        setTranscriptChunks(trans.chunks || []);
      }

      if (meetingsRes.ok) {
        const data = await meetingsRes.json();
        const meeting = (data.meetings || []).find(m => m.meeting_id === meetingId);
        if (meeting) {
          setMeetingMeta(meeting);
          if (meeting.title) setTitle(meeting.title);
          if (meeting.notes) setNotes(meeting.notes);
          if (meeting.summary) setSummary(meeting.summary);
        }
      }
    } catch (error) {
      console.error('Failed to load meeting:', error);
    } finally {
      setLoading(false);
    }
  }, [meetingId]);

  useEffect(() => {
    setTitle('');
    setNotes('');
    setSummary('');
    loadMeeting();
  }, [meetingId, loadMeeting]);

  const saveTitle = async () => {
    setEditingTitle(false);
    await fetch(`${API}/meetings/${meetingId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
  };

  const saveNotes = async () => {
    await fetch(`${API}/meetings/${meetingId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes })
    });
  };

  const addActionItem = async () => {
    if (!newAction.task.trim()) return;
    const res = await fetch(`${API}/meetings/${meetingId}/action-items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newAction)
    });
    if (res.ok) {
      const data = await res.json();
      setActionItems([...actionItems, { id: data.id, ...newAction, status: 'OPEN' }]);
      setNewAction({ owner: '', task: '', due_date: '' });
    }
  };

  const deleteActionItem = async (id) => {
    const res = await fetch(`${API}/action-items/${id}`, { method: 'DELETE' });
    if (res.ok) setActionItems(actionItems.filter(a => a.id !== id));
  };

  const saveActionItem = async (item) => {
    await fetch(`${API}/action-items/${item.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item)
    });
    setEditingItemId(null);
  };

  const addDecision = async () => {
    if (!newDecision.trim()) return;
    const res = await fetch(`${API}/meetings/${meetingId}/decisions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: newDecision })
    });
    if (res.ok) {
      const data = await res.json();
      setDecisions([...decisions, { id: data.id, text: newDecision }]);
      setNewDecision('');
    }
  };

  const deleteDecision = async (id) => {
    const res = await fetch(`${API}/decisions/${id}`, { method: 'DELETE' });
    if (res.ok) setDecisions(decisions.filter(d => d.id !== id));
  };

  const saveDecision = async (id, text) => {
    await fetch(`${API}/decisions/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    setEditingDecisionId(null);
  };

  if (loading) return <div className="detail-loading">Loading meeting...</div>;

  return (
    <div className="meeting-detail">
      {/* Title */}
      <div className="detail-title-section">
        {editingTitle ? (
          <input
            className="title-input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={saveTitle}
            onKeyDown={(e) => e.key === 'Enter' && saveTitle()}
            autoFocus
          />
        ) : (
          <h1 className="detail-title" onClick={() => setEditingTitle(true)}>
            {title || meetingId}
            <span className="edit-hint">click to edit</span>
          </h1>
        )}
        <div className="detail-meta">
          <span>{meetingMeta.started_at}</span>
          <span className={`meeting-status-badge ${meetingMeta.status?.toLowerCase()}`}>
            {meetingMeta.status}
          </span>
        </div>
      </div>

      {/* Summary */}
      {summary && (
        <section className="detail-section summary-section">
          <h2>Meeting Summary</h2>
          <div className="summary-content">
            {summary.split('\n').map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </section>
      )}

      {/* Transcript */}
      {transcriptChunks.length > 0 && (
        <section className="detail-section">
          <h2>Transcript</h2>
          <div className="detail-transcript">
            {transcriptChunks.map((chunk, idx) => (
              <div key={idx} className="transcript-chunk">
                <span className="chunk-num">{chunk.chunk_number}</span>
                <span className="chunk-text">{chunk.text}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Action Items */}
      <section className="detail-section">
        <h2>Action Items <span className="count-badge">{actionItems.length}</span></h2>
        <div className="action-items-table">
          {actionItems.map((item) => (
            <div key={item.id} className="action-row">
              {editingItemId === item.id ? (
                <>
                  <input value={item.owner || ''} onChange={(e) => setActionItems(actionItems.map(a => a.id === item.id ? {...a, owner: e.target.value} : a))} placeholder="Owner" className="inline-input sm" />
                  <input value={item.task} onChange={(e) => setActionItems(actionItems.map(a => a.id === item.id ? {...a, task: e.target.value} : a))} placeholder="Task" className="inline-input lg" />
                  <input value={item.due_date || ''} onChange={(e) => setActionItems(actionItems.map(a => a.id === item.id ? {...a, due_date: e.target.value} : a))} placeholder="Due date" className="inline-input sm" />
                  <button className="icon-btn save" onClick={() => saveActionItem(item)}>Save</button>
                  <button className="icon-btn cancel" onClick={() => setEditingItemId(null)}>X</button>
                </>
              ) : (
                <>
                  <span className="action-owner">{item.owner || '—'}</span>
                  <span className="action-task">{item.task}</span>
                  <span className="action-due">{item.due_date || '—'}</span>
                  <button className="icon-btn edit" onClick={() => setEditingItemId(item.id)}>Edit</button>
                  <button className="icon-btn delete" onClick={() => deleteActionItem(item.id)}>Del</button>
                </>
              )}
            </div>
          ))}
        </div>
        <div className="add-row">
          <input value={newAction.owner} onChange={(e) => setNewAction({...newAction, owner: e.target.value})} placeholder="Owner" className="inline-input sm" />
          <input value={newAction.task} onChange={(e) => setNewAction({...newAction, task: e.target.value})} placeholder="New action item..." className="inline-input lg" />
          <input value={newAction.due_date} onChange={(e) => setNewAction({...newAction, due_date: e.target.value})} placeholder="Due date" className="inline-input sm" />
          <button className="icon-btn add" onClick={addActionItem}>Add</button>
        </div>
      </section>

      {/* Decisions */}
      <section className="detail-section">
        <h2>Decisions <span className="count-badge">{decisions.length}</span></h2>
        <div className="decisions-list">
          {decisions.map((d) => (
            <div key={d.id} className="decision-row">
              {editingDecisionId === d.id ? (
                <>
                  <input
                    value={d.text}
                    onChange={(e) => setDecisions(decisions.map(x => x.id === d.id ? {...x, text: e.target.value} : x))}
                    className="inline-input lg"
                    onKeyDown={(e) => e.key === 'Enter' && saveDecision(d.id, d.text)}
                  />
                  <button className="icon-btn save" onClick={() => saveDecision(d.id, d.text)}>Save</button>
                  <button className="icon-btn cancel" onClick={() => setEditingDecisionId(null)}>X</button>
                </>
              ) : (
                <>
                  <span className="decision-text">{d.text}</span>
                  <button className="icon-btn edit" onClick={() => setEditingDecisionId(d.id)}>Edit</button>
                  <button className="icon-btn delete" onClick={() => deleteDecision(d.id)}>Del</button>
                </>
              )}
            </div>
          ))}
        </div>
        <div className="add-row">
          <input value={newDecision} onChange={(e) => setNewDecision(e.target.value)} placeholder="New decision..." className="inline-input lg" onKeyDown={(e) => e.key === 'Enter' && addDecision()} />
          <button className="icon-btn add" onClick={addDecision}>Add</button>
        </div>
      </section>

      {/* Topics & Attendees */}
      {(topics.length > 0 || attendees.length > 0) && (
        <section className="detail-section tags-row">
          {attendees.length > 0 && (
            <div className="tags-group">
              <h3>Attendees</h3>
              <div className="tag-list">
                {attendees.map((a, i) => <span key={i} className="tag attendee-tag">{a}</span>)}
              </div>
            </div>
          )}
          {topics.length > 0 && (
            <div className="tags-group">
              <h3>Topics</h3>
              <div className="tag-list">
                {topics.map((t, i) => <span key={i} className="tag topic-tag">{t}</span>)}
              </div>
            </div>
          )}
        </section>
      )}

      {/* Blockers */}
      {blockers.length > 0 && (
        <section className="detail-section blockers">
          <h2>Blockers</h2>
          <ul className="blockers-list">
            {blockers.map((b, i) => <li key={i} className="blocker-item">{b}</li>)}
          </ul>
        </section>
      )}

      {/* Notes */}
      <section className="detail-section">
        <h2>Notes</h2>
        <textarea
          className="notes-textarea"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          onBlur={saveNotes}
          placeholder="Add meeting notes..."
          rows={5}
        />
      </section>
    </div>
  );
};

export default MeetingDetail;
