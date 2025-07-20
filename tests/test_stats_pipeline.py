

from pedal.command_line.modes import StatsPipeline, MODES
from pedal.core.config_job import JobConfig


def test_stats_pipeline():
    """
    Test the StatsPipeline class to ensure it initializes correctly and can run.
    """
    pipeline = StatsPipeline(JobConfig(
        mode=MODES.STATS,
        submissions = "def main():\n    return 'Hello, World!'",
        instructor = "from pedal import *\nensure_function('main')",
        instructor_direct = True,
        submission_direct = True,
    ))
    assert pipeline is not None, "StatsPipeline should be initialized"

    # Run the pipeline and check if it completes without errors
    try:
        pipeline.execute()
    except Exception as e:
        assert False, f"StatsPipeline run failed with exception: {e}"

    # Check if the report is generated
    pipeline.result