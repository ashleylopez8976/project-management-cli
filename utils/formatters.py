def format_users(users):
    """Display users, or a message when no users exist."""
    if not users:
        return "No users found."

    return "Users:\n" + "\n".join(str(user) for user in users)


def format_projects(projects):
    """Display projects, including their descriptions."""
    if not projects:
        return "No projects found."

    lines = ["Projects:"]

    for project in projects:
        lines.append(str(project))
        lines.append(
            f"  Description: {project.description or 'Not provided'}"
        )

    return "\n".join(lines)


def format_tasks(tasks, users):
    """Display tasks with contributor names resolved from user IDs."""
    if not tasks:
        return "No tasks found."

    user_names = {user.id: user.name for user in users}
    lines = ["Tasks:"]

    for task in tasks:
        contributors = ", ".join(
            user_names.get(user_id, f"Unknown user #{user_id}")
            for user_id in task.assigned_to
        )

        lines.append(
            f"{task} | Contributors: {contributors or 'Unassigned'}"
        )

    return "\n".join(lines)