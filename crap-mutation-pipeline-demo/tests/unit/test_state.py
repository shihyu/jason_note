from pipeline.state import TaskState


def test_save_and_load_roundtrip(tmp_path):
    state = TaskState(task_id="t1", language="python", requirement="do X")
    state.spec = "- [ ] test 1"
    state.history.append({"stage": "specification", "output": "..."})

    state.save(state_dir=tmp_path)
    loaded = TaskState.load("t1", state_dir=tmp_path)

    assert loaded.task_id == "t1"
    assert loaded.language == "python"
    assert loaded.spec == "- [ ] test 1"
    assert loaded.history == [{"stage": "specification", "output": "..."}]
