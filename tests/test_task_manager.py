"""
Unit tests for Task Manager (After Review version)
"""

import unittest
import os
import tempfile
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'after-review'))

from task_manager import (
    TaskManager, 
    TaskStatus, 
    ValidationError, 
    DatabaseError
)


class TestTaskManager(unittest.TestCase):
    """Test cases for TaskManager class."""
    
    def setUp(self):
        """Set up test database before each test."""
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.manager = TaskManager(self.db_path)
    
    def tearDown(self):
        """Clean up test database after each test."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_add_task_success(self):
        """Test successful task creation."""
        task_id = self.manager.add_task(
            "Test Task",
            "Test Description",
            TaskStatus.PENDING.value
        )
        self.assertIsInstance(task_id, int)
        self.assertGreater(task_id, 0)
    
    def test_add_task_empty_title(self):
        """Test that empty title raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.manager.add_task("", "Description")
    
    def test_add_task_whitespace_title(self):
        """Test that whitespace-only title raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.manager.add_task("   ", "Description")
    
    def test_add_task_invalid_status(self):
        """Test that invalid status raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.manager.add_task("Title", "Desc", "invalid_status")
    
    def test_add_task_title_too_long(self):
        """Test that too long title raises ValidationError."""
        long_title = "x" * 201
        with self.assertRaises(ValidationError):
            self.manager.add_task(long_title, "Description")
    
    def test_get_all_tasks(self):
        """Test retrieving all tasks."""
        # Add some tasks
        self.manager.add_task("Task 1", "Desc 1")
        self.manager.add_task("Task 2", "Desc 2")
        
        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertIsInstance(tasks, list)
        self.assertIsInstance(tasks[0], dict)
    
    def test_get_task_by_id_exists(self):
        """Test retrieving existing task by ID."""
        task_id = self.manager.add_task("Test", "Desc")
        task = self.manager.get_task_by_id(task_id)
        
        self.assertIsNotNone(task)
        self.assertEqual(task['title'], "Test")
        self.assertEqual(task['description'], "Desc")
    
    def test_get_task_by_id_not_exists(self):
        """Test retrieving non-existent task returns None."""
        task = self.manager.get_task_by_id(9999)
        self.assertIsNone(task)
    
    def test_update_task_success(self):
        """Test successful task update."""
        task_id = self.manager.add_task("Original", "Desc")
        result = self.manager.update_task(
            task_id,
            title="Updated",
            status=TaskStatus.COMPLETED.value
        )
        
        self.assertTrue(result)
        
        updated_task = self.manager.get_task_by_id(task_id)
        self.assertEqual(updated_task['title'], "Updated")
        self.assertEqual(updated_task['status'], TaskStatus.COMPLETED.value)
    
    def test_update_task_not_exists(self):
        """Test updating non-existent task returns False."""
        result = self.manager.update_task(9999, title="Updated")
        self.assertFalse(result)
    
    def test_delete_task_success(self):
        """Test successful task deletion."""
        task_id = self.manager.add_task("To Delete", "Desc")
        result = self.manager.delete_task(task_id)
        
        self.assertTrue(result)
        
        # Verify task is deleted
        task = self.manager.get_task_by_id(task_id)
        self.assertIsNone(task)
    
    def test_delete_task_not_exists(self):
        """Test deleting non-existent task returns False."""
        result = self.manager.delete_task(9999)
        self.assertFalse(result)
    
    def test_search_tasks(self):
        """Test task search functionality."""
        self.manager.add_task("Python Tutorial", "Learn Python")
        self.manager.add_task("Java Tutorial", "Learn Java")
        self.manager.add_task("Python Advanced", "Advanced Python")
        
        results = self.manager.search_tasks("Python")
        self.assertEqual(len(results), 2)
        
        for task in results:
            self.assertIn("Python", task['title'])
    
    def test_filter_by_status(self):
        """Test filtering tasks by status."""
        self.manager.add_task("Task 1", "Desc", TaskStatus.PENDING.value)
        self.manager.add_task("Task 2", "Desc", TaskStatus.COMPLETED.value)
        self.manager.add_task("Task 3", "Desc", TaskStatus.PENDING.value)
        
        pending_tasks = self.manager.filter_by_status(TaskStatus.PENDING.value)
        self.assertEqual(len(pending_tasks), 2)
        
        for task in pending_tasks:
            self.assertEqual(task['status'], TaskStatus.PENDING.value)
    
    def test_filter_by_invalid_status(self):
        """Test filtering by invalid status raises ValidationError."""
        with self.assertRaises(ValidationError):
            self.manager.filter_by_status("invalid_status")
    
    def test_get_priority_tasks(self):
        """Test retrieving priority tasks."""
        self.manager.add_task("Normal", "Desc", TaskStatus.PENDING.value)
        self.manager.add_task("Important", "Desc", TaskStatus.HIGH.value)
        self.manager.add_task("Critical", "Desc", TaskStatus.URGENT.value)
        
        priority_tasks = self.manager.get_priority_tasks()
        self.assertEqual(len(priority_tasks), 2)
        
        statuses = [task['status'] for task in priority_tasks]
        self.assertIn(TaskStatus.HIGH.value, statuses)
        self.assertIn(TaskStatus.URGENT.value, statuses)
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are handled safely."""
        # This should not cause SQL injection
        malicious_title = "Test'; DROP TABLE tasks; --"
        
        task_id = self.manager.add_task(malicious_title, "Desc")
        task = self.manager.get_task_by_id(task_id)
        
        # Task should be created with the malicious string as literal text
        self.assertEqual(task['title'], malicious_title)
        
        # Database should still exist and be queryable
        all_tasks = self.manager.get_all_tasks()
        self.assertIsInstance(all_tasks, list)


class TestTaskStatus(unittest.TestCase):
    """Test cases for TaskStatus enum."""
    
    def test_task_status_values(self):
        """Test that TaskStatus enum has correct values."""
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        self.assertEqual(TaskStatus.HIGH.value, "high")
        self.assertEqual(TaskStatus.URGENT.value, "urgent")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
