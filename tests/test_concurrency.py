from __future__ import annotations

from app.services.concurrency import JobTracker


def test_job_tracker_acquire_release() -> None:
    tracker = JobTracker(max_concurrent=2, max_per_ip=2)

    assert tracker.try_acquire("10.0.0.1")
    assert tracker.try_acquire("10.0.0.1")
    assert not tracker.try_acquire("10.0.0.1"), "Acima do limite por IP"
    assert tracker.active_count() == 2

    tracker.release("10.0.0.1")
    assert tracker.try_acquire("10.0.0.1")
    assert tracker.active_count() == 2


def test_job_tracker_global_limit() -> None:
    tracker = JobTracker(max_concurrent=1, max_per_ip=2)

    assert tracker.try_acquire("10.0.0.1")
    assert not tracker.try_acquire("10.0.0.2"), "Limite global de 1 job ativo"

    tracker.release("10.0.0.1")
    assert tracker.try_acquire("10.0.0.2")


def test_job_tracker_release_removes_ip() -> None:
    tracker = JobTracker(max_concurrent=3, max_per_ip=1)

    assert tracker.try_acquire("10.0.0.1")
    assert not tracker.try_acquire("10.0.0.1")
    tracker.release("10.0.0.1")
    tracker.release("10.0.0.1")  # release duplo não pode corromper o estado

    assert tracker.try_acquire("10.0.0.1")
    assert tracker.active_count() == 1
