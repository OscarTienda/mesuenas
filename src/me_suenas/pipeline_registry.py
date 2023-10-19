"""Project pipelines."""
from __future__ import annotations

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

from me_suenas.pipelines import me_suenas



def register_pipelines() -> dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """

    me_suenas_pipeline = me_suenas.me_suenas_pipeline()

    return {
        "__default__": me_suenas_pipeline
    }