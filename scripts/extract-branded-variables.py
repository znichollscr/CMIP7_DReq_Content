import copy
import json
from collections import defaultdict
from pathlib import Path

import tqdm


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
    OUT_DIR = REPO_ROOT / "branded-variables"
    OUT_DIR.mkdir(exist_ok=True, parents=True)

    bvs = defaultdict(list)
    for file in tqdm.tqdm(
        IN_DIR.glob("*.json"), desc="Rows in data request variables table"
    ):
        with open(file) as fh:
            raw = json.load(fh)

        branded_variable = raw["branded_variable"]
        bvs[branded_variable].append(raw)

    n_clashes = 0
    for branded_variable, records in tqdm.tqdm(bvs.items(), desc="Branded variables"):
        if len(records) == 1:
            # no dups
            branded_variable_info = records[0]
            branded_variable_info.pop("@@review_requested")
            branded_variable_info.pop("cmip6_compound_name")

        else:
            records_checker = copy.deepcopy(records)
            for r in records_checker:
                r.pop("cmip6_compound_name")

            branded_variable_info = records_checker[0]
            all_same = all(r == branded_variable_info for r in records_checker)
            if not all_same:
                for r in records_checker:
                    r.pop("description")

                branded_variable_info = records_checker[0]
                all_same = all(r == records_checker[0] for r in records_checker)
                if not all_same:
                    clashing = {}
                    for k in branded_variable_info:
                        if not all(
                            branded_variable_info[k] == rc[k] for rc in records_checker
                        ):
                            clashing[k] = [rc[k] for rc in records_checker]

                    print()
                    print(f"Clash for {branded_variable}, not writing output")
                    # print(records_checker)
                    print(clashing)
                    print()
                    n_clashes += 1
                    continue

                branded_variable_info["description"] = "TBC (clashes in original table)"

            branded_variable_info.pop("@@review_requested")

        out_file = OUT_DIR / f"{branded_variable}.json"
        with open(out_file, "w") as fh:
            json.dump(branded_variable_info, fh, indent=2, sort_keys=True)

    print()
    print(f"{n_clashes=}")


if __name__ == "__main__":
    main()
