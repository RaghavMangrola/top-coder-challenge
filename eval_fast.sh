#!/bin/bash

# Ultra-Fast Black Box Challenge Evaluation Script
# Uses batch processing instead of 1000 individual Python calls

set -e

echo "🚀 Ultra-Fast Black Box Challenge - Batch Evaluation"
echo "===================================================="
echo

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed!"
    echo "Please install jq: brew install jq"
    exit 1
fi

# Check if bc is available
if ! command -v bc &> /dev/null; then
    echo "❌ Error: bc is required but not installed!"
    echo "Please install bc: brew install bc"
    exit 1
fi

# Check if public cases exist
if [ ! -f "public_cases.json" ]; then
    echo "❌ Error: public_cases.json not found!"
    exit 1
fi

echo "📊 Running ultra-fast batch evaluation against 1,000 test cases..."
echo

# Get expected outputs for comparison
echo "Extracting expected outputs..."
expected_outputs=$(jq -r '.[].expected_output' public_cases.json)

# Run batch prediction (single Python call for all 1000 cases!)
echo "Running batch prediction..."
start_time=$(date +%s.%N)
actual_outputs=$(python3 calculate_ultra_fast.py batch 2>/dev/null)
end_time=$(date +%s.%N)

# Calculate elapsed time
elapsed=$(echo "$end_time - $start_time" | bc)
echo "⚡ Batch prediction completed in ${elapsed} seconds!"

# Convert outputs to arrays
expected_array=()
actual_array=()

while IFS= read -r line; do
    expected_array+=("$line")
done <<< "$expected_outputs"

while IFS= read -r line; do
    actual_array+=("$line")
done <<< "$actual_outputs"

# Verify we have the same number of results
if [ ${#expected_array[@]} -ne ${#actual_array[@]} ]; then
    echo "❌ Error: Mismatch in number of results!"
    echo "Expected: ${#expected_array[@]}, Got: ${#actual_array[@]}"
    exit 1
fi

num_cases=${#expected_array[@]}
echo "Processing $num_cases results..."

# Initialize counters
successful_runs=$num_cases
exact_matches=0
close_matches=0
total_error="0"
max_error="0"
max_error_case=""
high_error_cases=()

# Process results
for ((i=0; i<num_cases; i++)); do
    if [ $((i % 200)) -eq 0 ]; then
        echo "Progress: $i/$num_cases cases analyzed..." >&2
    fi
    
    expected="${expected_array[i]}"
    actual="${actual_array[i]}"
    
    # Calculate absolute error
    error=$(echo "scale=10; if ($actual - $expected < 0) -1 * ($actual - $expected) else ($actual - $expected)" | bc)
    
    # Check for exact match (within $0.01)
    if (( $(echo "$error < 0.01" | bc -l) )); then
        exact_matches=$((exact_matches + 1))
    fi
    
    # Check for close match (within $1.00)
    if (( $(echo "$error < 1.0" | bc -l) )); then
        close_matches=$((close_matches + 1))
    fi
    
    # Update total error
    total_error=$(echo "scale=10; $total_error + $error" | bc)
    
    # Track maximum error and high-error cases
    if (( $(echo "$error > $max_error" | bc -l) )); then
        max_error="$error"
        max_error_case="Case $((i+1))"
    fi
    
    # Store high-error cases for analysis
    if (( $(echo "$error > 50" | bc -l) )); then
        # Get case details from JSON
        case_details=$(jq -r ".[$i] | \"$((i+1)):\(.input.trip_duration_days):\(.input.miles_traveled):\(.input.total_receipts_amount)\"" public_cases.json)
        high_error_cases+=("$case_details:$expected:$actual:$error")
    fi
done

# Calculate and display results
avg_error=$(echo "scale=2; $total_error / $successful_runs" | bc)
exact_pct=$(echo "scale=1; $exact_matches * 100 / $successful_runs" | bc)
close_pct=$(echo "scale=1; $close_matches * 100 / $successful_runs" | bc)

echo "✅ Ultra-Fast Evaluation Complete!"
echo ""
echo "⚡ Performance:"
echo "  Total processing time: ${elapsed} seconds"
echo "  Speed improvement: ~$(echo "scale=0; 900 / $elapsed" | bc)x faster than sequential"
echo ""
echo "📈 Results Summary:"
echo "  Total test cases: $num_cases"
echo "  Successful runs: $successful_runs"
echo "  Exact matches (±\$0.01): $exact_matches (${exact_pct}%)"
echo "  Close matches (±\$1.00): $close_matches (${close_pct}%)"
echo "  Average error: \$${avg_error}"
echo "  Maximum error: \$${max_error}"
echo ""

# Calculate score (lower is better)
score=$(echo "scale=2; $avg_error * 100 + ($num_cases - $exact_matches) * 0.1" | bc)
echo "🎯 Your Score: $score (lower is better)"
echo ""

# Provide feedback
if [ $exact_matches -eq $num_cases ]; then
    echo "🏆 PERFECT SCORE! You have reverse-engineered the system completely!"
elif [ $exact_matches -gt 950 ]; then
    echo "🥇 Excellent! You are very close to the perfect solution."
elif [ $exact_matches -gt 800 ]; then
    echo "🥈 Great work! You have captured most of the system behavior."
elif [ $exact_matches -gt 500 ]; then
    echo "🥉 Good progress! You understand some key patterns."
else
    echo "📚 Keep analyzing the patterns in the interviews and test cases."
fi

# Show high-error cases for analysis
if [ ${#high_error_cases[@]} -gt 0 ]; then
    echo ""
    echo "💡 High-error cases for analysis (error > \$50):"
    
    # Sort and show top 5 high-error cases
    IFS=$'\n' sorted_errors=($(printf '%s\n' "${high_error_cases[@]}" | sort -t: -k8 -nr | head -5))
    for result in "${sorted_errors[@]}"; do
        IFS=: read -r case_num days miles receipts expected actual error <<< "$result"
        printf "    Case %s: %s days, %s miles, \$%s receipts\n" "$case_num" "$days" "$miles" "$receipts"
        printf "      Expected: \$%.2f, Got: \$%.2f, Error: \$%.2f\n" "$expected" "$actual" "$error"
    done
fi

echo ""
echo "🚀 Performance Summary:"
echo "  M1 Optimization: ✅ Vectorized operations, single model loading"
echo "  Batch Processing: ✅ 1 Python call instead of 1000"
echo "  Speed Improvement: ~$(echo "scale=0; 900 / $elapsed" | bc)x faster"
echo ""
echo "📝 Next steps:"
echo "  1. Analyze high-error cases above"
echo "  2. Fine-tune model hyperparameters"
echo "  3. Consider ensemble improvements"
echo "  4. Submit when ready via Google Form!" 