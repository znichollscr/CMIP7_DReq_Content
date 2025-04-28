import copy
import json
from pathlib import Path

import pandas as pd
import tqdm
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
    IN_DIR = REPO_ROOT / "variables-split"
    KARL_FILE = "v1_2-Variables-Spreadsheet-KT-review-041525.xlsx"

    karl_table = pd.read_excel(KARL_FILE, sheet_name="v1.2 Variables")
    idx_col = "CMIP6 Compound Name"
    karl_table_reidx = karl_table.loc[~karl_table[idx_col].isnull()].set_index(idx_col)

    for cmip6_compound_name, row in tqdm.tqdm(karl_table_reidx.iterrows()):
        file_of_interest = IN_DIR / f"{cmip6_compound_name}.json"
        if not file_of_interest.exists():
            print(f"No file for {cmip6_compound_name} in new release")
            continue

        with open(file_of_interest) as fh:
            raw = json.load(fh)

        updated = copy.deepcopy(raw)

        dimensions = split_dimensions(row["dimensions for determining branding suffix"])
        cell_methods = row["cell_methods for determining branding suffix"].strip()
        variable_root = row["variableRootDD"]
        branded_variable = map_to_cmip_branded_variable(
            variable_name=variable_root,
            dimensions=dimensions,
            cell_methods=cell_methods,
        )

        updated["dimensions"] = dimensions
        updated["cell_methods"] = cell_methods
        updated["variableRootDD"] = variable_root
        updated["branded_variable"] = branded_variable
        updated["description"] = row.Description
        updated["@@review_requested"] = row["Review Requested"]

        with open(file_of_interest, "w") as fh:
            json.dump(updated, fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
