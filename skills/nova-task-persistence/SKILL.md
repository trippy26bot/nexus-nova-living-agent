# Nova Task Persistence Engine v1.0.0

Tasks NEVER stop. Background = still running. Only user YES closes a task.

States: FOREGROUND | BACKGROUND | PENDING | ENDING | COMPLETE

```python
from nova_task_persistence import TaskPersistenceEngine
tpe = TaskPersistenceEngine()
tpe.start_task("research", "Deep dive")
tpe.list_active()
tpe.session_summary()
```
