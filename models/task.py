class Task:
    """Represent a project task and its assigned contributors."""

    _next_id = 1

    def __init__(self, title, assigned_to=None):
        """Initialize a task with a unique ID and pending status."""
        self.title = title
        self.id = Task._next_id
        Task._next_id += 1
        self.status = "pending"
        self.assigned_to = list(assigned_to) if assigned_to else []

    @property
    def title(self):
        """Return the task title."""
        return self._title

    @title.setter
    def title(self, value):
        """Require a nonempty task title."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Task title cannot be empty.")
        self._title = value.strip()

    @property
    def status(self):
        """Return the current task status."""
        return self._status

    @status.setter
    def status(self, value):
        """Allow only supported task statuses."""
        if value not in ("pending", "completed"):
            raise ValueError("Status must be pending or completed.")
        self._status = value

    def complete(self):
        """Mark this task as completed."""
        self.status = "completed"

    def add_contributor(self, user_id):
        """Assign a user by ID without adding duplicates."""
        if user_id not in self.assigned_to:
            self.assigned_to.append(user_id)

    def to_dict(self):
        """Convert this task into JSON-compatible data."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "assigned_to": list(self.assigned_to),
        }

    @classmethod
    def from_dict(cls, data):
        """Restore a saved task and advance the ID counter."""
        task = cls(data["title"], data.get("assigned_to", []))
        task.id = data["id"]
        task.status = data.get("status", "pending")
        cls._next_id = max(cls._next_id, task.id + 1)
        return task

    def __str__(self):
        """Return a readable task description for CLI output."""
        return f"{self.id}: {self.title} [{self.status}]"