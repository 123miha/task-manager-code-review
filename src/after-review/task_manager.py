"""
Task Manager Module - Improved Version After Code Review

This module provides functionality for managing tasks with proper
error handling, validation, and security measures.
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from contextlib import contextmanager
from enum import Enum


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Enumeration for task statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    HIGH = "high"
    URGENT = "urgent"


class TaskManagerError(Exception):
    """Base exception for TaskManager errors."""
    pass


class ValidationError(TaskManagerError):
    """Raised when input validation fails."""
    pass


class DatabaseError(TaskManagerError):
    """Raised when database operation fails."""
    pass


class TaskManager:
    """
    Task Manager class for handling task operations.
    
    This class provides CRUD operations for tasks with proper
    error handling and SQL injection protection.
    """
    
    def __init__(self, db_path: str = "tasks.db"):
        """
        Initialize TaskManager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_database()
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
            
        Raises:
            DatabaseError: If connection fails
        """
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            yield connection
            connection.commit()
        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
        finally:
            if connection:
                connection.close()
    
    def _initialize_database(self) -> None:
        """Create tasks table if it doesn't exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT
                    )
                ''')
                logger.info("Database initialized successfully")
        except DatabaseError as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _validate_task_data(
        self, 
        title: str, 
        status: str, 
        description: Optional[str] = None
    ) -> None:
        """
        Validate task input data.
        
        Args:
            title: Task title
            status: Task status
            description: Task description (optional)
            
        Raises:
            ValidationError: If validation fails
        """
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty")
        
        if len(title) > 200:
            raise ValidationError("Title too long (max 200 characters)")
        
        if description and len(description) > 1000:
            raise ValidationError("Description too long (max 1000 characters)")
        
        valid_statuses = [status.value for status in TaskStatus]
        if status not in valid_statuses:
            raise ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
    
    def add_task(
        self, 
        title: str, 
        description: str = "", 
        status: str = TaskStatus.PENDING.value
    ) -> int:
        """
        Add a new task to the database.
        
        Args:
            title: Task title
            description: Task description
            status: Task status (default: pending)
            
        Returns:
            ID of the created task
            
        Raises:
            ValidationError: If input validation fails
            DatabaseError: If database operation fails
        """
        self._validate_task_data(title, status, description)
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO tasks (title, description, status, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (title.strip(), description.strip(), status, datetime.now().isoformat())
                )
                task_id = cursor.lastrowid
                logger.info(f"Task created successfully with ID: {task_id}")
                return task_id
        except DatabaseError as e:
            logger.error(f"Failed to add task: {e}")
            raise
    
    def get_all_tasks(self) -> List[dict]:
        """
        Retrieve all tasks from the database.
        
        Returns:
            List of tasks as dictionaries
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
                tasks = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Retrieved {len(tasks)} tasks")
                return tasks
        except DatabaseError as e:
            logger.error(f"Failed to retrieve tasks: {e}")
            raise
    
    def get_task_by_id(self, task_id: int) -> Optional[dict]:
        """
        Retrieve a specific task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task as dictionary or None if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                
                if row:
                    task = dict(row)
                    logger.info(f"Task {task_id} retrieved successfully")
                    return task
                else:
                    logger.warning(f"Task {task_id} not found")
                    return None
        except DatabaseError as e:
            logger.error(f"Failed to retrieve task {task_id}: {e}")
            raise
    
    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
    ) -> bool:
        """
        Update an existing task.
        
        Args:
            task_id: Task ID
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            
        Returns:
            True if task was updated, False if not found
            
        Raises:
            ValidationError: If input validation fails
            DatabaseError: If database operation fails
        """
        # Get existing task
        existing_task = self.get_task_by_id(task_id)
        if not existing_task:
            return False
        
        # Use existing values if new ones not provided
        new_title = title if title is not None else existing_task['title']
        new_description = description if description is not None else existing_task['description']
        new_status = status if status is not None else existing_task['status']
        
        # Validate
        self._validate_task_data(new_title, new_status, new_description)
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE tasks 
                    SET title = ?, description = ?, status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (new_title.strip(), new_description.strip(), new_status, 
                     datetime.now().isoformat(), task_id)
                )
                logger.info(f"Task {task_id} updated successfully")
                return True
        except DatabaseError as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task from the database.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if task was deleted, False if not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                
                if cursor.rowcount > 0:
                    logger.info(f"Task {task_id} deleted successfully")
                    return True
                else:
                    logger.warning(f"Task {task_id} not found for deletion")
                    return False
        except DatabaseError as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise
    
    def search_tasks(self, search_term: str) -> List[dict]:
        """
        Search tasks by title.
        
        Args:
            search_term: Search term
            
        Returns:
            List of matching tasks
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM tasks WHERE title LIKE ? ORDER BY created_at DESC",
                    (f"%{search_term}%",)
                )
                tasks = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Search found {len(tasks)} tasks for term: {search_term}")
                return tasks
        except DatabaseError as e:
            logger.error(f"Failed to search tasks: {e}")
            raise
    
    def filter_by_status(self, status: str) -> List[dict]:
        """
        Filter tasks by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of tasks with specified status
            
        Raises:
            ValidationError: If status is invalid
            DatabaseError: If database operation fails
        """
        valid_statuses = [s.value for s in TaskStatus]
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status: {status}")
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC",
                    (status,)
                )
                tasks = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Found {len(tasks)} tasks with status: {status}")
                return tasks
        except DatabaseError as e:
            logger.error(f"Failed to filter tasks by status: {e}")
            raise
    
    def get_priority_tasks(self) -> List[dict]:
        """
        Get high priority and urgent tasks.
        
        Returns:
            List of priority tasks
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM tasks 
                    WHERE status IN (?, ?)
                    ORDER BY created_at DESC
                    """,
                    (TaskStatus.HIGH.value, TaskStatus.URGENT.value)
                )
                tasks = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Found {len(tasks)} priority tasks")
                return tasks
        except DatabaseError as e:
            logger.error(f"Failed to retrieve priority tasks: {e}")
            raise


def main():
    """Example usage of TaskManager."""
    try:
        manager = TaskManager()
        
        # Add tasks
        task_id = manager.add_task(
            "Complete project documentation",
            "Write comprehensive docs for the project",
            TaskStatus.PENDING.value
        )
        print(f"Created task with ID: {task_id}")
        
        # Get all tasks
        all_tasks = manager.get_all_tasks()
        print(f"\nAll tasks: {len(all_tasks)}")
        for task in all_tasks:
            print(f"  - {task['title']} ({task['status']})")
        
    except TaskManagerError as e:
        logger.error(f"Application error: {e}")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
