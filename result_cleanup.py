import argparse
import json
import os
import sqlite3
import pandas as pd


parser = argparse.ArgumentParser(
    description="Parses args"
)
parser.add_argument('-r',
                    '--results',
                    help="Path to results folder.",
                    required=True,
                    )
parser.add_argument('-o',
                    '--outfile',
                    help="Location to save the outfile.",
                    required=True,
                    )
args = parser.parse_args()


con = sqlite3.connect("mutation_config.sqlite")
mutation_specs = pd.read_sql_query("SELECT * from mutation_specs", con, index_col="job_id")
work_results = pd.read_sql_query("SELECT * from work_results", con, index_col="job_id")
con.close()

results = {}
for job in os.listdir(args.results):
    if not job.endswith(".json") or job.endswith("mutation_config.json") or "results" in job:
        continue
    job_id = job[:-5]
    result = {}
    with open(job) as f:
        result["test_outcomes"] = json.load(f)
        if job_id != "baseline":
            result["mutation_spec"] = mutation_specs.loc[job_id].to_dict()
            result["work_result"] = work_results.loc[job_id].to_dict()
        results[job_id] = result
    os.remove(os.path.join(args.results, job))
with open(os.path.join(args.results, args.outfile), 'w') as f:
    print(json.dumps(results, indent=2), file=f)
