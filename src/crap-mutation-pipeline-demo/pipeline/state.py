import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

STATE_DIR = Path(".pipeline_state")


@dataclass
class TaskState:
    task_id: str
    language: str
    requirement: str
    stage: str = "spec"
    spec: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)

    def save(self, state_dir: Path = STATE_DIR) -> None:
        state_dir.mkdir(parents=True, exist_ok=True)
        path = state_dir / f"{self.task_id}.json"
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False))

    @classmethod
    def load(cls, task_id: str, state_dir: Path = STATE_DIR) -> "TaskState":
        path = state_dir / f"{task_id}.json"
        data = json.loads(path.read_text())
        return cls(**data)
