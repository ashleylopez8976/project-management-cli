from datetime import date

from models.task import Task


class Project:
    """Represent a user's project and its tasks."""

    _next_id = 1

    def __init__(self, title, description="", due_date=None):
        """Initialize a project with a unique ID and an empty task list."""
        self.title = title
        self.description = description
        self.due_date = due_date
        self.id = Project._next_id
        Project._next_id += 1
        self.tasks = []

    @property
    def title(self):
        """Return the project title."""
        return self._title

    @title.setter
    def title(self, value):
        """Require a nonempty project title."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Project title cannot be empty.")
        self._title = value.strip()

    @property
    def due_date(self):
        """Return the optional due date."""
        return self._due_date

    @due_date.setter
    def due_date(self, value):
        """Validate an optional date in YYYY-MM-DD format."""
        if value is None or value == "":
            self._due_date = None
            return

        if not isinstance(value, str):
            raise ValueError("Due date must use YYYY-MM-DD format.")

        try:
            parsed = date.fromisoformat(value)
        except ValueError as error:
            raise ValueError(
                "Due date must be a valid date in YYYY-MM-DD format."
            ) from error

        if parsed.isoformat() != value:
            raise ValueError("Due date must use YYYY-MM-DD format.")

        self._due_date = value

    def add_task(self, task):
        """Add a Task object to this project."""
        if not isinstance(task, Task):
            raise ValueError("A project can only contain Task objects.")

        if any(existing.title == task.title for existing in self.tasks):
            raise ValueError("A task with that title already exists.")

        self.tasks.append(task)

    def get_task_by_title(self, title):
        """Find a task by title, returning None when absent."""
        return next(
            (task for task in self.tasks if task.title == title),
            None,
        )

    def to_dict(self):
        """Convert the project and its tasks into JSON-compatible data."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data):
        """Restore a saved project, its tasks, and the ID counter."""
        project = cls(
            data["title"],
            data.get("description", ""),
            data.get("due_date"),
        )
        project.id = data["id"]
        project.tasks = [
            Task.from_dict(task_data)
            for task_data in data.get("tasks", [])
        ]
        cls._next_id = max(cls._next_id, project.id + 1)
        return project

    def __str__(self):
        """Return a readable project description for CLI output."""
        due = self.due_date or "Not set"
        return (
            f"{self.id}: {self.title} | Due: {due} | "
            f"Tasks: {len(self.tasks)}"
        )