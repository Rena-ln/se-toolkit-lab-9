import { useState, useEffect } from 'react'
import './App.css'
import Dashboard from './Dashboard'

interface Course {
  id: number
  name: string
  code: string
  description: string | null
  instructor: string | null
  semester: string
  credits: number
  color: string | null
  created_at: string
  updated_at: string
}

interface Assignment {
  id: number
  course_id: number
  title: string
  description: string | null
  assignment_type: string
  weight: number
  estimated_hours: number | null
  priority: string
  status: string
  attributes: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

interface Deadline {
  id: number
  assignment_id: number
  due_date: string
  is_final: boolean
  notes: string | null
  created_at: string
}

interface PrioritizedTask {
  assignment: Assignment
  deadline: Deadline
  priority_score: number
  recommendation: string
  risk_level: string
  conflict_warnings: string[]
}

interface CourseProgress {
  course_id: number
  course_name: string
  course_code: string
  total_assignments: number
  completed: number
  in_progress: number
  not_started: number
  overdue: number
  completion_percentage: number
}

type View = 'tasks' | 'dashboard' | 'manage'

function App() {
  const [apiKey, setApiKey] = useState<string>(() => {
    return localStorage.getItem('do_api_key') || ''
  })
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!apiKey)
  const [view, setView] = useState<View>('tasks')
  const [tasks, setTasks] = useState<PrioritizedTask[]>([])
  const [progress, setProgress] = useState<CourseProgress[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [deadlines, setDeadlines] = useState<Deadline[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1'

  useEffect(() => {
    if (apiKey) {
      localStorage.setItem('do_api_key', apiKey)
      fetchData()
    }
  }, [apiKey])

  const headers = () => ({
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  })

  const handleApiKeySubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (apiKey.trim()) {
      setIsAuthenticated(true)
    }
  }

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [tasksRes, progressRes, coursesRes, assignmentsRes, deadlinesRes] =
        await Promise.all([
          fetch(`${API_BASE}/analytics/prioritize`, {
            method: 'POST',
            headers: headers(),
            body: JSON.stringify({ max_tasks: 20 }),
          }),
          fetch(`${API_BASE}/analytics/progress`, { headers: headers() }),
          fetch(`${API_BASE}/courses/`, { headers: headers() }),
          fetch(`${API_BASE}/assignments/`, { headers: headers() }),
          fetch(`${API_BASE}/deadlines/`, { headers: headers() }),
        ])

      if (!coursesRes.ok) throw new Error('Failed to fetch data. Check your API key.')

      const tasksData = tasksRes.ok ? await tasksRes.json() : { tasks: [] }
      const progressData = progressRes.ok ? await progressRes.json() : { courses: [] }
      const coursesData = await coursesRes.json()
      const assignmentsData = assignmentsRes.ok ? await assignmentsRes.json() : []
      const deadlinesData = deadlinesRes.ok ? await deadlinesRes.json() : []

      setTasks(tasksData.tasks || [])
      setProgress(progressData.courses || [])
      setCourses(coursesData)
      setAssignments(assignmentsData)
      setDeadlines(deadlinesData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const handleDisconnect = () => {
    setIsAuthenticated(false)
    setApiKey('')
    localStorage.removeItem('do_api_key')
    setTasks([])
    setProgress([])
    setCourses([])
    setAssignments([])
    setDeadlines([])
  }

  // ── Deadline CRUD ────────────────────────────────────────────────

  const createDeadline = async (data: {
    assignment_id: number
    due_date: string
    is_final: boolean
    notes: string
  }) => {
    try {
      setError(null)
      setSuccess(null)
      const resp = await fetch(`${API_BASE}/deadlines/`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(data),
      })
      if (!resp.ok) {
        const err = await resp.json()
        throw new Error(err.detail || 'Failed to create deadline')
      }
      setSuccess('Deadline created!')
      await fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create deadline')
    }
  }

  const deleteDeadline = async (deadlineId: number) => {
    if (!confirm('Delete this deadline?')) return
    try {
      setError(null)
      setSuccess(null)
      const resp = await fetch(`${API_BASE}/deadlines/${deadlineId}`, {
        method: 'DELETE',
        headers: headers(),
      })
      if (!resp.ok && resp.status !== 204) {
        const err = await resp.json()
        throw new Error(err.detail || 'Failed to delete deadline')
      }
      setSuccess('Deadline deleted!')
      await fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete deadline')
    }
  }

  // ── Assignment CRUD ──────────────────────────────────────────────

  const createAssignment = async (data: {
    course_id: number
    title: string
    description: string
    assignment_type: string
    weight: number
    estimated_hours: number | null
    priority: string
  }) => {
    try {
      setError(null)
      setSuccess(null)
      const resp = await fetch(`${API_BASE}/assignments/`, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(data),
      })
      if (!resp.ok) {
        const err = await resp.json()
        throw new Error(err.detail || 'Failed to create assignment')
      }
      setSuccess('Assignment created!')
      await fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create assignment')
    }
  }

