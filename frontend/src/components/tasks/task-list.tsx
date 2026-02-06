'use client';

import { useState } from 'react';
import { Task } from '@/types/task';

interface TaskListProps {
  tasks: Task[];
  onToggleCompletion: (taskId: string) => Promise<void>;
  onDeleteTask: (taskId: string) => Promise<void>;
  onEditTask?: (task: Task) => void;
}

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
          className={`px-6 py-4 border-b border-gray-200 ${task.completed ? 'bg-green-50' : 'bg-white'}`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => onToggleCompletion(task.id)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <span
                className={`ml-3 text-lg cursor-pointer ${
                  task.completed ? 'line-through text-gray-500' : 'text-gray-900'
                }`}
                onClick={() => setExpandedTaskId(expandedTaskId === task.id ? null : task.id)}
              >
                {task.title}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onEditTask && onEditTask(task)}
                className="text-blue-600 hover:text-blue-900 text-sm flex-shrink-0"
              >
                Edit
              </button>
              <button
                onClick={() => onDeleteTask(task.id)}
                className="text-red-600 hover:text-red-900 text-sm flex-shrink-0"
              >
                Delete
              </button>
            </div>
          </div>

          {(task.description || task.created_at) && (
            <div
              className={`mt-2 text-sm ${
                expandedTaskId === task.id ? 'block' : 'hidden'
              }`}
            >
              {task.description && (
                <p className="text-gray-600 mb-1">{task.description}</p>
              )}
              {task.created_at && (
                <p className="text-xs text-gray-500">
                  Created: {new Date(task.created_at).toLocaleString()}
                  {task.completed_at && (
                    <span>, Completed: {new Date(task.completed_at).toLocaleString()}</span>
                  )}
                </p>
              )}
            </div>
          )}
        </li>
      ))}
    </ul>
  );
}