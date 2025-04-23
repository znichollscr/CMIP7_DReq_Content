import json
from pathlib import Path

import pandas as pd
import tqdm
from cmip_branded_variable_mapper import map_to_cmip_branded_variable


def main():
    REPO_ROOT = Path(__file__).parents[1]
    OUT_DIR = REPO_ROOT / "variables-split"
    OUT_DIR.mkdir(exist_ok=True, parents=True)

    with open(REPO_ROOT / "airtable_export" / "dreq_release_export.json") as fh:
        raw_table = json.load(fh)

    top_level = raw_table["Data Request v1.2"]
    table_to_export = "Variables"

    records_l = []
    for pid, record in top_level[table_to_export]["records"].items():
        dimensions = tuple(v.strip() for v in record["Dimensions"].split(","))

        key = "Cell Methods"
        cm_pid_l = record[key]
        if len(cm_pid_l) > 1:
            raise AssertionError
        cm_pid = cm_pid_l[0]
        cell_methods = top_level[key]["records"][cm_pid][key].strip()

        key = "Physical Parameter"
        pp_pid_l = record[key]
        if len(pp_pid_l) > 1:
            raise AssertionError
        pp_pid = pp_pid_l[0]

        variable_root = top_level[f"{key}s"]["records"][pp_pid]["Name"].strip()
        description = record["Title"]
        cmip6_compound_name = record["CMIP6 Compound Name"]

        records_l.append(
            {
                "cell_methods": cell_methods,
                "dimensions": dimensions,
                "variableRootDD": variable_root,
                "description": description,
                "cmip6_compound_name": cmip6_compound_name,
            }
        )

    # Silly to loop again, but easier cognitively
    # and allows us to dump this in a dataframe if we want.
    variables = pd.DataFrame(records_l)
    # print({c: len(variables[c].unique()) for c in variables})
    # Make sure this key will give unique outputs
    assert len(variables["cmip6_compound_name"].unique()) == variables.shape[0]
    assert (
        len(variables["cmip6_compound_name"].str.lower().unique()) == variables.shape[0]
    )

    variables_reindexed = variables.set_index("cmip6_compound_name")
    for cmip6_compound_name, row in tqdm.tqdm(variables_reindexed.iterrows()):
        branded_variable = map_to_cmip_branded_variable(
            variable_name=row.variableRootDD,
            dimensions=row.dimensions,
            cell_methods=row.cell_methods,
        )

        to_write = {
            "cmip6_compound_name": cmip6_compound_name,
            "dimensions": row.dimensions,
            "cell_methods": row.cell_methods,
            "variableRootDD": row.variableRootDD,
            "description": row.description,
            "@context": "TBD",
            "id": "TBD",
            "type": ["TBD"],
            "label": "TBD",
            "branded_variable": branded_variable,
        }

        out_file = OUT_DIR / f"{cmip6_compound_name}.json"

        if out_file.exists():
            raise FileExistsError(out_file)

        with open(out_file, "w") as fh:
            json.dump(to_write, fh, indent=2, sort_keys=2)


if __name__ == "__main__":
    main()
