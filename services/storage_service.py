import json
import os
import tempfile
from pathlib import Path

from models.user import User


class StorageService:
    """Save and restore users, projects, and tasks using JSON."""

    def __init__(self, file_path=None):
        """Use the project's data folder unless another path is supplied."""
        default_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "project_data.json"
        )
        self.file_path = (
            Path(file_path) if file_path is not None else default_path
        )

    def load(self):
        """Load saved users, returning an empty list for a missing file."""
        try:
            with self.file_path.open(encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(
                f"Could not read project data: {error}"
            ) from error

        try:
            if not isinstance(data, dict):
                raise ValueError("Saved data must be a JSON object.")

            user_data = data["users"]

            if not isinstance(user_data, list):
                raise ValueError("Saved users must be a list.")

            return [User.from_dict(item) for item in user_data]

        except (KeyError, TypeError, ValueError, AttributeError) as error:
            raise RuntimeError(
                f"Invalid project data: {error}"
            ) from error

    def save(self, users):
        """Replace the saved file only after new data is fully written."""
        temporary_path = None

        try:
            data = {
                "users": [user.to_dict() for user in users]
            }

            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                json.dump(data, file, indent=2)
                file.write("\n")

            os.replace(temporary_path, self.file_path)

        except (OSError, TypeError, ValueError) as error:
            raise RuntimeError(
                f"Could not save project data: {error}"
            ) from error

        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)