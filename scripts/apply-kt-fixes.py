import json
from pathlib import Path

import pandas as pd
from cmip_branded_variable_mapper import map_to_cmip_branded_variable


def split_dimensions(d: str) -> tuple[str, ...]:
    if "," in d:
        res = tuple([v.strip() for v in d.split(",")])
    else:
        # Assume space separated
        res = tuple([v.strip() for v in d.split(" ")])

    return res


def main():
    REPO_ROOT = Path(__file__).parents[1]
    OUT_DIR = REPO_ROOT / "branded-variables"
    KARL_FILE = "v1_2-Variables-Spreadsheet-KT-review-041525.xlsx"

    karl_table = pd.read_excel(KARL_FILE, sheet_name="v1.2 Variables")

    for _, row in karl_table.iterrows():
        if pd.isnull(row["Physical Parameter"]):
            continue

        dimensions = split_dimensions(row["dimensions for determining branding suffix"])
        cell_methods = row["cell_methods for determining branding suffix"].strip()
        variable_root = row["variableRootDD"]
        # Descriptions change no matter what I do, whatever
        # description = row["Title"]
        description = row["Description"]

        res = {
            "cell_methods": cell_methods,
            "dimensions": dimensions,
            "variableRootDD": variable_root,
            "description": description,
            "@context": "TBD",
            "id": "TBD",
            "type": ["TBD"],
            "label": "TBD",
            "branded_variable": map_to_cmip_branded_variable(
                variable_name=variable_root,
                dimensions=dimensions,
                cell_methods=cell_methods,
            ),
        }
        with open(OUT_DIR / f"{res['branded_variable']}.json", "w") as fh:
            json.dump(res, fh, indent=2, sort_keys=2)


if __name__ == "__main__":
    main()
