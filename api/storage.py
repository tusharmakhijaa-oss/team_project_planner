import json
import os
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"


class JSONStorage:
    """Manage persistent application data using JSON files.

    This class provides a simple persistence abstraction for the
    application APIs. It stores collections of records as JSON lists
    inside the project's ``db`` directory.

    Writes use a temporary file followed by an atomic replacement
    to reduce the risk of leaving partially written JSON files.

    Attributes:
        file_path: Absolute path to the JSON storage file.
    """

    def __init__(self, filename):
        """Initialize a JSON storage handler.

        Creates the storage directory if necessary. If the requested
        file does not exist, it initializes the file with an empty
        JSON list.

        Args:
            filename: Name of the JSON file used for persistence.

        Raises:
            OSError: If the storage directory or initial file cannot
                be created.
            ValueError: If the filename is invalid.
        """
        if not filename or Path(filename).name != filename:
            raise ValueError(
                "A filename without directory paths is required."
            )
        
        self.file_path = DB_DIR / filename
        DB_DIR.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            self._write([])

    def _read(self):
        """Read and deserialize the stored JSON records.

        Returns:
            A list of records loaded from the JSON file. Returns an
            empty list if the file is missing or contains invalid JSON.

        Raises:
            OSError: If the file cannot be accessed for reasons other
                than it being missing.
        """

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write(self, data):
        """Write records to the storage file atomically.

        Data is first serialized to a temporary file in the storage
        directory. The temporary file then replaces the destination
        file, reducing the risk of partial writes.

        Args:
            data: List of records to serialize as JSON.

        Raises:
            OSError: If the temporary file cannot be created, written,
                or moved into place.
            TypeError: If the supplied data cannot be serialized to
                JSON.
            ValueError: If JSON serialization encounters an invalid
                value.
        """

        DB_DIR.mkdir(parents=True, exist_ok=True)

        fd, temp_path = tempfile.mkstemp(
            dir=DB_DIR,
            prefix=".tmp_",
            suffix=".json",
        )

        try:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            os.replace(temp_path, self.file_path)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def all(self):
        """Return all records stored in the JSON file.

        Returns:
            A list containing the stored records. Returns an empty
            list if the file is missing or contains invalid JSON.
        """
        return self._read()

    def save_all(self, data):
        """Persist a complete collection of records.

        Args:
            data: List of records to save to the JSON file.

        Raises:
            TypeError: If the data cannot be serialized to JSON.
            ValueError: If JSON serialization encounters an invalid
                value.
            OSError: If the data cannot be written to disk.
        """
        self._write(data)