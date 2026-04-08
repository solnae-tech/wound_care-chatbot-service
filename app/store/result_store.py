from typing import Any, Dict, Optional

from app.queue.result_queue import drain_results


_RESULT_CACHE: Dict[str, Dict[str, Any]] = {}


def _sync_from_queue() -> None:
    """Pull completed results from RabbitMQ into local cache."""
    queued_results = drain_results()
    if queued_results:
        _RESULT_CACHE.update(queued_results)


def get_result(job_id: str) -> Optional[Dict[str, Any]]:
    """Return result by job_id after syncing cache from result queue."""
    _sync_from_queue()
    return _RESULT_CACHE.get(job_id)