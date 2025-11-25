import json
import time
import uuid
import requests
import os

from collections import defaultdict
from pathlib import Path

from eval_types import (
    EvaluationLog, 
    EvaluatorRelationship,
    EvaluationResult,
    EvaluationSource,
    EvaluationSourceType,
    MetricConfig,
    ModelInfo,
    ScoreDetails,
    ScoreType,
    SourceMetadata
)

def download_leaderboard(url):
    response = requests.get(url)
    response.raise_for_status()

    return response.json()

def save_to_file(unified_eval_log: EvaluationLog, output_filepath: str) -> bool:
    try:
        json_str = unified_eval_log.model_dump_json(indent=2, exclude_none=True)

        with open(output_filepath, 'w') as json_file:
            json_file.write(json_str)

        print(f'Unified eval log was successfully saved to {output_filepath} file.')
    except Exception as e:
        print(f"Problem with saving unified eval log to file: {e}")
        raise e
    
def get_generation_config_from_run_specs(run_specs: str):
    generation_config = defaultdict(list)

    for run_spec in run_specs:
        task, args_str = tuple(run_spec.split(':', 1))
        args = args_str.split(',')
        
        for arg in args:
            key, value = tuple(arg.split('='))
            if key == 'model':
                continue
                
            generation_config[key].append(value)
    
    for key, values in generation_config.items():
        if len(set(values)) == 1:
            generation_config[key] = values[0]
    
    return generation_config

def prepare_model_info_map(row):
    model_name = row[0].get('value')
    run_spec_names = next(
        (r["run_spec_names"] for r in row if "run_spec_names" in r),
        None
    )
    spec = run_spec_names[0]
    args = spec.split(':', 1)[1].split(',')

    model_details = next(
        (arg.split('=', 1)[1] for arg in args if arg.startswith('model=')),
        ''
    )
    
    developer = model_details.split('_')[0]
    model_id = model_details.replace('_', '/')

    model_info = ModelInfo(
        name=model_name,
        id=model_id,
        developer=developer,
        inference_platform='unknown'
    )
    
    return model_info

def convert(leaderboard_name, leaderboard_data, evaluation_source, source_data):
    acc_stats = leaderboard_data[0]
    
    rows = acc_stats.get('rows')
    headers = acc_stats.get('header')
    eval_names = [header.get('value') for header in headers[1:]]

    metrics = [
        MetricConfig(
            evaluation_description=header.get('description') or None,
            lower_is_better=header.get('lower_is_better') or False,
            min_score=0,
            max_score=1,
            score_type=ScoreType.continuous
        )
        for header in headers[1:]
    ]

    evaluation_logs = {}

    for row in rows[:10]:
        model_info = prepare_model_info_map(row)
        retrieved_timestamp = str(time.time())
        evaluation_id=f'{leaderboard_name}/{model_info.id.replace('/', '_')}/{retrieved_timestamp}'

        evaluation_results = []
        for idx, res in enumerate(row[1:]):
            if not res.get('value'):
                continue

            generation_config = get_generation_config_from_run_specs(res.get('run_spec_names')) if res.get('run_spec_names') else {}

            evaluation_results.append(
                EvaluationResult(
                    evaluation_name=eval_names[idx - 1],
                    metric_config=metrics[idx - 1],
                    score_details=ScoreDetails(
                        score=round(res.get('value'), 3),
                        details={
                            'description': res.get('description')
                        }
                    ),
                    generation_config=generation_config
                )
            )

        eval_log = EvaluationLog(
            schema_version='0.0.1',
            evaluation_id=evaluation_id,
            retrieved_timestamp=retrieved_timestamp,
            source_metadata=SourceMetadata(
                source_organization_name='crfm',
                evaluator_relationship=EvaluatorRelationship.third_party
            ),
            model_info=model_info,
            source_data=source_data,
            evaluation_source=evaluation_source,
            evaluation_results=evaluation_results
        )
        
        evaluation_logs[evaluation_id] = eval_log

        log_filename = f'{uuid.uuid4()}.json'
        model_dev, model_name = tuple(model_info.id.split('/'))
        dirpath = f'data/{leaderboard_name}/{model_dev}/{model_name}'

        os.makedirs(dirpath, exist_ok=True)

        save_to_file(eval_log, f'{dirpath}/{log_filename}')


if __name__ == '__main__':
    leaderboard_name = 'HELM_Capabilities' # 'HELM_Lite'
    leaderboard_name = leaderboard_name.lower()
    source_data = [
        'https://storage.googleapis.com/crfm-helm-public/capabilities/benchmark_output/releases/v1.12.0/groups/core_scenarios.json'
        # 'https://storage.googleapis.com/crfm-helm-public/lite/benchmark_output/releases/v1.13.0/groups/core_scenarios.json'
    ]

    os.makedirs(f'data/{leaderboard_name}', exist_ok=True)

    leaderboard_data = download_leaderboard(source_data[0])

    evaluation_source = EvaluationSource(
        evaluation_source_name=leaderboard_name,
        evaluation_source_type=EvaluationSourceType.leaderboard
    )

    convert(leaderboard_name, leaderboard_data, evaluation_source, source_data)