  const deleteAssignment = async (assignmentId: number) => {
    if (!confirm('Delete this assignment and all its deadlines?')) return
    try {
      setError(null)
      setSuccess(null)
      const resp = await fetch(`${API_BASE}/assignments/${assignmentId}`, {
        method: 'DELETE',
        headers: headers(),
      })
      if (!resp.ok && resp.status !== 204) {
        const err = await resp.json()
        throw new Error(err.detail || 'Failed to delete assignment')
      }
      setSuccess('Assignment deleted!')
      await fetchData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete assignment')
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="login-container">
        <div className="login-card">
          <h1>📅 Assignment Deadline Optimizer</h1>
          <p>AI-powered personal deadline tracker</p>
          <form onSubmit={handleApiKeySubmit}>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter API Key"
              className="api-key-input"
              autoFocus
            />
            <button type="submit" className="login-button">
              Connect
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📅 Deadline Optimizer</h1>
        <nav className="app-nav">
          <button className={view === 'tasks' ? 'active' : ''} onClick={() => setView('tasks')}>
            📋 Tasks
          </button>
          <button className={view === 'dashboard' ? 'active' : ''} onClick={() => setView('dashboard')}>
            📊 Dashboard
          </button>
          <button className={view === 'manage' ? 'active' : ''} onClick={() => setView('manage')}>
            ⚙️ Manage
          </button>
        </nav>
        <button onClick={handleDisconnect} className="disconnect-button">
          Disconnect
        </button>
      </header>

      {error && <div className="error-message">❌ {error}</div>}
      {success && <div className="success-message">✅ {success}</div>}
      {loading && <div className="loading">Loading...</div>}

      <main>
        {view === 'tasks' && (
          <TaskListView tasks={tasks} courses={courses} onRefresh={fetchData} />
        )}
        {view === 'dashboard' && <Dashboard progress={progress} courses={courses} />}
        {view === 'manage' && (
          <ManageView
            courses={courses}
            assignments={assignments}
            deadlines={deadlines}
            onCreateDeadline={createDeadline}
            onDeleteDeadline={deleteDeadline}
            onCreateAssignment={createAssignment}
            onDeleteAssignment={deleteAssignment}
            onRefresh={fetchData}
          />
        )}
      </main>
    </div>
  )
}

// ── Task List View ──────────────────────────────────────────────────────

function TaskListView({
  tasks,
  courses,
  onRefresh,
}: {
  tasks: PrioritizedTask[]
  courses: Course[]
  onRefresh: () => void
}) {
  const getCourseName = (courseId: number) => {
    const course = courses.find((c) => c.id === courseId)
    return course ? `${course.code} - ${course.name}` : 'Unknown Course'
  }

  const getCourseColor = (courseId: number) => {
    const course = courses.find((c) => c.id === courseId)
    return course?.color || '#3B82F6'
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleString()
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical': return '#EF4444'
      case 'high': return '#F97316'
      case 'medium': return '#F59E0B'
      case 'low': return '#10B981'
      default: return '#6B7280'
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'not_started': return '⬜ Not Started'
      case 'in_progress': return '🔄 In Progress'
      case 'submitted': return '📤 Submitted'
      case 'completed': return '✅ Completed'
      case 'overdue': return '🚨 Overdue'
      default: return status
    }
  }

  if (tasks.length === 0) {
    return (
      <div className="task-list-empty">
        <p>No pending tasks found. You're all caught up! 🎉</p>
        <button onClick={onRefresh}>Refresh</button>
      </div>
    )
  }

