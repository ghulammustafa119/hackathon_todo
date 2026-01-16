'use client';

import { useState } from 'react';

export default function TaskCompleteToggle({ task, onToggleCompletion }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleToggle = async () => {
    setLoading(true);
    setError('');

    try {
      await onToggleCompletion(task.id);
    } catch (err) {
      setError(err.message || 'Failed to update task completion status');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={handleToggle}
        disabled={loading}
        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded disabled:opacity-50"
      />
      <span className={`ml-2 ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
        {loading ? 'Updating...' : task.completed ? 'Completed' : 'Mark Complete'}
      </span>
      {error && (
        <span className="ml-2 text-sm text-red-600">{error}</span>
      )}
    </div>
  );
}