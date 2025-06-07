#!/bin/bash

# Parallel Results Generation Script for Time-Critical Submissions
set -e

echo "🚀 Black Box Challenge - Parallel Results Generation"
echo "===================================================="

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed!"
    exit 1
fi

# Check if private cases exist
if [ ! -f "private_cases.json" ]; then
    echo "❌ Error: private_cases.json not found!"
    exit 1
fi

# Make run.sh executable
chmod +x run.sh

# Get total cases
total_cases=$(jq length private_cases.json)
echo "📊 Processing $total_cases test cases in parallel..."

# Remove existing results file
rm -f private_results.txt

# Create temporary directory for parallel processing
temp_dir="temp_parallel_$$"
mkdir -p "$temp_dir"

# Function to process a batch of test cases
process_batch() {
    local start_idx=$1
    local end_idx=$2
    local batch_file="$3"
    
    echo "Processing batch $start_idx to $end_idx..." >&2
    
    # Extract batch of test cases
    jq -r ".[$start_idx:$end_idx] | .[] | \"\(.trip_duration_days):\(.miles_traveled):\(.total_receipts_amount)\"" private_cases.json > "$temp_dir/batch_$start_idx.txt"
    
    # Process each line in the batch
    while IFS=':' read -r trip_duration miles_traveled receipts_amount; do
        if script_output=$(./run.sh "$trip_duration" "$miles_traveled" "$receipts_amount" 2>/dev/null); then
            output=$(echo "$script_output" | tr -d '[:space:]')
            if [[ $output =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
                echo "$output"
            else
                echo "ERROR"
            fi
        else
            echo "ERROR"
        fi
    done < "$temp_dir/batch_$start_idx.txt" > "$batch_file"
}

export -f process_batch
export temp_dir

# Calculate batch size (divide into 5 parallel processes)
batch_size=$((total_cases / 5))
if [ $((total_cases % 5)) -ne 0 ]; then
    batch_size=$((batch_size + 1))
fi

echo "📦 Batch size: $batch_size cases per process"
echo "🔄 Starting parallel processing..."

# Create batch processing commands
for i in {0..4}; do
    start_idx=$((i * batch_size))
    end_idx=$(((i + 1) * batch_size))
    if [ $end_idx -gt $total_cases ]; then
        end_idx=$total_cases
    fi
    
    if [ $start_idx -lt $total_cases ]; then
        echo "process_batch $start_idx $end_idx $temp_dir/results_$i.txt"
    fi
done > "$temp_dir/commands.txt"

# Run batches in parallel using xargs (more portable than GNU parallel)
cat "$temp_dir/commands.txt" | xargs -n 3 -P 5 bash -c 'process_batch "$@"' _

# Combine results in correct order
echo "🔗 Combining results..."
for i in {0..4}; do
    if [ -f "$temp_dir/results_$i.txt" ]; then
        cat "$temp_dir/results_$i.txt" >> private_results.txt
    fi
done

# Cleanup
rm -rf "$temp_dir"

echo "✅ Parallel processing complete!"
echo "📄 Results saved to private_results.txt"
echo "⏱️  Processing time significantly reduced!" 