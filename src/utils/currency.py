import json
from pathlib import Path
from pydantic import BaseModel

def generate_currency_dict() -> dict[str, str]:
    with open("data/currency/currency_codes.txt", "r") as f:
        currency_codes = f.read().splitlines()

    class RawCurrencyLine(BaseModel):
        currency_code: str
        currency_name: str

    raw_currency_lines = [RawCurrencyLine(currency_code=line.split(":")[0].strip(), currency_name=line.split(":")[1].strip()) for line in currency_codes]
    currency_dict = {line.currency_code: line.currency_name for line in raw_currency_lines}

    with open("data/currency/currency_dict.json", "w") as f:
        json.dump(currency_dict, f)

    return currency_dict
    
def _load_currency_codes() -> set[str]:
    currency_path = Path("data/currency/currency_dict.json")
    if not currency_path.exists():
        generate_currency_dict()
    else:
        data = json.loads(currency_path.read_text())
        return set(data.keys())

CURRENCY_CODES = _load_currency_codes()