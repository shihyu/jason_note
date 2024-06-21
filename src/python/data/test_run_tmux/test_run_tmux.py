import subprocess

def run_in_tmux(session_name, script_path):
    try:
        # Start a new tmux session with the specified name
        subprocess.run(['tmux', 'new-session', '-d', '-s', session_name], check=True)
        
        # Send the command to run the python script within the tmux session
        subprocess.run(['tmux', 'send-keys', '-t', session_name, f'python {script_path}', 'C-m'], check=True)
        
        print(f"Started {script_path} in tmux session '{session_name}'")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    session_name = "mysession"
    script_path = "hello.py"
    
    run_in_tmux(session_name, script_path)

