"""Tests for Phase I Todo Console App - Task Operations"""

from todo_console.services.storage import TaskStorage
from todo_console.services.operations import TaskOperations


def test_create_task():
    storage = TaskStorage()
    ops = TaskOperations(storage)
    result = ops.create_task("Test Task", "Test Description")
    assert result["success"] is True
    assert result["task_id"] == 1


def test_list_tasks():
    storage = TaskStorage()
    ops = TaskOperations(storage)
    ops.create_task("Task 1", "Desc 1")
    ops.create_task("Task 2", "Desc 2")
    result = ops.list_tasks()
    assert len(result["tasks"]) == 2


def test_update_task():
    storage = TaskStorage()
    ops = TaskOperations(storage)
    ops.create_task("Old Title", "Old Desc")
    result = ops.update_task(1, title="New Title")
    assert result["success"] is True


def test_delete_task():
    storage = TaskStorage()
    ops = TaskOperations(storage)
    ops.create_task("To Delete", "")
    result = ops.delete_task(1)
    assert result["success"] is True
    assert ops.list_tasks()["tasks"] == []


def test_toggle_completion():
    storage = TaskStorage()
    ops = TaskOperations(storage)
    ops.create_task("Toggle Me", "")
    result = ops.toggle_completion(1)
    assert result["success"] is True
    assert result["new_status"] is True
