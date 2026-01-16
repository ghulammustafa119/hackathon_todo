#!/usr/bin/env python3
"""
Test script to verify the tasks CRUD endpoints are working properly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing Todo API endpoints...")

    # Test registration
    print("\n1. Testing user registration...")
    register_data = {
        "email": "test@example.com",
        "password": "TestPass123",
        "name": "Test User"
    }
    register_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"Registration status: {register_response.status_code}")
    if register_response.status_code == 200:
        print(f"Registration response: {register_response.json()}")
    elif register_response.status_code == 409:
        print("User already exists, continuing with login...")
    else:
        print(f"Registration failed: {register_response.text}")
        return

    # Test login
    print("\n2. Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "TestPass123"
    }
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data['access_token']
        print(f"Login successful, got token: {access_token[:20]}...")
    else:
        print(f"Login failed: {login_response.text}")
        return

    # Prepare headers with the token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Test getting user info
    print("\n3. Testing getting user info...")
    user_response = requests.get(f"{BASE_URL}/api/auth/user", headers=headers)
    print(f"Get user status: {user_response.status_code}")
    if user_response.status_code == 200:
        user_data = user_response.json()
        print(f"User data: {user_data}")
    else:
        print(f"Get user failed: {user_response.text}")

    # Test getting tasks (should be empty initially)
    print("\n4. Testing getting tasks...")
    tasks_get_response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
    print(f"Get tasks status: {tasks_get_response.status_code}")
    if tasks_get_response.status_code == 200:
        tasks_data = tasks_get_response.json()
        print(f"Tasks: {tasks_data}")
    else:
        print(f"Get tasks failed: {tasks_get_response.text}")

    # Test creating a task
    print("\n5. Testing creating a task...")
    task_data = {
        "title": "Test Task",
        "description": "This is a test task"
    }
    task_create_response = requests.post(f"{BASE_URL}/api/tasks", json=task_data, headers=headers)
    print(f"Create task status: {task_create_response.status_code}")
    if task_create_response.status_code == 200:
        created_task = task_create_response.json()
        print(f"Created task: {created_task}")
        task_id = created_task['id']
    else:
        print(f"Create task failed: {task_create_response.text}")
        return

    # Test getting the specific task
    print("\n6. Testing getting specific task...")
    task_get_response = requests.get(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
    print(f"Get specific task status: {task_get_response.status_code}")
    if task_get_response.status_code == 200:
        specific_task = task_get_response.json()
        print(f"Specific task: {specific_task}")
    else:
        print(f"Get specific task failed: {task_get_response.text}")

    # Test updating the task
    print("\n7. Testing updating the task...")
    update_data = {
        "title": "Updated Test Task",
        "description": "This is an updated test task",
        "completed": True
    }
    task_update_response = requests.put(f"{BASE_URL}/api/tasks/{task_id}", json=update_data, headers=headers)
    print(f"Update task status: {task_update_response.status_code}")
    if task_update_response.status_code == 200:
        updated_task = task_update_response.json()
        print(f"Updated task: {updated_task}")
    else:
        print(f"Update task failed: {task_update_response.text}")

    # Test toggling completion status
    print("\n8. Testing toggling completion status...")
    toggle_response = requests.patch(f"{BASE_URL}/api/tasks/{task_id}/complete", headers=headers)
    print(f"Toggle completion status: {toggle_response.status_code}")
    if toggle_response.status_code == 200:
        toggle_result = toggle_response.json()
        print(f"Toggle result: {toggle_result}")
    else:
        print(f"Toggle completion failed: {toggle_response.text}")

    # Test getting all tasks again (should include our task)
    print("\n9. Testing getting tasks again...")
    tasks_get_response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
    print(f"Get tasks status: {tasks_get_response.status_code}")
    if tasks_get_response.status_code == 200:
        tasks_data = tasks_get_response.json()
        print(f"All tasks: {len(tasks_data)} total")
        for task in tasks_data:
            print(f"  - {task['id']}: {task['title']} (completed: {task['completed']})")
    else:
        print(f"Get tasks failed: {tasks_get_response.text}")

    # Test deleting the task
    print("\n10. Testing deleting the task...")
    task_delete_response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
    print(f"Delete task status: {task_delete_response.status_code}")
    if task_delete_response.status_code == 200:
        delete_result = task_delete_response.json()
        print(f"Delete result: {delete_result}")
    else:
        print(f"Delete task failed: {task_delete_response.text}")

    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_api()