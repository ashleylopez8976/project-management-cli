# Project Management CLI

A Python command-line application for managing users, projects, and tasks.
Data is saved locally in JSON. A reusable Ollama client generates project
summaries from existing project and task data.

## Features

- Create and list users.
- Create, list, and edit projects.
- Add, list, edit, and complete tasks.
- Assign multiple contributors to a task.
- Save and restore data between commands.
- Generate AI project summaries.
- Display readable input, storage, and service errors.

## Requirements

- Python 3.11
- Dependencies listed in requirements.txt
- Ollama and the llama3.2 model for AI summaries

The standard project management commands work without the Ollama service
running. The Python dependencies must still be installed.

## Setup

Clone the repository and enter its folder:

```bash
git clone https://github.com/ashleylopez8976/project-management-cli.git
cd project-management-cli
```

Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Alternatively, with uv installed:

```bash
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Run the CLI

Display the available commands:

```bash
python main.py --help
```

Display help for a specific command:

```bash
python main.py add-task --help
```

Each invocation runs one command. Changes are saved automatically.

## Example Workflow

Run these commands on a new tracker:

```bash
python main.py add-user --name "Alex" --email "alex@example.com"
python main.py add-user --name "Maya" --email "maya@example.com"

python main.py add-project --user "Alex" --title "CLI Tool" --description "Build project tracker" --due-date "2026-12-01"

python main.py add-task --project "CLI Tool" --title "Implement add-task" --assigned-to "Alex"

python main.py assign-task --project "CLI Tool" --task "Implement add-task" --user "Maya"

python main.py list-users
python main.py list-projects --user "Alex"
python main.py list-tasks --project "CLI Tool"

python main.py edit-project --project "CLI Tool" --description "Build and test the project tracker"

python main.py edit-task --project "CLI Tool" --task "Implement add-task" --status pending

python main.py complete-task --project "CLI Tool" --task "Implement add-task"
```

Project and task titles can also be changed using the corresponding
edit command's --title argument.

## AI Summary Setup

Install the Ollama application from https://ollama.com.

For Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

If the installer reports that zstd is missing:

```bash
sudo apt update
sudo apt install zstd
```

Download the model:

```bash
ollama pull llama3.2
```

If the Ollama service is not already running, start it in a separate terminal:

```bash
ollama serve
```

Generate a summary:

```bash
python main.py summarize-project --project "CLI Tool"
```

The project summary service builds a prompt containing structured project
data and explicit task counts. The reusable AI client handles model calls,
response extraction, conversation history, and service failures.

AI output is a suggestion and should be reviewed for accuracy before use.

## File Structure

| Path | Responsibility |
| --- | --- |
| main.py | Argument parsing and command coordination |
| models/user.py | Person and User classes, validation, and owned projects |
| models/project.py | Project details and task relationships |
| models/task.py | Task status and contributor IDs |
| services/storage_service.py | JSON loading and saving |
| services/ai_client.py | Reusable Ollama communication |
| services/project_summary_service.py | Project-specific summary prompts |
| utils/formatters.py | Readable terminal output |
| data/project_data.json | Runtime data, created on the first save |
| requirements.txt | External Python dependency |

## Object-Oriented Design

User inherits name validation from Person. Each user owns projects, and
each project contains tasks. Tasks can reference multiple users through
contributor IDs, and users can contribute to multiple tasks.

Properties validate names, email addresses, titles, due dates, and task
statuses. Class attributes track IDs. Class methods restore objects from
saved dictionaries, while instance methods manage object behavior.
The __str__ methods provide readable object descriptions.

## Persistence and Error Handling

Data is stored in data/project_data.json, relative to the application folder.

A missing data file starts an empty tracker. Unreadable or malformed data
produces an error rather than being silently overwritten. Saves use a
temporary file before replacing the existing data file.

Invalid input, missing users or tasks, duplicate names, and service
connection failures produce readable messages.

## Manual Verification

The following workflows were checked:

- Displaying command help.
- Creating users, projects, and tasks.
- Loading saved data in later command invocations.
- Completing a task and changing it back to pending.
- Editing a project description.
- Assigning two contributors to one task.
- Rejecting duplicate users and invalid email addresses.
- Reporting a missing user.
- Handling an unavailable Ollama service.
- Generating a summary with the local llama3.2 model.

## Known Limitations

- This is a local prototype without authentication or access controls.
- User names and project titles must be unique.
- Task title lookup is case-sensitive.
- Concurrent writes from multiple processes are not supported.
- Email validation checks basic structure, not address ownership.
- AI responses can contain mistakes despite prompt instructions.
- AI summaries require the Ollama application, a downloaded model,
  and sufficient local computing resources.
- Conversation history exists only within the current client instance.