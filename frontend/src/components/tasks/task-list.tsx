'use client';

import { useState } from 'react';
import { Task } from '@/types/task';

interface TaskListProps {
  tasks: Task[];
  onToggleCompletion: (taskId: string) => Promise<void>;
  onDeleteTask: (taskId: string) => Promise<void>;
  onEditTask?: (task: Task) => void;
}

const PRIORITY_COLORS: Record<string, string> = {
  low: 'bg-gray-100 text-gray-700',
  medium: 'bg-blue-100 text-blue-700',
  high: 'bg-orange-100 text-orange-700',
  urgent: 'bg-red-100 text-red-700',
};

export default function TaskList({ tasks, onToggleCompletion, onDeleteTask, onEditTask }: TaskListProps) {
  const [expandedTaskId, setExpandedTaskId] = useState<string | null>(null);

  if (!tasks || tasks.length === 0) {
    return (
      <div className="text-center py-10">
        <p className="text-gray-600">No tasks yet. Add your first task!</p>
      </div>
    );
  }

  return (
    <ul className="bg-white shadow overflow-hidden rounded-md">
      {tasks.map((task) => (
        <li
          key={task.id}
          className={`px-6 py-4 border-b border-gray-200 ${
            task.completed ? 'bg-green-50' :
            (task.due_date && new Date(task.due_date) < new Date() ? 'bg-white border-l-4 border-l-red-500' : 'bg-white')
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center flex-1 min-w-0">
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => onToggleCompletion(task.id)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded flex-shrink-0"
              />
              <span
                className={`ml-3 text-lg cursor-pointer truncate ${
                  task.completed ? 'line-through text-gray-500' : 'text-gray-900'
                }`}
                onClick={() => setExpandedTaskId(expandedTaskId === task.id ? null : task.id)}
              >
                {task.title}
              </span>
              {task.priority && task.priority !== 'medium' && (
                <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium flex-shrink-0 ${PRIORITY_COLORS[task.priority] || ''}`}>
                  {task.priority}
                </span>
              )}
              {task.recurrence_rule && (
                <span className="ml-1 text-gray-400 flex-shrink-0" title={`Repeats ${task.recurrence_rule}`}>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2 flex-shrink-0 ml-2">
              <button
                onClick={() => onEditTask && onEditTask(task)}
                className="text-blue-600 hover:text-blue-900 text-sm"
              >
                Edit
              </button>
              <button
                onClick={() => onDeleteTask(task.id)}
                className="text-red-600 hover:text-red-900 text-sm"
              >
                Delete
              </button>
            </div>
          </div>

          {/* Tags row */}
          {task.tags && task.tags.length > 0 && (
            <div className="mt-1 ml-7 flex flex-wrap gap-1">
              {task.tags.map(tag => (
                <span key={tag} className="inline-block px-2 py-0.5 rounded-full text-xs bg-indigo-50 text-indigo-600">
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Expanded details */}
          <div className={`mt-2 text-sm ${expandedTaskId === task.id ? 'block' : 'hidden'}`}>
            {task.description && (
              <p className="text-gray-600 mb-1 ml-7">{task.description}</p>
            )}
            <div className="ml-7 text-xs text-gray-500 space-y-0.5">
              {task.due_date && (
                <p>Due: {new Date(task.due_date).toLocaleString()}</p>
              )}
              {task.created_at && (
                <p>
                  Created: {new Date(task.created_at).toLocaleString()}
                  {task.completed_at && (
                    <span>, Completed: {new Date(task.completed_at).toLocaleString()}</span>
                  )}
                </p>
              )}
              {task.recurrence_rule && (
                <p>Repeats: {task.recurrence_rule}</p>
              )}
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
