import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend } from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'

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

interface Course {
  id: number
  name: string
  code: string
  color: string | null
}

interface DashboardProps {
  progress: CourseProgress[]
  courses: Course[]
}

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

function Dashboard({ progress, courses }: DashboardProps) {
  const getCompletionData = () => {
    return {
      labels: progress.map((p) => p.course_code),
      datasets: [
        {
          label: 'Completion %',
          data: progress.map((p) => p.completion_percentage),
          backgroundColor: courses.map((c) => c.color || '#3B82F6'),
          borderColor: courses.map((c) => c.color || '#3B82F6'),
          borderWidth: 1,
        },
      ],
    }
  }

  const getStatusData = () => {
    const totalCompleted = progress.reduce((sum, p) => sum + p.completed, 0)
    const totalInProgress = progress.reduce((sum, p) => sum + p.in_progress, 0)
    const totalNotStarted = progress.reduce((sum, p) => sum + p.not_started, 0)
    const totalOverdue = progress.reduce((sum, p) => sum + p.overdue, 0)

    return {
      labels: ['Completed', 'In Progress', 'Not Started', 'Overdue'],
      datasets: [
        {
          data: [totalCompleted, totalInProgress, totalNotStarted, totalOverdue],
          backgroundColor: ['#10B981', '#3B82F6', '#6B7280', '#EF4444'],
          borderWidth: 0,
        },
      ],
    }
  }

  const getWorkloadData = () => {
    return {
      labels: progress.map((p) => p.course_code),
      datasets: [
        {
          label: 'Total Assignments',
          data: progress.map((p) => p.total_assignments),
          backgroundColor: '#8B5CF6',
        },
        {
          label: 'Completed',
          data: progress.map((p) => p.completed),
          backgroundColor: '#10B981',
        },
      ],
    }
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
  }

  const overallCompletion = () => {
    const total = progress.reduce((sum, p) => sum + p.total_assignments, 0)
    const completed = progress.reduce((sum, p) => sum + p.completed, 0)
    return total > 0 ? ((completed / total) * 100).toFixed(1) : '0.0'
  }

  return (
    <div className="dashboard">
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-value">{overallCompletion()}%</div>
          <div className="stat-label">Overall Completion</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{progress.length}</div>
          <div className="stat-label">Active Courses</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {progress.reduce((sum, p) => sum + p.total_assignments, 0)}
          </div>
          <div className="stat-label">Total Assignments</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#EF4444' }}>
            {progress.reduce((sum, p) => sum + p.overdue, 0)}
          </div>
          <div className="stat-label">Overdue Tasks</div>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="chart-card">
          <h3>Course Completion Rates</h3>
          <div style={{ height: '300px' }}>
            <Bar data={getCompletionData()} options={chartOptions} />
          </div>
        </div>

        <div className="chart-card">
          <h3>Task Status Distribution</h3>
          <div style={{ height: '300px' }}>
            <Doughnut data={getStatusData()} />
          </div>
        </div>

        <div className="chart-card">
          <h3>Workload by Course</h3>
          <div style={{ height: '300px' }}>
            <Bar data={getWorkloadData()} options={chartOptions} />
          </div>
        </div>
      </div>

      <div className="chart-card">
        <h3>Detailed Progress</h3>
        <table className="progress-table">
          <thead>
            <tr>
              <th>Course</th>
              <th>Total</th>
              <th>Completed</th>
              <th>In Progress</th>
              <th>Not Started</th>
              <th>Overdue</th>
              <th>Completion</th>
            </tr>
          </thead>
          <tbody>
            {progress.map((p) => (
              <tr key={p.course_id}>
                <td>
                  {p.course_code} - {p.course_name}
                </td>
                <td>{p.total_assignments}</td>
                <td>{p.completed}</td>
                <td>{p.in_progress}</td>
                <td>{p.not_started}</td>
                <td style={{ color: p.overdue > 0 ? '#EF4444' : 'inherit' }}>{p.overdue}</td>
                <td>
                  <div className="progress-bar-container">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${p.completion_percentage}%` }}
                    />
                  </div>
                  <span>{p.completion_percentage}%</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Dashboard
