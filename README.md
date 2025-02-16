# streaming-utilities

A collection of terminal-based utilities for streamers featuring a Spotify
now-playing display and a simple task management system.

## Features

### Now Playing Display

- Real-time display of currently playing Spotify tracks
- Scrolling for long track names and artist information
- Progress bar showing the current position in the track
- Clean, minimal terminal interface

### Task Management

- Simple terminal-based task management system
- Create and edit tasks with subtasks
- Mark tasks as complete/incomplete
- Quick keyboard shortcuts for task manipulation
- Persistent storage of tasks in a `.task` file

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/streaming-utilities.git
cd streaming-utilities
```

2. Install the required dependencies:

```bash
pip install rich prompt_toolkit python-dotenv requests
```

3. Set up Spotify API credentials:
    - Go to https://developer.spotify.com/dashboard and log in with your Spotify
      account
    - Click "Create App"
    - Fill in the app details:
        - App name: Choose any name (e.g., "Streaming Utilities")
        - App description: Brief description of your usage
        - Redirect URI: `http://localhost:8989` (!important)
        - Website: Optional
    - After creating the app, you'll see your Client ID and Client Secret on the
      page of the app
    - Create a `.env` file in the project root with the following content:
   ```
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=http://localhost:8989
   ```

## Usage

The utilities can be accessed through the `stream.py` script with different
command-line arguments:

### Now Playing Display

```bash
python stream.py --now-playing
```

This will show the currently playing Spotify track with a progress bar.
When you start the view you may be prompted to login with your Spotify account.

### Task Management

```bash
python stream.py --current-task
```

This will open the task management interface. Use the following keyboard
shortcuts:

- `c`: Change main task
- Numbers (1-9): Select a task
- `x`: Toggle selected subtask completion
- `d`: Delete selected subtask
- `a`: Add new subtask
- `Ctrl+C`: Exit
