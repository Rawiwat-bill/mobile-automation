import time
from robot.api import logger


class BenchmarkMetrics:
    """Collects and reports benchmark timing and event metrics.

    Import as Library in Robot Framework resource files.
    All public methods are available as keywords.
    State is per-library-instance (one instance per import scope).
    """

    def __init__(self):
        self.reset("default")

    def reset(self, benchmark_name):
        self.name = benchmark_name
        self.start_time = None
        self.end_time = None
        self.phases = []
        self.current_phase = None
        self.current_phase_start = None
        self.wait_time = 0.0
        self.scroll_time = 0.0
        self.appium_actions = 0
        self.adb_calls = 0
        self.screenshots = 0
        self.retries = 0
        self.strategy_name = ""
        self.field_name = ""
        self.result = "PASS"

    def start_benchmark(self, benchmark_name):
        self.reset(benchmark_name)
        self.start_time = time.time()

    def end_benchmark(self):
        self.end_time = time.time()
        self.log_results()

    def set_strategy(self, field, strategy):
        self.field_name = field
        self.strategy_name = strategy

    def set_result(self, result):
        self.result = result

    def start_phase(self, phase_name):
        if self.current_phase is not None:
            self.end_phase()
        self.current_phase = phase_name
        self.current_phase_start = time.time()

    def end_phase(self):
        if self.current_phase is None:
            return
        elapsed = time.time() - self.current_phase_start
        self.phases.append({"name": self.current_phase, "elapsed": round(elapsed, 3)})
        self.current_phase = None
        self.current_phase_start = None

    def record_wait(self, duration):
        duration = float(duration)
        self.wait_time += duration
        self.phases.append({"name": "wait", "elapsed": round(duration, 3)})

    def record_scroll(self, duration):
        duration = float(duration)
        self.scroll_time += duration
        self.phases.append({"name": "scroll", "elapsed": round(duration, 3)})

    def record_appium_action(self):
        self.appium_actions += 1

    def record_adb_call(self):
        self.adb_calls += 1

    def record_screenshot(self):
        self.screenshots += 1

    def record_retry(self):
        self.retries += 1

    def log_results(self):
        total = self._total_execution()
        logger.info("=" * 60)
        logger.info(f"BENCHMARK RESULT: {self.name}")
        logger.info(f"  Field:           {self.field_name}")
        logger.info(f"  Strategy:        {self.strategy_name}")
        logger.info(f"  Result:          {self.result}")
        logger.info(f"  Total Time:      {total}s")
        logger.info(f"  Wait Time:       {round(self.wait_time, 3)}s")
        logger.info(f"  Scroll Time:     {round(self.scroll_time, 3)}s")
        logger.info(f"  Appium Actions:  {self.appium_actions}")
        logger.info(f"  ADB Calls:       {self.adb_calls}")
        logger.info(f"  Screenshots:     {self.screenshots}")
        logger.info(f"  Retries:         {self.retries}")
        if self.phases:
            logger.info("  Phases:")
            for p in self.phases:
                logger.info(f"    {p['name']}: {p['elapsed']}s")
        logger.info("=" * 60)

        summary = (
            f"BENCHMARK|{self.name}|{self.field_name}|{self.strategy_name}|{self.result}|"
            f"{total}|{round(self.wait_time, 3)}|{round(self.scroll_time, 3)}|"
            f"{self.appium_actions}|{self.adb_calls}|{self.screenshots}|{self.retries}"
        )
        logger.info(summary)

    def _total_execution(self):
        if self.start_time and self.end_time:
            return round(self.end_time - self.start_time, 3)
        return 0.0
