import argparse
import json
import os
import sqlite3
import pandas as pd


def relation_passed(outcome):
    # Independence relations - Fails if any test failed
    if "_||_" in outcome["relation"]:
        return outcome["failed"]
    # Dependence relations - Fails if all tests failed
    elif "-->" in outcome["relation"]:
        return len(outcome["failed"]) < outcome["total"]
    else:
        raise ValueError(f"Invalid outcome relation {outcome['relation']}. Expected '_||_' or '-->'")


parser = argparse.ArgumentParser(
    description="Parses args"
)
parser.add_argument('-r',
                    '--results',
                    help="Path to results folder.",
                    required=True,
                    )
parser.add_argument('-db',
                    '--database',
                    help="Name of mutation configuration database (sqlite file).",
                    required=True,
                    )
parser.add_argument('-o',
                    '--outfile',
                    help="Location to save the outfile.",
                    required=True,
                    )
args = parser.parse_args()
con = sqlite3.connect(args.database)
mutation_specs = pd.read_sql_query("SELECT * from mutation_specs", con, index_col="job_id")
work_results = pd.read_sql_query("SELECT * from work_results", con, index_col="job_id")
con.close()

results = {}
for job in os.listdir(args.results):
    if not job.endswith(".json") or "mutation_config" in job or "results" in job:
        continue
    job_id = job[:-5]
    result = {}
    with open(os.path.join(args.results, job)) as f:
        # result["test_outcomes"] = json.load(f)
        test_outcomes = json.load(f)
        results[job_id] = {}
        # for relation in result["test_outcomes"]:
            # relation["passed"] = not relation["failed"]
        if job_id != "baseline":
            mutation_spec = mutation_specs.loc[job_id].to_dict()
            work_result = work_results.loc[job_id].to_dict()
            mutation_dict = {"operator": mutation_spec["operator_name"],
                             "args": mutation_spec["operator_args"],
                             "outcome": work_result["test_outcome"],
                             "diff": work_result["diff"]}
            results[job_id] = mutation_dict
        else:
            results[job_id]["total_tests"] = sum([relation["total"] for relation in test_outcomes])
            results[job_id]["n_tests"] = test_outcomes[0]["total"]
            results[job_id]["total_relations"] = len(test_outcomes)
        results[job_id]["failed_relations"] = [mr["relation"] for mr in test_outcomes if mr["failed"]]

            # results["mutation_operator_args"] = mutation_spec
            # result["work_result"] = work_results.loc[job_id].to_dict()
        # results[job_id] = result
    os.remove(os.path.join(args.results, job))
with open(os.path.join(args.results, args.outfile), 'w') as f:
    print(json.dumps(results), file=f)
