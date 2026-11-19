 
import { useEffect, useMemo, useState } from "react";
import "./App.css";
 
const API = "/api";
 
function App() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
 
  async function request(path, options = {}) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
 
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
 
    return response.status === 204 ? null : response.json();
  }
 
  async function loadTasks() {
    try {
      setError("");
      const data = await request("/tasks");
      setTasks(data);
    } catch (err) {
      setError("Unable to load tasks. Check whether the API is running.");
    } finally {
      setLoading(false);
    }
  }
 
  useEffect(() => {
    loadTasks();
  }, []);
 
  async function addTask(e) {
    e.preventDefault();
    if (!title.trim()) return;
 
    try {
      const task = await request("/tasks", {
        method: "POST",
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim(),
        }),
      });
 
      setTasks((current) => [...current, task]);
      setTitle("");
      setDescription("");
      setError("");
    } catch {
      setError("Could not create the task.");
    }
  }
 
  async function toggleTask(task) {
    try {
      const updated = await request(`/tasks/${task.id}`, {
        method: "PUT",
        body: JSON.stringify({
          title: task.title,
          description: task.description,
          completed: !task.completed,
        }),
      });
 
      setTasks((current) =>
        current.map((item) => item.id === task.id ? updated : item)
      );
    } catch {
      setError("Could not update the task.");
    }
  }
 
  async function deleteTask(id) {
    if (!window.confirm("Delete this task permanently?")) return;
 
    try {
      await request(`/tasks/${id}`, { method: "DELETE" });
      setTasks((current) => current.filter((task) => task.id !== id));
      if (editingId === id) setEditingId(null);
    } catch {
      setError("Could not delete the task.");
    }
  }
 
  function startEditing(task) {
    setEditingId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description || "");
  }
 
  async function saveEdit(id) {
    if (!editTitle.trim()) return;
 
    try {
      const updated = await request(`/tasks/${id}`, {
        method: "PUT",
        body: JSON.stringify({
          title: editTitle.trim(),
          description: editDescription.trim(),
          completed: tasks.find((task) => task.id === id).completed,
        }),
      });
 
      setTasks((current) =>
        current.map((task) => task.id === id ? updated : task)
      );
      setEditingId(null);
    } catch {
      setError("Could not save your changes.");
    }
  }
 
  const completedCount = tasks.filter((task) => task.completed).length;
  const pendingCount = tasks.length - completedCount;
 
  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      const matchesSearch =
        `${task.title} ${task.description || ""}`
          .toLowerCase()
          .includes(search.toLowerCase());
 
      const matchesFilter =
        filter === "all" ||
        (filter === "completed" && task.completed) ||
        (filter === "pending" && !task.completed);
 
      return matchesSearch && matchesFilter;
    });
  }, [tasks, search, filter]);
 
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">✓</div>
          <span>TaskFlow</span>
        </div>
 
        <p className="nav-label">WORKSPACE</p>
        <button className="nav-item active">▦ &nbsp; Overview</button>
        <button className="nav-item" onClick={() => setFilter("all")}>
          ☰ &nbsp; All tasks
        </button>
        <button className="nav-item" onClick={() => setFilter("pending")}>
          ◷ &nbsp; Pending
        </button>
        <button className="nav-item" onClick={() => setFilter("completed")}>
          ✓ &nbsp; Completed
        </button>
 
        <div className="sidebar-bottom">
          <div className="profile-avatar">M</div>
          <div>
            <strong>My Workspace</strong>
            <small>Personal dashboard</small>
          </div>
        </div>
      </aside>
 
      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">WORKSPACE / OVERVIEW</span>
            <h1>My Dashboard</h1>
            <p>Stay organized. Get things done.</p>
          </div>
          <div className="date-chip">
            <span>●</span> Workspace active
          </div>
        </header>
 
        {error && <div className="error-message">{error}</div>}
 
        <section className="stats-grid">
          <div className="stat-card">
            <span className="stat-icon blue">▦</span>
            <p>Total tasks</p>
            <h2>{tasks.length}</h2>
            <small>All your tasks</small>
          </div>
          <div className="stat-card">
            <span className="stat-icon green">✓</span>
            <p>Completed</p>
            <h2>{completedCount}</h2>
            <small>Successfully finished</small>
          </div>
          <div className="stat-card">
            <span className="stat-icon orange">◷</span>
            <p>Pending</p>
            <h2>{pendingCount}</h2>
            <small>Awaiting completion</small>
          </div>
        </section>
 
        <section className="task-panel">
          <div className="section-heading">
            <div>
              <h2>Create a task</h2>
              <p>Add something you want to accomplish.</p>
            </div>
          </div>
 
          <form className="task-form" onSubmit={addTask}>
            <input
              placeholder="Task title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <input
              placeholder="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <button className="primary-button" type="submit">
              + Add task
            </button>
          </form>
        </section>
 
        <section className="task-section">
          <div className="section-heading task-heading">
            <div>
              <h2>Your tasks</h2>
              <p>{filteredTasks.length} tasks displayed</p>
            </div>
 
            <input
              className="search-input"
              placeholder="⌕  Search tasks..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
 
          <div className="filter-tabs">
            {["all", "pending", "completed"].map((item) => (
              <button
                key={item}
                className={filter === item ? "filter active-filter" : "filter"}
                onClick={() => setFilter(item)}
              >
                {item.charAt(0).toUpperCase() + item.slice(1)}
              </button>
            ))}
          </div>
 
          <div className="task-list">
            {loading ? (
              <div className="empty-state">Loading your tasks...</div>
            ) : filteredTasks.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">✓</div>
                <h3>No tasks found</h3>
                <p>Add a task or change your search/filter.</p>
              </div>
            ) : (
              filteredTasks.map((task) => (
                <article className="task-card" key={task.id}>
                  {editingId === task.id ? (
                    <div className="edit-form">
                      <input
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        placeholder="Task title"
                      />
                      <input
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        placeholder="Description"
                      />
                      <div className="actions">
                        <button className="primary-button" onClick={() => saveEdit(task.id)}>
                          Save
                        </button>
                        <button className="secondary-button" onClick={() => setEditingId(null)}>
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="task-info">
                        <div className={task.completed ? "task-check checked" : "task-check"}>
                          {task.completed ? "✓" : ""}
                        </div>
                        <div>
                          <h3 className={task.completed ? "task-done" : ""}>
                            {task.title}
                          </h3>
                          {task.description && <p>{task.description}</p>}
                          <span className={task.completed ? "status completed" : "status pending"}>
                            {task.completed ? "Completed" : "Pending"}
                          </span>
                        </div>
                      </div>
 
                      <div className="actions">
                        <button className="secondary-button" onClick={() => startEditing(task)}>
                          Edit
                        </button>
                        <button className="primary-button" onClick={() => toggleTask(task)}>
                          {task.completed ? "Undo" : "Complete"}
                        </button>
                        <button className="danger-button" onClick={() => deleteTask(task.id)}>
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </article>
              ))
            )}
          </div>
        </section>
 
        <footer className="footer">
          TaskFlow · Built with React, FastAPI and PostgreSQL
        </footer>
      </main>
    </div>
  );
}
 
export default App;
 