import json
from pathlib import Path

import tqdm
from cmip_branded_variable_mapper import map_to_cmip_branded_variable


def main():
    REPO_ROOT = Path(__file__).parents[1]
    OUT_DIR = REPO_ROOT / "branded-variables"
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
        cell_methods = top_level[key]["records"][cm_pid][key]

        key = "Physical Parameter"
        pp_pid_l = record[key]
        if len(pp_pid_l) > 1:
            raise AssertionError
        pp_pid = pp_pid_l[0]

        variable_root = top_level[f"{key}s"]["records"][pp_pid]["Name"]
        description = record["Title"]

        records_l.append(
            {
                "cell_methods": cell_methods,
                "dimensions": dimensions,
                "variableRootDD": variable_root,
                "description": description,
            }
        )

    # # Silly to loop again, but easier cognitively
    # # and allows us to dump this in a dataframe if we want.
    # variables = pd.DataFrame(records_l)
    for rr in tqdm.tqdm(records_l):
        to_write = rr | {
            "@context": "TBD",
            "id": "TBD",
            "type": ["TBD"],
            "label": "TBD",
            "branded_variable": map_to_cmip_branded_variable(
                variable_name=rr["variableRootDD"],
                dimensions=rr["dimensions"],
                cell_methods=rr["cell_methods"],
            ),
        }

        with open(OUT_DIR / f"{to_write['branded_variable']}.json", "w") as fh:
            json.dump(to_write, fh, indent=2, sort_keys=2)


if __name__ == "__main__":
    main()
