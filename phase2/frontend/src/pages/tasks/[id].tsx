import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getAuthToken } from '../../../src/utils/auth';

interface Task {
  id: string;
  content: string;
  user_id: string;
}

const TaskDetailPage: React.FC = () => {
  const router = useRouter();
  const { id } = router.query;
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [editedContent, setEditedContent] = useState('');

  useEffect(() => {
    if (!id) return;

    const fetchTask = async () => {
      const token = getAuthToken();
      if (!token) {
        router.push('/login');
        return;
      }

      try {
        const response = await fetch(`/tasks/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data: Task = await response.json();
          setTask(data);
          setEditedContent(data.content);
        } else if (response.status === 401) {
          router.push('/login');
        } else {
          const errData = await response.json();
          setError(errData.detail || 'Failed to fetch task');
        }
      } catch (err) {
        setError('Network error or server unreachable');
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [id, router]);

  const handleUpdate = async () => {
    const token = getAuthToken();
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const response = await fetch(`/tasks/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ content: editedContent }),
      });

      if (response.ok) {
        const updatedTask: Task = await response.json();
        setTask(updatedTask);
        setEditMode(false);
      } else if (response.status === 401) {
        router.push('/login');
      } else {
        const errData = await response.json();
        setError(errData.detail || 'Failed to update task');
      }
    } catch (err) {
      setError('Network error or server unreachable');
    }
  };

  const handleDelete = async () => {
    const token = getAuthToken();
    if (!token) {
      router.push('/login');
      return;
    }

    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      const response = await fetch(`/tasks/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.status === 204) {
        router.push('/tasks'); // Redirect to tasks list after deletion
      } else if (response.status === 401) {
        router.push('/login');
      } else {
        const errData = await response.json();
        setError(errData.detail || 'Failed to delete task');
      }
    } catch (err) {
      setError('Network error or server unreachable');
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading task...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>Error: {error}</div>;
  }

  if (!task) {
    return <div style={{ textAlign: 'center', marginTop: '50px' }}>Task not found.</div>;
  }

  return (
    <div style={{ maxWidth: '800px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <button onClick={() => router.push('/tasks')} style={{ marginBottom: '20px', padding: '8px 12px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
        Back to Tasks
      </button>
      <h1>Task: {task.content}</h1>
      {editMode ? (
        <div>
          <textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            style={{ width: '100%', minHeight: '100px', padding: '10px', boxSizing: 'border-box', borderRadius: '4px', border: '1px solid #ddd', marginBottom: '10px' }}
          />
          <button onClick={handleUpdate} style={{ padding: '10px 15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '10px' }}>
            Save
          </button>
          <button onClick={() => setEditMode(false)} style={{ padding: '10px 15px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Cancel
          </button>
        </div>
      ) : (
        <div>
          <p>{task.content}</p>
          <button onClick={() => setEditMode(true)} style={{ padding: '10px 15px', backgroundColor: '#ffc107', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '10px' }}>
            Edit
          </button>
          <button onClick={handleDelete} style={{ padding: '10px 15px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Delete
          </button>
        </div>
      )}
    </div>
  );
};

export default TaskDetailPage;
