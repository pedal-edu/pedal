from __future__ import annotations
from pedal.command_line.modes import AbstractPipeline, Bundle
from pedal.core.config_job import JobConfig

class SimplePipeline(AbstractPipeline):
    def process_output(self):
        return self

def run_job(**config) -> list[Bundle]:
    """
    Runs a Pedal job with the given configuration.
    """
    pipeline = SimplePipeline(JobConfig(mode="simple", **config))
    pipeline.execute()
    return pipeline.submissions
