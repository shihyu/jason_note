from Jlab.utils import get_execution_time, update_github
import time


@get_execution_time
def my_function():
    print("Start sleeping for 5 seconds...")
    time.sleep(5)
    print("Finished sleeping for 5 seconds.")

def test_update_github():
    token = "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"
    repo_name = "stockinfo"
    filename = "test.c"
    update_github(token, repo_name, filename)

if __name__ == "__main__":
    # my_function()
    test_update_github()
