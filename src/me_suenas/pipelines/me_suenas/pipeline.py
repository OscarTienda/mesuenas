from kedro.pipeline import node, Pipeline
from .nodes import *

def me_suenas_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=process_df,
                inputs="data_x_raw",
                outputs="df_x",
                name="process_data_x"
            ),
            node(
                func=process_df,
                inputs="data_y_raw",
                outputs="df_y",
                name="process_data_y"
            ),
            node(
                func=set_accuracy_level,
                inputs="params:accuracy_level",
                outputs="accuracy_info",
                name="set_accuracy_level"
            ),
            node(
                func=prepare_timestamps,
                inputs=["df_x", "df_y", "params:first_meeting_date"],
                outputs=["df_x_timestamps", "df_y_timestamps"],
                name="prepare_timestamps"
            ),
        ]
    )