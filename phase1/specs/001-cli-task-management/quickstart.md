# Quickstart: CLI Task Management

**Version**: 1.0
**Status**: Completed
**Author**: Gemini
**Last Updated**: 2025-12-06

## 1. Prerequisites

- Python 3.10+
- `pip` for installing dependencies

## 2. Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies**:
    ```bash
    pip install rich
    ```

## 3. Running the Application

To run the application, execute the `app.py` script with the desired command:

```bash
python app.py <command> [arguments]
```

### Available Commands:

-   **`add <description>`**: Add a new task.
-   **`list`**: List all tasks.
-   **`update <id> <new-description>`**: Update a task's description.
-   **`complete <id>`**: Mark a task as complete.
-   **`delete <id>`**: Delete a task.
-   **`help`**: Show the help message.
