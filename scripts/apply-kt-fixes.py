import copy
import json
from pathlib import Path

import pandas as pd


def split_dimensions(d: str) -> list[str]:
    if "," in d:
        res = [v.strip() for v in d.split(",")]
    else:
        # Assume space separated
        res = [v.strip() for v in d.split(" ")]

    return res


def main():
    REPO_ROOT = Path(__file__).parents[1]
    IN_DIR = REPO_ROOT / "variables"
    KARL_FILE = "v1_2-Variables-Spreadsheet-KT-review-041525.xlsx"

    karl_table = pd.read_excel(KARL_FILE, sheet_name="v1.2 Variables").set_index(
        "Physical Parameter"
    )

    for json_file in IN_DIR.glob("*.json"):
        with open(json_file) as fh:
            raw = json.load(fh)

        updated = copy.deepcopy(raw)
        variableRootDD = raw["variableRootDD"]

        karl_row = karl_table.loc[variableRootDD]
        if len(karl_row.shape) > 1:
            ket_comments = karl_row["KET comments"]
            can_be_eliminated = ket_comments.map(
                lambda x: not isinstance(x, float) and "see ***" in x
            )
            if (~can_be_eliminated).sum() < 1:
                # All can be eliminated, so just take the first
                karl_row = karl_row.iloc[0, :]

            elif (~can_be_eliminated).sum() > 1:
                print(f"Not clear how to deal with duplicates for {variableRootDD}")
                continue

            else:
                karl_row = karl_row[~can_be_eliminated].loc[variableRootDD]

        for karl_key, data_key, pre_processor in (
            (
                "cell_methods for determining branding suffix",
                "cell_methods",
                lambda x: x.strip(),
            ),
            (
                "dimensions for determining branding suffix",
                "dimensions",
                split_dimensions,
            ),
        ):
            if len(karl_row.shape) > 1:
                karl_value_l = karl_row.loc[:, karl_key].unique().tolist()
                if len(karl_value_l) > 1:
                    breakpoint()

                karl_value = karl_value_l[0]

            else:
                karl_value = karl_row.loc[karl_key]

            if pre_processor is not None:
                karl_value = pre_processor(karl_value)

            if data_key == "dimensions" and any("area" in v for v in karl_value):
                print(
                    "Assuming Karl didn't mean to put area in dimensions, but good to check. "
                    f"{data_key=} {karl_value=}"
                )

            updated[data_key] = karl_value

        with open(json_file, "w") as fh:
            json.dump(updated, fh, indent=2)


if __name__ == "__main__":
    main()
