'use client';

import { useState } from 'react';

interface TaskFiltersProps {
  onFilterChange: (filters: FilterState) => void;
}

export interface FilterState {
  priority?: string;
  status?: string;
  tag?: string;
  search?: string;
  sort_by?: string;
  sort_order?: string;
}

const PRIORITIES = ['all', 'low', 'medium', 'high', 'urgent'];
const STATUSES = ['all', 'pending', 'completed'];

export default function TaskFilters({ onFilterChange }: TaskFiltersProps) {
  const [filters, setFilters] = useState<FilterState>({});
  const [searchInput, setSearchInput] = useState('');

  const updateFilter = (key: keyof FilterState, value: string) => {
    const newFilters = { ...filters };
    if (value === 'all' || value === '') {
      delete newFilters[key];
    } else {
      newFilters[key] = value;
    }
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleSearch = () => {
    updateFilter('search', searchInput);
  };

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="mb-4 p-4 bg-gray-50 rounded-lg border">
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Search</label>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            onBlur={handleSearch}
            placeholder="Search tasks..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Priority</label>
          <select
            value={filters.priority || 'all'}
            onChange={(e) => updateFilter('priority', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {PRIORITIES.map(p => (
              <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Status</label>
          <select
            value={filters.status || 'all'}
            onChange={(e) => updateFilter('status', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            {STATUSES.map(s => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Sort</label>
          <select
            value={filters.sort_by || 'created_at'}
            onChange={(e) => updateFilter('sort_by', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="created_at">Date Created</option>
            <option value="priority">Priority</option>
            <option value="due_date">Due Date</option>
            <option value="title">Title</option>
          </select>
        </div>
      </div>
    </div>
  );
}
