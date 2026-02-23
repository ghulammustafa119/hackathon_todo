'use client';

import { useState, useEffect } from 'react';
import apiService from '@/lib/api';

interface AuditEvent {
  event_id: string;
  event_type: string;
  timestamp: string;
  changes?: Record<string, { from: any; to: any }>;
}

interface TaskAuditLogProps {
  taskId: string;
  onClose: () => void;
}

const EVENT_LABELS: Record<string, { label: string; color: string }> = {
  'task.created': { label: 'Created', color: 'bg-green-100 text-green-700' },
  'task.updated': { label: 'Updated', color: 'bg-blue-100 text-blue-700' },
  'task.completed': { label: 'Completed', color: 'bg-purple-100 text-purple-700' },
  'task.uncompleted': { label: 'Reopened', color: 'bg-yellow-100 text-yellow-700' },
  'task.deleted': { label: 'Deleted', color: 'bg-red-100 text-red-700' },
};

export default function TaskAuditLog({ taskId, onClose }: TaskAuditLogProps) {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await apiService.getTaskEvents(taskId);
        setEvents(data);
      } catch {
        // silently fail
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, [taskId]);

  const formatChange = (key: string, change: { from: any; to: any }) => {
    const label = key.replace('_', ' ');
    const from = change.from ?? '(empty)';
    const to = change.to ?? '(empty)';
    return (
      <div key={key} className="text-xs text-gray-600 ml-4">
        <span className="font-medium capitalize">{label}:</span>{' '}
        <span className="line-through text-red-500">{String(from)}</span>{' '}
        <span className="text-green-600">{String(to)}</span>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[70vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold text-gray-800">Task History</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-xl leading-none">&times;</button>
        </div>

        <div className="overflow-y-auto flex-1 p-4">
          {loading ? (
            <p className="text-center text-gray-500 py-4">Loading...</p>
          ) : events.length === 0 ? (
            <p className="text-center text-gray-500 py-4">No history found</p>
          ) : (
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-3 top-2 bottom-2 w-0.5 bg-gray-200"></div>

              <div className="space-y-4">
                {events.map((event) => {
                  const info = EVENT_LABELS[event.event_type] || { label: event.event_type, color: 'bg-gray-100 text-gray-700' };
                  return (
                    <div key={event.event_id} className="relative pl-8">
                      {/* Timeline dot */}
                      <div className="absolute left-1.5 top-1.5 w-3 h-3 rounded-full bg-indigo-500 border-2 border-white"></div>

                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${info.color}`}>
                            {info.label}
                          </span>
                          <span className="text-xs text-gray-400">
                            {new Date(event.timestamp).toLocaleString()}
                          </span>
                        </div>

                        {/* Show changes for updates */}
                        {event.changes && Object.keys(event.changes).length > 0 && (
                          <div className="mt-1 space-y-0.5">
                            {Object.entries(event.changes).map(([key, change]) =>
                              formatChange(key, change)
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
