from kedro.pipeline import node, Pipeline
from .nodes import *


def me_suenas_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=expand_locations_column,
                inputs="data_x_raw",
                outputs="df_x",
                name="process_data_x",
            ),
            node(
                func=expand_locations_column,
                inputs="data_y_raw",
                outputs="df_y",
                name="process_data_y",
            ),
            node(
                func=set_accuracy_level,
                inputs="params:accuracy_level",
                outputs="accuracy_info",
                name="set_accuracy_level",
            ),
            node(
                func=prepare_timestamp,
                inputs=[
                    "df_x",
                    "df_y",
                    "params:first_meeting_date",
                    "params:x_name",
                    "params:y_name",
                ],
                outputs=["df_x_timestamp", "df_y_timestamp"],
                name="prepare_timestamp",
            ),
            node(
                func=normalize_timestamp,
                inputs=["df_x_timestamp", "df_y_timestamp", "params:time_margin"],
                outputs=["df_x_timestamps_norm", "df_y_timestamps_norm"],
                name="normalize_timestamps",
            ),
            node(
                func=preprocess_map_data_for_person,
                inputs=["df_x_timestamps_norm", "accuracy_info"],
                outputs="df_x_common_timestamps",
                name="preprocess_map_data_x",
            ),
            node(
                func=preprocess_map_data_for_person,
                inputs=["df_y_timestamps_norm", "accuracy_info"],
                outputs="df_y_common_timestamps",
                name="preprocess_map_data_y",
            ),
            node(
                func=combine_records,
                inputs=[
                    "df_x_common_timestamps",
                    "df_y_common_timestamps",
                    "params:x_name",
                    "params:y_name",
                ],
                outputs="df_combined",
                name="combine_records",
            ),
            node(
                func=find_encounters,
                inputs=["df_combined"],
                outputs="df_encounters",
                name="find_encounters",
            ),
        ]
    )
