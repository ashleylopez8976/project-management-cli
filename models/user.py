from models.project import Project


class Person:
    """Represent a person with a validated name."""

    def __init__(self, name):
        """Initialize the person's name."""
        self.name = name

    @property
    def name(self):
        """Return the person's name."""
        return self._name

    @name.setter
    def name(self, value):
        """Require a nonempty name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()


class User(Person):
    """Represent a user who owns projects and contributes to tasks."""

    _next_id = 1

    def __init__(self, name, email):
        """Initialize a user with a unique ID and no projects."""
        super().__init__(name)
        self.email = email
        self.id = User._next_id
        User._next_id += 1
        self.projects = []

    @property
    def email(self):
        """Return the user's email address."""
        return self._email

    @email.setter
    def email(self, value):
        """Check the basic structure of an email address."""
        if not isinstance(value, str):
            raise ValueError("Enter a valid email address.")

        value = value.strip()
        local, separator, domain = value.partition("@")

        if (
            not separator
            or not local
            or "." not in domain
            or domain.startswith(".")
            or domain.endswith(".")
            or "@" in domain
            or any(character.isspace() for character in value)
        ):
            raise ValueError("Enter a valid email address.")

        self._email = value

    def add_project(self, project):
        """Add a Project object to the user's projects."""
        if not isinstance(project, Project):
            raise ValueError("A user can only own Project objects.")

        if any(
            existing.title == project.title
            for existing in self.projects
        ):
            raise ValueError("A project with that title already exists.")

        self.projects.append(project)

    def get_project_by_title(self, title):
        """Find an owned project by title, or return None."""
        return next(
            (
                project
                for project in self.projects
                if project.title == title
            ),
            None,
        )

    def to_dict(self):
        """Convert the user and owned projects into saved data."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "projects": [
                project.to_dict() for project in self.projects
            ],
        }

    @classmethod
    def from_dict(cls, data):
        """Restore a saved user, owned projects, and the ID counter."""
        user = cls(data["name"], data["email"])
        user.id = data["id"]
        user.projects = [
            Project.from_dict(project_data)
            for project_data in data.get("projects", [])
        ]
        cls._next_id = max(cls._next_id, user.id + 1)
        return user

    def __str__(self):
        """Return a readable user description for CLI output."""
        return (
            f"{self.id}: {self.name} <{self.email}> | "
            f"Projects: {len(self.projects)}"
        )