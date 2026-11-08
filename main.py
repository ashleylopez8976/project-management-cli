import argparse

from models.project import Project
from models.task import Task
from models.user import User
from services.ai_client import OllamaChatClient
from services.project_summary_service import ProjectSummaryService
from services.storage_service import StorageService
from utils.formatters import format_projects, format_tasks, format_users


def find_user(users, name):
    """Find a user by name or raise a readable error."""
    for user in users:
        if user.name.casefold() == name.strip().casefold():
            return user
    raise ValueError(f"User '{name}' not found.")


def find_project(users, title):
    """Find a uniquely named project and its owner."""
    matches = [
        (user, project)
        for user in users
        for project in user.projects
        if project.title.casefold() == title.strip().casefold()
    ]

    if not matches:
        raise ValueError(f"Project '{title}' not found.")
    if len(matches) > 1:
        raise ValueError("Project title is ambiguous. Use unique titles.")

    return matches[0]


def find_task(project, title):
    """Find a task within a project."""
    task = project.get_task_by_title(title)
    if task is None:
        raise ValueError(f"Task '{title}' not found.")
    return task


def ensure_unique_project_title(users, title, current=None):
    """Require project titles to be unique across the tracker."""
    for user in users:
        for project in user.projects:
            if (
                project is not current
                and project.title.casefold() == title.strip().casefold()
            ):
                raise ValueError("A project with that title already exists.")


def build_parser():
    """Define supported CLI commands and their arguments."""
    parser = argparse.ArgumentParser(
        description="Manage users, projects, and tasks.",
        epilog="Example: python main.py list-users",
    )
    commands = parser.add_subparsers(dest="command")

    add_user = commands.add_parser("add-user", help="Create a user")
    add_user.add_argument("--name", required=True)
    add_user.add_argument("--email", required=True)

    commands.add_parser("list-users", help="List all users")

    add_project = commands.add_parser("add-project", help="Create a project")
    add_project.add_argument("--user", required=True)
    add_project.add_argument("--title", required=True)
    add_project.add_argument("--description", default="")
    add_project.add_argument("--due-date")

    list_projects = commands.add_parser(
        "list-projects", help="List a user's projects"
    )
    list_projects.add_argument("--user", required=True)

    edit_project = commands.add_parser(
        "edit-project", help="Update project details"
    )
    edit_project.add_argument("--project", required=True)
    edit_project.add_argument("--title")
    edit_project.add_argument("--description")
    edit_project.add_argument("--due-date")

    add_task = commands.add_parser("add-task", help="Create a task")
    add_task.add_argument("--project", required=True)
    add_task.add_argument("--title", required=True)
    add_task.add_argument(
        "--assigned-to", nargs="+", default=[], help="Contributor names"
    )

    list_tasks = commands.add_parser("list-tasks", help="List project tasks")
    list_tasks.add_argument("--project", required=True)

    complete_task = commands.add_parser(
        "complete-task", help="Mark a task completed"
    )
    complete_task.add_argument("--project", required=True)
    complete_task.add_argument("--task", required=True)

    edit_task = commands.add_parser("edit-task", help="Update task details")
    edit_task.add_argument("--project", required=True)
    edit_task.add_argument("--task", required=True)
    edit_task.add_argument("--title")
    edit_task.add_argument("--status", choices=["pending", "completed"])

    assign_task = commands.add_parser(
        "assign-task", help="Add a contributor to a task"
    )
    assign_task.add_argument("--project", required=True)
    assign_task.add_argument("--task", required=True)
    assign_task.add_argument("--user", required=True)

    summary = commands.add_parser(
        "summarize-project", help="Generate an AI project summary"
    )
    summary.add_argument("--project", required=True)

    return parser


def execute_command(args, users):
    """Run a command and return its output and whether data changed."""
    if args.command == "add-user":
        name = args.name.strip()
        if any(user.name.casefold() == name.casefold() for user in users):
            raise ValueError("A user with that name already exists.")
        if any(
            user.email.casefold() == args.email.strip().casefold()
            for user in users
        ):
            raise ValueError("A user with that email already exists.")

        user = User(name, args.email)
        users.append(user)
        return f"User '{user.name}' added.", True

    if args.command == "list-users":
        return format_users(users), False

    if args.command == "add-project":
        user = find_user(users, args.user)
        ensure_unique_project_title(users, args.title)
        project = Project(args.title, args.description, args.due_date)
        user.add_project(project)
        return f"Project '{project.title}' added to {user.name}.", True

    if args.command == "list-projects":
        user = find_user(users, args.user)
        return format_projects(user.projects), False

    owner, project = find_project(users, args.project)

    if args.command == "edit-project":
        if all(
            value is None
            for value in (args.title, args.description, args.due_date)
        ):
            raise ValueError("Provide a title, description, or due date.")

        if args.title is not None:
            ensure_unique_project_title(users, args.title, current=project)
            project.title = args.title
        if args.description is not None:
            project.description = args.description
        if args.due_date is not None:
            project.due_date = args.due_date

        return f"Project '{project.title}' updated.", True

    if args.command == "add-task":
        contributor_ids = [
            find_user(users, name).id for name in args.assigned_to
        ]
        task = Task(args.title)
        for user_id in contributor_ids:
            task.add_contributor(user_id)
        project.add_task(task)
        return f"Task '{task.title}' added.", True

    if args.command == "list-tasks":
        return format_tasks(project.tasks, users), False

    if args.command == "summarize-project":
        client = OllamaChatClient()
        service = ProjectSummaryService(client)
        return service.summarize(project, owner), False

    task = find_task(project, args.task)

    if args.command == "complete-task":
        task.complete()
        return f"Task '{task.title}' completed.", True

    if args.command == "assign-task":
        user = find_user(users, args.user)
        task.add_contributor(user.id)
        return f"{user.name} assigned to '{task.title}'.", True

    if args.command == "edit-task":
        if args.title is None and args.status is None:
            raise ValueError("Provide a new title or status.")

        if args.title is not None:
            new_title = args.title.strip()
            if any(
                other is not task and other.title == new_title
                for other in project.tasks
            ):
                raise ValueError("A task with that title already exists.")
            task.title = new_title
        if args.status is not None:
            task.status = args.status

        return f"Task '{task.title}' updated.", True

    raise ValueError("Unknown command.")


def main():
    """Load data, execute one CLI command, and save changes."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    storage = StorageService()

    try:
        users = storage.load()
        output, changed = execute_command(args, users)

        if changed:
            storage.save(users)

        print(output)
        return 0

    except ValueError as error:
        print(f"Input Error: {error}")
        return 1
    except RuntimeError as error:
        print(f"Service or Storage Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())