  return (
    <div className="task-list">
      {tasks.map((task) => (
        <div key={task.assignment.id} className="task-card">
          <div className="task-priority-bar" style={{ backgroundColor: getRiskColor(task.risk_level) }} />
          <div className="task-content">
            <div className="task-header">
              <h3>{task.assignment.title}</h3>
              <span className="priority-score" style={{ backgroundColor: getRiskColor(task.risk_level) }}>
                Score: {task.priority_score}
              </span>
            </div>
            <div className="task-course" style={{ color: getCourseColor(task.assignment.course_id) }}>
              {getCourseName(task.assignment.course_id)}
            </div>
            <div className="task-meta">
              <span>{getStatusBadge(task.assignment.status)}</span>
              <span>📝 {task.assignment.assignment_type}</span>
              <span>💯 {task.assignment.weight}% of grade</span>
              {task.assignment.estimated_hours && <span>⏱️ ~{task.assignment.estimated_hours}h</span>}
            </div>
            <div className="task-deadline">
              📅 Due: {formatDate(task.deadline.due_date)}
              {task.deadline.notes && <span className="deadline-notes">({task.deadline.notes})</span>}
            </div>
            <div className="task-recommendation">{task.recommendation}</div>
            {task.conflict_warnings.length > 0 && (
              <div className="conflict-warnings">⚠️ {task.conflict_warnings.join(', ')}</div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

// ── Manage View (Create / Delete Deadlines & Assignments) ───────────────

function ManageView({
  courses,
  assignments,
  deadlines,
  onCreateDeadline,
  onDeleteDeadline,
  onCreateAssignment,
  onDeleteAssignment,
  onRefresh,
}: {
  courses: Course[]
  assignments: Assignment[]
  deadlines: Deadline[]
  onCreateDeadline: (data: { assignment_id: number; due_date: string; is_final: boolean; notes: string }) => void
  onDeleteDeadline: (id: number) => void
  onCreateAssignment: (data: { course_id: number; title: string; description: string; assignment_type: string; weight: number; estimated_hours: number | null; priority: string }) => void
  onDeleteAssignment: (id: number) => void
  onRefresh: () => void
}) {
  // Deadline form state
  const [dlAssignmentId, setDlAssignmentId] = useState<number>(assignments[0]?.id || 0)
  const [dlDate, setDlDate] = useState('')
  const [dlTime, setDlTime] = useState('23:59')
  const [dlNotes, setDlNotes] = useState('')
  const [dlFinal, setDlFinal] = useState(true)

  // Assignment form state
  const [asCourseId, setAsCourseId] = useState<number>(courses[0]?.id || 0)
  const [asTitle, setAsTitle] = useState('')
  const [asDesc, setAsDesc] = useState('')
  const [asType, setAsType] = useState('homework')
  const [asWeight, setAsWeight] = useState(10)
  const [asHours, setAsHours] = useState('')
  const [asPriority, setAsPriority] = useState('medium')

  const handleDeadlineSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!dlAssignmentId || !dlDate) return
    const due_date = `${dlDate}T${dlTime}:00Z`
    onCreateDeadline({ assignment_id: dlAssignmentId, due_date, is_final: dlFinal, notes: dlNotes })
    setDlDate('')
    setDlNotes('')
  }

  const handleAssignmentSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!asTitle.trim()) return
    onCreateAssignment({
      course_id: asCourseId,
      title: asTitle,
      description: asDesc,
      assignment_type: asType,
      weight: asWeight,
      estimated_hours: asHours ? parseFloat(asHours) : null,
      priority: asPriority,
    })
    setAsTitle('')
    setAsDesc('')
    setAsHours('')
  }

  const getAssignmentTitle = (assignmentId: number) => {
    const a = assignments.find((x) => x.id === assignmentId)
    return a ? a.title : `Assignment #${assignmentId}`
  }

  return (
    <div className="manage-view">
      {/* ── Create Deadline ─────────────────────────────────────── */}
      <section className="manage-section">
        <h2>➕ Create Deadline</h2>
        <form onSubmit={handleDeadlineSubmit} className="manage-form">
          <div className="form-group">
            <label>Assignment</label>
            <select value={dlAssignmentId} onChange={(e) => setDlAssignmentId(Number(e.target.value))} required>
              {assignments.map((a) => (
                <option key={a.id} value={a.id}>{a.title}</option>
              ))}
            </select>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Date</label>
              <input type="date" value={dlDate} onChange={(e) => setDlDate(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Time</label>
              <input type="time" value={dlTime} onChange={(e) => setDlTime(e.target.value)} required />
            </div>
          </div>
          <div className="form-group">
            <label>Notes</label>
            <input type="text" value={dlNotes} onChange={(e) => setDlNotes(e.target.value)} placeholder="e.g. Submit via Moodle" />
          </div>
          <div className="form-group checkbox-group">
            <label>
              <input type="checkbox" checked={dlFinal} onChange={(e) => setDlFinal(e.target.checked)} />
              Final deadline
            </label>
          </div>
          <button type="submit" className="btn-primary" disabled={assignments.length === 0}>
            Create Deadline
          </button>
        </form>
      </section>

      {/* ── Create Assignment ───────────────────────────────────── */}
      <section className="manage-section">
        <h2>➕ Create Assignment</h2>
        <form onSubmit={handleAssignmentSubmit} className="manage-form">
          <div className="form-group">
            <label>Course</label>
            <select value={asCourseId} onChange={(e) => setAsCourseId(Number(e.target.value))} required>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>{c.code} — {c.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Title</label>
            <input type="text" value={asTitle} onChange={(e) => setAsTitle(e.target.value)} placeholder="e.g. Lab Report 3" required />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea value={asDesc} onChange={(e) => setAsDesc(e.target.value)} placeholder="Optional description" rows={2} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Type</label>
              <select value={asType} onChange={(e) => setAsType(e.target.value)}>
                <option value="homework">Homework</option>
                <option value="lab">Lab</option>
                <option value="exam">Exam</option>
                <option value="project">Project</option>
                <option value="quiz">Quiz</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label>Weight (%)</label>
              <input type="number" value={asWeight} onChange={(e) => setAsWeight(Number(e.target.value))} min={0} max={100} step={0.5} required />
            </div>
            <div className="form-group">
              <label>Est. hours</label>
              <input type="number" value={asHours} onChange={(e) => setAsHours(e.target.value)} min={0} step={0.5} placeholder="optional" />
            </div>
          </div>
          <div className="form-group">
            <label>Priority</label>
            <select value={asPriority} onChange={(e) => setAsPriority(e.target.value)}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
          <button type="submit" className="btn-primary" disabled={courses.length === 0}>
            Create Assignment
          </button>
        </form>
      </section>

      {/* ── Existing Deadlines ──────────────────────────────────── */}
      <section className="manage-section">
        <h2>📅 Existing Deadlines ({deadlines.length})</h2>
        {deadlines.length === 0 ? (
          <p className="empty-text">No deadlines yet.</p>
        ) : (
          <table className="manage-table">
            <thead>
              <tr>
                <th>Assignment</th>
                <th>Due Date</th>
                <th>Final</th>
                <th>Notes</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {deadlines.sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime()).map((dl) => (
                <tr key={dl.id}>
                  <td>{getAssignmentTitle(dl.assignment_id)}</td>
                  <td>{new Date(dl.due_date).toLocaleString()}</td>
                  <td>{dl.is_final ? '✅ Yes' : '❌ No'}</td>
                  <td>{dl.notes || '—'}</td>
                  <td>
                    <button className="btn-danger" onClick={() => onDeleteDeadline(dl.id)}>
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* ── Existing Assignments ────────────────────────────────── */}
      <section className="manage-section">
        <h2>📝 Existing Assignments ({assignments.length})</h2>
        {assignments.length === 0 ? (
          <p className="empty-text">No assignments yet.</p>
        ) : (
          <table className="manage-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Course ID</th>
                <th>Type</th>
                <th>Weight</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {assignments.map((a) => (
                <tr key={a.id}>
                  <td>{a.title}</td>
                  <td>{a.course_id}</td>
                  <td>{a.assignment_type}</td>
                  <td>{a.weight}%</td>
                  <td>{a.status}</td>
                  <td>
                    <button className="btn-danger" onClick={() => onDeleteAssignment(a.id)}>
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <div className="manage-actions">
        <button className="btn-secondary" onClick={onRefresh}>🔄 Refresh All</button>
      </div>
    </div>
  )
}

export default App
