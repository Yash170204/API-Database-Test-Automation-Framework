import json
import os
from typing import Any, Dict
import jsonschema
from src.utils.logger import logger

def load_json_schema(schema_filename: str) -> Dict[str, Any]:
    """Loads a JSON schema from the schemas directory."""
    # Build absolute path to schemas directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    schema_path = os.path.join(base_dir, "schemas", schema_filename)
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"JSON Schema file not found: {schema_path}")
        
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_json_schema(data: Any, schema_filename: str) -> bool:
    """Validates data against a specific JSON schema file.
    Raises jsonschema.exceptions.ValidationError on failure.
    """
    schema = load_json_schema(schema_filename)
    try:
        jsonschema.validate(instance=data, schema=schema)
        logger.info(f"JSON Schema validation PASSED for schema: {schema_filename}")
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"JSON Schema validation FAILED for schema '{schema_filename}': {e.message}")
        logger.error(f"Failed element: {e.instance}")
        raise e
