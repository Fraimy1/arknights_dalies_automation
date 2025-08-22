import time
import random
from typing import Callable, Iterable, Optional
from logger import logger
from config import Settings


class Wait:
    """Flexible waiter with backoff and stability frames.

    - until(predicate): retries until predicate returns True for N consecutive frames
    - until_any(*predicates): succeeds if any becomes stably True
    - until_all(*predicates): succeeds when all are stably True
    """

    def __init__(self,
                 timeout: Optional[float] = None,
                 min_interval: Optional[float] = None,
                 max_interval: Optional[float] = None,
                 require_stable_frames: Optional[int] = None,
                 abort_check: Optional[Callable[[], bool]] = None,
                 name: str = ""):
        t = Settings.timeouts
        self.timeout = timeout if timeout is not None else t.default_timeout
        self.min_interval = min_interval if min_interval is not None else t.check_interval_min
        self.max_interval = max_interval if max_interval is not None else t.check_interval_max
        self.require_stable_frames = require_stable_frames if require_stable_frames is not None else t.stability_frames
        self.abort_check = abort_check
        self.name = name

    def _sleep(self):
        dt = random.uniform(self.min_interval, self.max_interval)
        time.sleep(dt)

    def _should_abort(self) -> bool:
        try:
            return bool(self.abort_check and self.abort_check())
        except Exception:
            return False

    def until(self, predicate: Callable[[], bool]) -> bool:
        start = time.monotonic()
        stable = 0
        last_exception: Optional[Exception] = None

        while (time.monotonic() - start) < self.timeout:
            if self._should_abort():
                logger.warning(f"Wait '{self.name}' aborted by panic/safety signal")
                return False
            try:
                ok = bool(predicate())
                if ok:
                    stable += 1
                    if stable >= self.require_stable_frames:
                        return True
                else:
                    stable = 0
            except Exception as ex:
                last_exception = ex
                stable = 0

            self._sleep()

        if last_exception:
            logger.warning(f"Wait '{self.name}' timed out with last exception: {last_exception}")
        else:
            logger.warning(f"Wait '{self.name}' timed out after {self.timeout:.2f}s")
        return False

    def until_any(self, predicates: Iterable[Callable[[], bool]]) -> bool:
        start = time.monotonic()
        preds = list(predicates)
        stables = [0] * len(preds)

        while (time.monotonic() - start) < self.timeout:
            if self._should_abort():
                logger.warning(f"Wait-any '{self.name}' aborted by panic/safety signal")
                return False

            any_true = False
            for i, p in enumerate(preds):
                try:
                    ok = bool(p())
                    if ok:
                        stables[i] += 1
                        if stables[i] >= self.require_stable_frames:
                            return True
                        any_true = True
                    else:
                        stables[i] = 0
                except Exception:
                    stables[i] = 0

            if any_true:
                # If something flickered true, still require stability, but we can sleep shorter
                pass

            self._sleep()

        logger.warning(f"Wait-any '{self.name}' timed out after {self.timeout:.2f}s")
        return False

    def until_all(self, predicates: Iterable[Callable[[], bool]]) -> bool:
        start = time.monotonic()
        preds = list(predicates)
        stables = [0] * len(preds)

        while (time.monotonic() - start) < self.timeout:
            if self._should_abort():
                logger.warning(f"Wait-all '{self.name}' aborted by panic/safety signal")
                return False

            all_true = True
            for i, p in enumerate(preds):
                try:
                    ok = bool(p())
                    if ok:
                        stables[i] += 1
                    else:
                        stables[i] = 0
                        all_true = False
                except Exception:
                    stables[i] = 0
                    all_true = False

            if all_true and all(s >= self.require_stable_frames for s in stables):
                return True

            self._sleep()

        logger.warning(f"Wait-all '{self.name}' timed out after {self.timeout:.2f}s")
        return False


