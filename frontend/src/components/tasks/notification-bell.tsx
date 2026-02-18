'use client';

import { useState, useEffect, useCallback } from 'react';
import apiService from '@/lib/api';

interface Notification {
  id: string;
  task_id: string;
  remind_at: string;
  status: string;
}

export default function NotificationBell() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  const fetchNotifications = useCallback(async () => {
    try {
      const data = await apiService.makeRequest<Notification[]>(
        `/${apiService['getUserId']()}/notifications`
      );
      setNotifications(data.filter(n => n.status === 'sent'));
    } catch {
      // Silently fail - notifications are non-critical
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const markAsRead = async (id: string) => {
    try {
      await apiService.makeRequest(
        `/${apiService['getUserId']()}/notifications/${id}/read`,
        { method: 'PATCH' }
      );
      setNotifications(prev => prev.filter(n => n.id !== id));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors"
        title="Notifications"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {notifications.length > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {notifications.length}
          </span>
        )}
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          <div className="p-3 border-b border-gray-100">
            <h3 className="text-sm font-semibold text-gray-700">Notifications</h3>
          </div>
          <div className="max-h-64 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-sm text-gray-500">No new notifications</div>
            ) : (
              notifications.map(n => (
                <div key={n.id} className="p-3 border-b border-gray-50 hover:bg-gray-50 flex justify-between items-center">
                  <div>
                    <p className="text-sm text-gray-700">Task reminder</p>
                    <p className="text-xs text-gray-500">{new Date(n.remind_at).toLocaleString()}</p>
                  </div>
                  <button
                    onClick={() => markAsRead(n.id)}
                    className="text-xs text-blue-600 hover:text-blue-800"
                  >
                    Dismiss
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
