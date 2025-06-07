#!/bin/bash

# Ultra-Fast Black Box Challenge - Private Results Generation Script
# Uses batch processing for maximum speed while maintaining output format compatibility

set -e

echo "🚀 Ultra-Fast Black Box Challenge - Generating Private Results"
echo "=============================================================="
echo

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed!"
    echo "Please install jq: brew install jq"
    exit 1
fi

# Check if private cases exist
if [ ! -f "private_cases.json" ]; then
    echo "❌ Error: private_cases.json not found!"
    echo "Please ensure the private cases file is in the current directory."
    exit 1
fi

echo "📊 Processing test cases using ultra-fast batch mode..."
echo "📝 Output will be saved to private_results.txt"
echo

# Remove existing results file if it exists
rm -f private_results.txt

# Get total number of cases
total_cases=$(jq length private_cases.json)
echo "Processing $total_cases test cases..." >&2

# Run batch prediction using our ultra-fast calculator
echo "Running ultra-fast batch prediction..."
start_time=$(date +%s.%N)

# Create a temporary modified script for private cases
python3 -c "
import json
import pandas as pd
import numpy as np
import joblib
import sys
import os

# Same configuration as calculate_ultra_fast.py
ENSEMBLE_SIZE = 5
MAIN_MODEL_FILES = [f'ensemble_main_{i}.joblib' for i in range(ENSEMBLE_SIZE)]
OUTLIER_MODEL_FILES = [f'ensemble_outlier_{i}.joblib' for i in range(ENSEMBLE_SIZE)]
OUTLIER_THRESHOLD = 1400

def feature_engineering(df):
    # Same feature engineering as calculate_ultra_fast.py
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    df.fillna(0, inplace=True)
    df['four_day_bonus'] = (df['trip_duration_days'] == 4).astype(int) * 150
    
    conditions = [
        (df['trip_duration_days'] == 1),
        (df['trip_duration_days'] == 5),
        (df['trip_duration_days'] >= 8)
    ]
    choices = [-0.5, 1.04, 0.02]
    df['receipt_multiplier'] = np.select(conditions, choices, default=1.0)
    
    df['adjusted_receipts'] = np.where(
        df['total_receipts_amount'] > 2000, 
        df['total_receipts_amount'] * 0.25, 
        df['total_receipts_amount']
    )
    df['multiplied_receipts'] = df['adjusted_receipts'] * df['receipt_multiplier']
    
    df['miles_tier1'] = np.clip(df['miles_traveled'], 0, 100)
    df['miles_tier2'] = np.clip(df['miles_traveled'] - 100, 0, 400)
    df['miles_tier3'] = np.clip(df['miles_traveled'] - 500, 0, None)
    
    df['efficiency_bonus_range'] = (
        (df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)
    ).astype(int)
    
    conditions = [
        (df['trip_duration_days'] <= 2) & (df['miles_per_day'] > 150),
        (df['trip_duration_days'] >= 8),
        (df['miles_per_day'] < 50),
        (df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)
    ]
    choices = ['quick_trip_high_miles', 'long_haul', 'low_efficiency', 'sweet_spot_efficiency']
    df['trip_category'] = np.select(conditions, choices, default='balanced')
    
    df = pd.get_dummies(df, columns=['trip_category'], prefix='cat')
    df['days_x_miles'] = df['trip_duration_days'] * df['miles_traveled']
    
    return df

def load_models():
    main_models = []
    outlier_models = []
    
    for i in range(ENSEMBLE_SIZE):
        if os.path.exists(MAIN_MODEL_FILES[i]):
            main_models.append(joblib.load(MAIN_MODEL_FILES[i]))
        if os.path.exists(OUTLIER_MODEL_FILES[i]):
            outlier_models.append(joblib.load(OUTLIER_MODEL_FILES[i]))
    
    return main_models, outlier_models

# Load models
main_models, outlier_models = load_models()

if not main_models or not outlier_models:
    print('Error: Models not found. Run training first.', file=sys.stderr)
    sys.exit(1)

# Load private test cases
with open('private_cases.json', 'r') as f:
    data = json.load(f)

print(f'Processing {len(data)} private cases...', file=sys.stderr)

# Convert to DataFrame
df = pd.DataFrame(data)
df.rename(columns={
    'trip_duration_days': 'trip_duration_days',
    'miles_traveled': 'miles_traveled', 
    'total_receipts_amount': 'total_receipts_amount'
}, inplace=True)

# Feature engineering
features_df = feature_engineering(df[['trip_duration_days', 'miles_traveled', 'total_receipts_amount']].copy())

# Split into main and outlier cases
outlier_mask = df['total_receipts_amount'] > OUTLIER_THRESHOLD
main_cases = features_df[~outlier_mask]
outlier_cases = features_df[outlier_mask]

# Initialize results array
predictions = np.zeros(len(df))

# Batch predict main cases
if len(main_cases) > 0:
    print(f'Processing {len(main_cases)} main cases...', file=sys.stderr)
    main_features = main_models[0].feature_names_in_
    main_data = main_cases.reindex(columns=main_features, fill_value=0)
    main_predictions = np.zeros((len(main_cases), len(main_models)))
    for i, model in enumerate(main_models):
        main_predictions[:, i] = model.predict(main_data)
    predictions[~outlier_mask] = np.mean(main_predictions, axis=1)

# Batch predict outlier cases
if len(outlier_cases) > 0:
    print(f'Processing {len(outlier_cases)} outlier cases...', file=sys.stderr)
    outlier_features = outlier_models[0].feature_names_in_
    outlier_data = outlier_cases.reindex(columns=outlier_features, fill_value=0)
    outlier_predictions = np.zeros((len(outlier_cases), len(outlier_models)))
    for i, model in enumerate(outlier_models):
        outlier_predictions[:, i] = model.predict(outlier_data)
    predictions[outlier_mask] = np.mean(outlier_predictions, axis=1)

# Output predictions to match generate_results.sh format
for pred in predictions:
    print(f'{pred:.2f}')
" > private_results.txt

end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc)

echo "⚡ Ultra-fast batch processing completed in ${elapsed} seconds!"
echo

# Verify results
result_lines=$(wc -l < private_results.txt)
echo "✅ Results generated successfully!" >&2
echo "📄 Output saved to private_results.txt ($result_lines lines)" >&2
echo "📊 Each line contains the result for the corresponding test case in private_cases.json" >&2

echo
echo "🚀 Performance Summary:"
echo "  Processing time: ${elapsed} seconds"
echo "  Speed improvement: ~$(echo "scale=0; ($total_cases * 0.9) / $elapsed" | bc)x faster than sequential"
echo "  M1 Optimization: ✅ Vectorized batch processing"
echo

echo "🎯 Next steps:"
echo "  1. Check private_results.txt - it should contain one result per line"
echo "  2. Each line corresponds to the same-numbered test case in private_cases.json"
echo "  3. Submit your private_results.txt file when ready!" 