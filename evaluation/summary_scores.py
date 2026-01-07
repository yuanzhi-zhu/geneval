# Get results of evaluation

import argparse
import os

import numpy as np
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str)
args = parser.parse_args()

# Load classnames

with open(os.path.join(os.path.dirname(__file__), "object_names.txt")) as cls_file:
    classnames = [line.strip() for line in cls_file]
    cls_to_idx = {"_".join(cls.split()):idx for idx, cls in enumerate(classnames)}

# Load results

df = pd.read_json(args.filename, orient="records", lines=True)

GenEval_Ns = [1, 2, 3, 4, 8, 16, 32, 48, 64]
GenEval_Ns_scores = []
GenEval_Ns_bon_scores = []

for BoN in GenEval_Ns:
    # bon_df = (
    #     df.groupby("metadata", sort=False)
    #       .apply(lambda g: g[g["correct"]].head(BoN) if g["correct"].any() else g.head(BoN))
    #       .reset_index(drop=True)
    # )
    first_N_df = (
        df.groupby("metadata", sort=False)
          .apply(lambda g: g.head(BoN))
          .reset_index(drop=True)
    )
    
    # Measure overall success

    print("Summary: N =", BoN)
    print("=======")
    print(f"Total images: {len(first_N_df)}")
    print(f"Total prompts: {len(first_N_df.groupby('metadata'))}")
    print(f"% correct images: {first_N_df['correct'].mean():.2%}")
    print(f"% correct prompts: {first_N_df.groupby('metadata')['correct'].any().mean():.2%}")
    print()

    # By group

    task_scores = []

    print("Task breakdown: N =", BoN)
    print("==============")
    for tag, task_df in first_N_df.groupby('tag', sort=False):
        task_scores.append(task_df['correct'].mean())
        print(f"{tag:<16} = {task_df['correct'].mean():.2%} ({task_df['correct'].sum()} / {len(task_df)})")
    print()

    print(f"Overall score (avg. over tasks): {np.mean(task_scores):.5f}")
    GenEval_Ns_scores.append(np.mean(task_scores))
    
    bon_df = (
        first_N_df.groupby("metadata", sort=False)
          .apply(lambda g: g[g["correct"]].head(1) if g["correct"].any() else g.head(1))
          .reset_index(drop=True)
    )

    print(f"BON Summary: N = {BoN}")
    print("===========")
    print(f"Total prompts: {len(bon_df)}")
    print(f"% correct prompts: {bon_df['correct'].mean():.2%}")
    print()

    bon_task_scores = []
    print(f"BON ({BoN}) Task breakdown")
    print("==============")
    for tag, task_df in bon_df.groupby('tag', sort=False):
        bon_task_scores.append(task_df['correct'].mean())
        print(f"{tag:<16} = {task_df['correct'].mean():.2%} ({task_df['correct'].sum()} / {len(task_df)})")
    print()
    print(f"BON Overall score (avg. over tasks): {np.mean(bon_task_scores):.5f}")
    print()
    
    GenEval_Ns_bon_scores.append(np.mean(bon_task_scores))

## plot the results
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 6))
plt.plot(GenEval_Ns, GenEval_Ns_scores, marker='o', label='GenEval Scores')
plt.plot(GenEval_Ns, GenEval_Ns_bon_scores, marker='s', label='GenEval BoN Scores')
plt.xscale('log', base=2)
plt.xticks(GenEval_Ns, GenEval_Ns)
plt.xlabel('Number of Samples per Prompt (N)')
plt.ylabel('Score (Average over Tasks)')
plt.title(f'GenEval vs # Samples per Prompt ({args.filename.split(".jsonl")[0]})')
plt.legend()
plt.grid(True)
# file_name = os.path.splitext(os.path.basename(args.filename))[0]
plt.savefig(f'{args.filename.split(".jsonl")[0]}_scores_vs_N.png', dpi=600)