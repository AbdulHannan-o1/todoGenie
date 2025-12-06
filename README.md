# CLI Task Management

This is a simple Command Line Interface (CLI) application for managing tasks. It allows users to add, list, update, complete, and delete tasks. The application stores tasks in-memory.

## Quickstart

### 1. Prerequisites

- Python 3.10+
- `pip` for installing dependencies

### 2. Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Initialize a virtual environment and install dependencies**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install rich
    ```

### 3. Running the Application

To run the application, execute the `app.py` script with the desired command:

```bash
python app.py <command> [arguments]
```

### Available Commands:

-   **`add <description>`**: Add a new task.
    Example: `python app.py add "Buy groceries"`
-   **`list`**: List all tasks.
    Example: `python app.py list`
-   **`update <id> <new-description>`**: Update a task's description.
    Example: `python app.py update 1 "Buy milk and eggs"`
-   **`complete <id>`**: Mark a task as complete.
    Example: `python app.py complete 1`
-   **`delete <id>`**: Delete a task.
    Example: `python app.py delete 1`
-   **`help`**: Show the help message.
    Example: `python app.py help`
