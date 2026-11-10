"""Fail the check if a saved plan violates constraints or its certified cost."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'benchmark'))
from validate_oracle_plans import FILES, instances, validate

expected_cost = {'Facil': 7, 'Medio': 17, 'Dificil': 11, 'Muito dificil': 48}
for instance in instances:
    result = validate(instance, ROOT / 'plans' / FILES[instance.name])
    assert result[0], (instance.name, result)
    assert result[1] == expected_cost[instance.name], (instance.name, result)
print('Four plans satisfy the validator and match the certified travel costs.')
