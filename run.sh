

output_dir="SD1.5"

python generation/diffusers_generate.py \
    "prompts/evaluation_metadata.jsonl" \
    --model "stable-diffusion-v1-5/stable-diffusion-v1-5" \
    --outdir $output_dir \
    --n_samples 32 \
    --batch_size 8 \
    --seed 43 



python evaluation/evaluate_images.py \
    "$output_dir" \
    --outfile "results/results_$output_dir.jsonl" \
    --model-path "./"



python evaluation/summary_scores.py \
    "results/results_$output_dir.jsonl"
