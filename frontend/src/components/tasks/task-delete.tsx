'use client';

import { useState } from 'react';

interface TaskDeleteConfirmationProps {
  taskId: string;
  taskTitle: string;
  onConfirmDelete: (taskId: string) => Promise<void>;
  onCancel: () => void;
}

export default function TaskDeleteConfirmation({ taskId, taskTitle, onConfirmDelete, onCancel }: TaskDeleteConfirmationProps) {
  const [loading, setLoading] = useState<boolean>(false);

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirmDelete(taskId);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-4 p-4 border border-red-300 rounded-md bg-red-50">
      <h3 className="text-lg font-medium text-red-800 mb-2">Confirm Deletion</h3>
      <p className="text-red-700 mb-4">
        Are you sure you want to delete the task "{taskTitle}"? This action cannot be undone.
      </p>
      <div className="flex space-x-3">
        <button
          onClick={handleConfirm}
          disabled={loading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
        >
          {loading ? 'Deleting...' : 'Delete Task'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}