'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import ProtectedRoute from '../components/auth/protected-route';
import TaskForm from '../components/tasks/task-form';
import TaskUpdateForm from '../components/tasks/task-update-form';
import LogoutButton from '../components/auth/logout';
import ChatInterface from '../components/chat/chat-interface';
import apiService from '../lib/api';
import authClient from '../lib/auth';

export default function DashboardPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [showTaskList, setShowTaskList] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [userInfo, setUserInfo] = useState({ userId: null, token: null });
  const router = useRouter();

  // Load user info on component mount
  useEffect(() => {
    const loadUserInfo = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (token) {
          // Get user info from API to get the user ID
          const response = await fetch('http://localhost:8000/api/auth/user', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            const userData = await response.json();
            setUserInfo({ userId: userData.id, token });
          } else {
            // If token is invalid, clear it
            localStorage.removeItem('auth_token');
            setUserInfo({ userId: null, token: null });
          }
        }
      } catch (error) {
        console.error('Error loading user info:', error);
        setUserInfo({ userId: null, token: null });
      }
    };

    loadUserInfo();
  }, []);

  useEffect(() => {
    fetchTasks(); // Fetch tasks on initial load to show the most recent task
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const tasksData = await apiService.getTasks();
      setTasks(tasksData);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      if (error.message.includes('Authentication required')) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };


  const handleTaskCreated = (newTask) => {
    setTasks(prev => [...prev, newTask]);
    setShowForm(false);
  };

  const handleToggleCompletion = async (taskId) => {
    try {
      const updatedTask = await apiService.toggleTaskCompletion(taskId);

      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? { ...task, completed: updatedTask.completed, completed_at: updatedTask.completed_at } : task
        )
      );
    } catch (error) {
      console.error('Error toggling task completion:', error);
      alert('Failed to update task completion status: ' + error.message);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await apiService.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (error) {
      console.error('Error deleting task:', error);
      alert('Failed to delete task: ' + error.message);
    }
  };

  const handleUpdateTask = async (taskId, updatedData) => {
    try {
      const updatedTask = await apiService.updateTask(taskId, updatedData);

      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? { ...task, ...updatedTask } : task
        )
      );

      setEditingTask(null);
    } catch (error) {
      console.error('Error updating task:', error);
      alert('Failed to update task: ' + error.message);
    }
  };

  const handleViewTaskList = async () => {
    if (showTaskList) {
      // If task list is currently shown, hide it
      setShowTaskList(false);
    } else {
      // If task list is currently hidden, fetch and show it
      await fetchTasks(); // Fetch tasks
      setShowTaskList(true); // Show task list after fetching
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Todo Dashboard</h1>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowChat(!showChat)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
              >
                {showChat ? 'Hide Chat' : 'AI Chat Assistant'}
              </button>
              <a
                href="/signup"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Sign Up
              </a>
              <LogoutButton />
            </div>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
              {/* Chat Interface */}
              {showChat && (
                <div className="mb-6 bg-white p-4 rounded-lg shadow-md">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">AI Task Assistant</h2>
                  <div className="h-96">
                    <ChatInterface userId={userInfo.userId} token={userInfo.token} />
                  </div>
                </div>
              )}

              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-800">Your Tasks</h2>
                <div className="flex space-x-3">
                  <button
                    onClick={handleViewTaskList}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    View Task List
                  </button>
                  <button
                    onClick={() => setShowForm(!showForm)}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    {showForm ? 'Cancel' : 'Add Task'}
                  </button>
                </div>
              </div>

              {showForm && (
                <TaskForm
                  onTaskCreated={handleTaskCreated}
                  onCancel={() => setShowForm(false)}
                />
              )}

              {!showTaskList && !showForm && (
                <>
                  {loading ? (
                    <div className="text-center py-10">
                      <p className="text-gray-600">Loading tasks...</p>
                    </div>
                  ) : tasks.length === 0 ? (
                    <div className="text-center py-10">
                      <p className="text-gray-600">No tasks yet. Add your first task!</p>
                    </div>
                  ) : (
                    // Show the most recent task by default
                    <div className="bg-white shadow overflow-hidden rounded-md">
                      {tasks.slice(0, 1).map((task) => (
                        <div key={task.id}>
                          {editingTask?.id === task.id ? (
                            <TaskUpdateForm
                              task={task}
                              onUpdateTask={handleUpdateTask}
                              onCancel={() => setEditingTask(null)}
                            />
                          ) : (
                            <div
                              className={`px-6 py-4 border-b border-gray-200 ${task.completed ? 'bg-green-50' : 'bg-white'}`}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                  <input
                                    type="checkbox"
                                    checked={task.completed}
                                    onChange={() => handleToggleCompletion(task.id)}
                                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                  />
                                  <span className={`ml-3 text-lg ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                                    {task.title}
                                  </span>
                                </div>
                                <div className="flex items-center space-x-2">
                                  {task.description && (
                                    <span className="text-sm text-gray-500 italic">
                                      {task.description}
                                    </span>
                                  )}
                                  <button
                                    onClick={() => setEditingTask(task)}
                                    className="text-blue-600 hover:text-blue-900"
                                  >
                                    Edit
                                  </button>
                                  <button
                                    onClick={() => handleDeleteTask(task.id)}
                                    className="text-red-600 hover:text-red-900"
                                  >
                                    Delete
                                  </button>
                                </div>
                              </div>
                              {task.created_at && (
                                <div className="mt-1 text-xs text-gray-500">
                                  Created: {new Date(task.created_at).toLocaleString('en-US', { timeZone: 'Asia/Karachi', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: true })}
                                  {task.completed_at && (
                                    <span>, Completed: {new Date(task.completed_at).toLocaleString('en-US', { timeZone: 'Asia/Karachi', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: true })}</span>
                                  )}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}

              {showTaskList && (
                <>
                  {loading ? (
                    <div className="text-center py-10">
                      <p className="text-gray-600">Loading tasks...</p>
                    </div>
                  ) : tasks.length === 0 ? (
                    <div className="text-center py-10">
                      <p className="text-gray-600">No tasks yet. Add your first task!</p>
                    </div>
                  ) : (
                    <ul className="bg-white shadow overflow-hidden rounded-md">
                      {tasks.map((task) => (
                        <div key={task.id}>
                          {editingTask?.id === task.id ? (
                            <TaskUpdateForm
                              task={task}
                              onUpdateTask={handleUpdateTask}
                              onCancel={() => setEditingTask(null)}
                            />
                          ) : (
                            <li
                              className={`px-6 py-4 border-b border-gray-200 ${task.completed ? 'bg-green-50' : 'bg-white'}`}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                  <input
                                    type="checkbox"
                                    checked={task.completed}
                                    onChange={() => handleToggleCompletion(task.id)}
                                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                  />
                                  <span className={`ml-3 text-lg ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                                    {task.title}
                                  </span>
                                </div>
                                <div className="flex items-center space-x-2">
                                  {task.description && (
                                    <span className="text-sm text-gray-500 italic">
                                      {task.description}
                                    </span>
                                  )}
                                  <button
                                    onClick={() => setEditingTask(task)}
                                    className="text-blue-600 hover:text-blue-900"
                                  >
                                    Edit
                                  </button>
                                  <button
                                    onClick={() => handleDeleteTask(task.id)}
                                    className="text-red-600 hover:text-red-900"
                                  >
                                    Delete
                                  </button>
                                </div>
                              </div>
                              {task.created_at && (
                                <div className="mt-1 text-xs text-gray-500">
                                  Created: {new Date(task.created_at).toLocaleString('en-US', { timeZone: 'Asia/Karachi', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: true })}
                                  {task.completed_at && (
                                    <span>, Completed: {new Date(task.completed_at).toLocaleString('en-US', { timeZone: 'Asia/Karachi', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: true })}</span>
                                  )}
                                </div>
                              )}
                            </li>
                          )}
                        </div>
                      ))}
                    </ul>
                  )}
                </>
              )}
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}