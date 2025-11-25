# every_eval_ever

## What is EvalEval?

> "We are a researcher community developing scientifically grounded research outputs and robust deployment infrastructure for broader impact evaluations."[EvalEval Coalition](https://evalevalai.com)

The EvalEval Coalition focuses on conducting rigorous research on AI evaluation methods, building practical infrastructure for evaluation work, and organizing collaborative efforts across their researcher community. This repository, **every_eval_ever**, provides a standarized metadata format for storing evaluation results from various leaderboards, research, and local evaluations.

## Contributor Guide
Leaderboard/evaluation data is split-up into files by individual model, and data for each model is stored using [this JSON Schema](https://github.com/evaleval/evalHub/blob/main/schema/eval.schema.json). The repository is structured into folders as `{leaderboard_name}/{developer_name}/{model_name}/`.

### UUID Naming Convention

Each JSON file is named with a **UUID (Universally Unique Identifier)** in the format `{uuid}.json`. The UUID is automatically generated (using standard UUID v4) when creating a new evaluation result file. This ensures that:
- **Multiple evaluations** of the same model can exist without conflicts (each gets a unique UUID)
- **Different timestamps** are stored as separate files with different UUIDs (not as separate folders)
- A model may have multiple result files, with each file representing different iterations or runs of the leaderboard/evaluation

**Example**: The model `openai/gpt-4o-2024-11-20` might have multiple files like:
- `e70acf51-30ef-4c20-b7cc-51704d114d70.json` (evaluation run #1)
- `a1b2c3d4-5678-90ab-cdef-1234567890ab.json` (evaluation run #2)

Note: Each file can contain multiple individual results related to one model. See [examples in /data](data/).

### How to add a new leaderboard:

1. Add a new folder under `/data` with a codename for your leaderboard.
2. For each model, use the HuggingFace (`developer_name/model_name`) naming convention to create a 2-tier folder structure.
3. Add a JSON file with results for each model and name it `{uuid}.json`.
4. [Optional] Include a `scripts` folder in your leaderboard folder with any scripts used to generate the data.
5. [Validate] Validation Script: Adds workflow (`workflows/validate-data.yml`) that runs validation script (`scripts/validate_data.py`) to check JSON files against schema and report errors before merging.

### Schema Instructions

1. **`model_info`**: Use HuggingFace formatting (`developer_name/model_name`). If a model does not come from HuggingFace, use the exact API reference. Check [examples in /data/livecodebenchpro](data/livecodebenchpro/).Notably, some do have a **date included in the model name**, but others **do not**. For example: 
- OpenAI: `gpt-4o-2024-11-20`, `gpt-5-2025-08-07`, `o3-2025-04-16`
- Anthropic: `claude-3-7-sonnet-20250219`, `claude-3-sonnet-20240229`
- Google: `gemini-2.5-pro`, `gemini-2.5-flash`
- xAI (Grok): `grok-2-2024-08-13`, `grok-3-2025-01-15`


2. **`evaluation_id`**: Use `{org_name}/{eval_name}/{retrieved_timestamp}` format.

3. **`inference_platform`**: The platform where the model was run (e.g., `openai`, `huggingface`, `openrouter`, `anthropic`, `xai`).

## Data Validation

This repository has a pre-commit that will validate that JSON files conform to the JSON schema. The pre-commit requires using [uv](https://docs.astral.sh/uv/) for dependency management.

To run the pre-commit on git staged files only:

```sh
uv run pre-commit run
```

To run the pre-commit on all files:

```sh
uv run pre-commit run --all-files
```

To run the pre-commit on specific files:

```sh
uv run pre-commit run --files a.json b.json c.json
```

To install the pre-commit so that it will run before `git commit` (optional):

```sh
uv run pre-commit install
```

## Repository Structure

```
data/
├── {eval_name}/
│   └── {developer_name}/
│       └─��� {model_name}/
│           └── {uuid}.json
│
scripts/
└── validate_data.py

.github/
└── workflows/
    └── validate-data.yml
```

Each evaluation (e.g., `livecodebenchpro`, `hfopenllm_v2`) has its own directory under `data/`. Within each evaluation, models are organized by model name, with a `{uuid}.json` file containing the evaluation results for that model.

