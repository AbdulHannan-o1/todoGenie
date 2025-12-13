import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getAuthToken } from '../../src/utils/auth';

interface Task {
  id: string;
  content: string;
  user_id: string;
}

const TasksPage: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const fetchTasks = async () => {
      const token = getAuthToken();
      if (!token) {
        router.push('/login');
        return;
      }

      try {
        const response = await fetch('/tasks', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data: Task[] = await response.json();
          setTasks(data);
        } else if (response.status === 401) {
          router.push('/login');
        } else {
          const errData = await response.json();
          setError(errData.detail || 'Failed to fetch tasks');
        }
      } catch (err) {
        setError('Network error or server unreachable');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [router]);

  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading tasks...</div>;
  }

  if (error) {
    return <div style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>Error: {error}</div>;
  }

  return (
    <div style={{ maxWidth: '800px', margin: '50px auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h1>My Tasks</h1>
      {tasks.length === 0 ? (
        <p>No tasks found. Start by adding a new one!</p>
      ) : (
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          {tasks.map((task) => (
            <li key={task.id} style={{ padding: '10px 0', borderBottom: '1px solid #eee' }}>
              {task.content}
            </li>
          ))}
        </ul>
      )}
      {/* Add a link or button to create new tasks */}
      <button onClick={() => router.push('/new-task')} style={{ marginTop: '20px', padding: '10px 15px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
        Add New Task
      </button>
    </div>
  );
};

export default TasksPage;
