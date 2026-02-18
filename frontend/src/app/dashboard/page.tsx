
'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import TaskForm from '@/components/tasks/task-form';
import TaskUpdateForm from '@/components/tasks/task-update-form';
import TaskFilters, { FilterState } from '@/components/tasks/task-filters';
import NotificationBell from '@/components/tasks/notification-bell';
import ChatInterface from '@/components/chat/chat-interface';
import apiService from '@/lib/api';
import LogoutButton from '@/components/auth/logout';
import { Task } from '@/types/task';

interface DashboardPageProps {}

export default function DashboardPage({}: DashboardPageProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showForm, setShowForm] = useState<boolean>(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [showTaskList, setShowTaskList] = useState<boolean>(false);
  const [showChat, setShowChat] = useState<boolean>(false);
  const [activeFilters, setActiveFilters] = useState<FilterState>({});
  const [userInfo, setUserInfo] = useState<{ userId: string | null; token: string | null }>({
    userId: null,
    token: null
  });
  const [authChecked, setAuthChecked] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (!token) {
          window.location.href = '/login';
          return;
        }

        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000/api';
        const response = await fetch(`${backendUrl}/auth/user`, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${token}` },
        });

        if (response.ok) {
          const userData = await response.json();
          setUserInfo({ userId: userData.id, token });
          setIsAuthenticated(true);
        } else {
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
      } catch (error) {
        console.error('Auth check error:', error);
        window.location.href = '/login';
      } finally {
        setAuthChecked(true);
      }
    };

    checkAuth();
  }, []);

  // Fetch tasks after auth
  const fetchTasks = useCallback(async (filters?: FilterState) => {
    if (!isAuthenticated) return;

    try {
      setLoading(true);
      const filterParams: Record<string, string> = {};
      const f = filters || activeFilters;
      if (f.priority) filterParams.priority = f.priority;
      if (f.status) filterParams.status = f.status;
      if (f.tag) filterParams.tag = f.tag;
      if (f.search) filterParams.search = f.search;
      if (f.sort_by) filterParams.sort_by = f.sort_by;
      if (f.sort_order) filterParams.sort_order = f.sort_order;
      const tasksData = await apiService.getTasks(Object.keys(filterParams).length > 0 ? filterParams : undefined);
      setTasks(tasksData);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      if ((error as Error).message.includes('Authentication required')) {
        window.location.href = '/login';
      }
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, activeFilters]);

  useEffect(() => {
    if (authChecked && isAuthenticated) {
      fetchTasks();
    }
  }, [authChecked, isAuthenticated, fetchTasks]);

  // Handlers
  const handleTaskCreated = (newTask: Task) => {
    setTasks(prev => [newTask, ...prev]);
    setShowForm(false);
  };

  const handleToggleCompletion = async (taskId: string) => {
    try {
      const updatedTask = await apiService.toggleTaskCompletion(taskId);
      setTasks(prev =>
        prev.map(task => (task.id === taskId ? { ...task, ...updatedTask } : task))
      );
    } catch (error) {
      console.error('Error toggling task completion:', error);
      alert('Failed to update task completion status: ' + (error as Error).message);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await apiService.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (error) {
      console.error('Error deleting task:', error);
      alert('Failed to delete task: ' + (error as Error).message);
    }
  };

  const handleUpdateTask = async (taskId: string, updatedData: Partial<Task>) => {
    try {
      const updatedTask = await apiService.updateTask(taskId, updatedData);
      setTasks(prev =>
        prev.map(task => (task.id === taskId ? { ...task, ...updatedTask } : task))
      );
      setEditingTask(null);
    } catch (error) {
      console.error('Error updating task:', error);
      alert('Failed to update task: ' + (error as Error).message);
    }
  };

  const handleFilterChange = (filters: FilterState) => {
    setActiveFilters(filters);
    fetchTasks(filters);
  };

  const handleViewTaskList = async () => {
    if (showTaskList) {
      setShowTaskList(false);
    } else {
      await fetchTasks();
      setShowTaskList(true);
    }
  };

  // ✅ Single return with conditional rendering
  return (
    <>
      {!authChecked ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-lg">Loading...</div>
        </div>
      ) : !isAuthenticated ? (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-lg">Redirecting to login...</div>
        </div>
      ) : (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 overflow-x-hidden">
          {/* Header */}
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8 flex justify-between items-center">
              <div className="flex items-center space-x-3">
                <div className="bg-indigo-600 p-2 rounded-lg flex-shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h1 className="text-2xl font-bold text-gray-900 truncate">Todo Dashboard</h1>
              </div>
              <div className="flex items-center space-x-3">
                <NotificationBell />
                <button
                  onClick={() => setShowChat(!showChat)}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-colors duration-200"
                >
                  {showChat ? 'Hide Chat' : 'AI Chat Assistant'}
                </button>
                <Link
                  href="/signup"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors duration-200"
                >
                  Sign Up
                </Link>
                <LogoutButton />
              </div>
            </div>
          </header>

          {/* Main */}
          <main>
            <div className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
              <div className="px-4 py-0 sm:px-0">
                {/* Chat Interface */}
                {showChat && (
                  <div className="mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-200 max-h-[400px]">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-xl font-semibold text-gray-800 flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2 text-purple-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                        </svg>
                        <span className="truncate">AI Task Assistant</span>
                      </h2>
                      <button onClick={() => setShowChat(false)} className="text-gray-400 hover:text-gray-600 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                    <div className="h-80 rounded-lg overflow-hidden">
                      <ChatInterface userId={userInfo.userId} token={userInfo.token} onTaskUpdate={fetchTasks} />
                    </div>
                  </div>
                )}

                {/* Task Controls */}
                <div className="flex justify-between items-center mb-8">
                  <h2 className="text-2xl font-semibold text-gray-800 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    <span className="truncate">Your Tasks</span>
                  </h2>
                  <div className="flex space-x-3">
                    <button
                      onClick={handleViewTaskList}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200"
                    >
                      {showTaskList ? 'Hide List' : 'View All'}
                    </button>
                    <button
                      onClick={() => setShowForm(!showForm)}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
                    >
                      {showForm ? 'Cancel' : 'Add Task'}
                    </button>
                  </div>
                </div>

                {/* Task Form */}
                {showForm && <TaskForm onTaskCreated={handleTaskCreated} onCancel={() => setShowForm(false)} />}

                {/* Filters */}
                {showTaskList && <TaskFilters onFilterChange={handleFilterChange} />}

                {/* Task List / Recent Task */}
                <div>
                  {loading ? (
                    <div className="text-center py-12">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                      <p className="text-gray-600">Loading tasks...</p>
                    </div>
                  ) : tasks.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
                      <p className="text-gray-600 text-lg">No tasks yet. Add your first task!</p>
                    </div>
                  ) : (
                    <ul className="bg-white shadow-sm rounded-xl overflow-y-auto max-h-[60vh] border border-gray-200 divide-y divide-gray-100">
                      {(showTaskList ? tasks : tasks.slice(0, 1)).map(task => (
                        <li key={task.id} className={`px-6 py-5 transition-colors duration-200 ${task.completed ? 'bg-green-50' : 'bg-white hover:bg-gray-50'}`}>
                          {editingTask?.id === task.id ? (
                            <TaskUpdateForm task={task} onUpdateTask={handleUpdateTask} onCancel={() => setEditingTask(null)} />
                          ) : (
                            <div className="flex items-center justify-between">
                              <div className="flex items-center">
                                <input
                                  type="checkbox"
                                  checked={task.completed}
                                  onChange={() => handleToggleCompletion(task.id)}
                                  className="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded focus:ring-2 focus:ring-offset-2 transition-colors flex-shrink-0"
                                />
                                <span className={`ml-4 text-lg font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-800'}`}>
                                  {task.title}
                                </span>
                                {task.priority && task.priority !== 'medium' && (
                                  <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium flex-shrink-0 ${
                                    task.priority === 'urgent' ? 'bg-red-100 text-red-700' :
                                    task.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                                    'bg-gray-100 text-gray-700'
                                  }`}>{task.priority}</span>
                                )}
                              </div>
                              <div className="flex items-center space-x-3">
                                {task.description && (
                                  <span className="text-sm text-gray-500 italic max-w-xs truncate flex-shrink-0" title={task.description}>
                                    {task.description}
                                  </span>
                                )}
                                <button onClick={() => setEditingTask(task)} className="text-blue-600 hover:text-blue-800 p-1 rounded-md hover:bg-blue-50 transition-colors duration-200 flex-shrink-0" title="Edit task">
                                  Edit
                                </button>
                                <button onClick={() => handleDeleteTask(task.id)} className="text-red-600 hover:text-red-800 p-1 rounded-md hover:bg-red-50 transition-colors duration-200 flex-shrink-0" title="Delete task">
                                  Delete
                                </button>
                              </div>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          </main>
        </div>
      )}
    </>
  );
}
