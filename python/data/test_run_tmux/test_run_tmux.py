import subprocess


def check_and_kill_tmux_session(session_name):
    # Check if the tmux session exists
    result = subprocess.run(["tmux", "ls"], capture_output=True, text=True)
    if session_name in result.stdout:
        print(f"Session '{session_name}' exists. Killing it.")
        subprocess.run(["tmux", "kill-session", "-t", session_name], check=True)
    else:
        print(f"No existing session named '{session_name}' found.")


def run_in_tmux(session_name, script_path):
    try:
        # Check and kill the session if it exists
        check_and_kill_tmux_session(session_name)

        # Start a new tmux session with the specified name
        subprocess.run(["tmux", "new-session", "-d", "-s", session_name], check=True)

        # Send the command to run the python script within the tmux session
        subprocess.run(
            ["tmux", "send-keys", "-t", session_name, f"python {script_path}", "C-m"],
            check=True,
        )

        print(f"Started {script_path} in tmux session '{session_name}'")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    session_name = "mysession"
    script_path = "hello.py"

    run_in_tmux(session_name, script_path)
