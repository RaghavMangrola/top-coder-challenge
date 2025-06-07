#!/usr/bin/env python3
"""
Ultra-fast batch calculator that processes all 1000 cases at once.
Optimized for M1 MacBook with vectorized operations and single model loading.
"""

import json
import pandas as pd
import numpy as np
import joblib
import sys
import os
from pathlib import Path

# Ensemble configuration
ENSEMBLE_SIZE = 5
MAIN_MODEL_FILES = [f'ensemble_main_{i}.joblib' for i in range(ENSEMBLE_SIZE)]
OUTLIER_MODEL_FILES = [f'ensemble_outlier_{i}.joblib' for i in range(ENSEMBLE_SIZE)]
OUTLIER_THRESHOLD = 1400

def feature_engineering(df):
    """Vectorized feature engineering for entire dataset"""
    # Basic ratios
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Handle potential division by zero
    df.fillna(0, inplace=True)

    # Add 4-day trip bonus
    df['four_day_bonus'] = (df['trip_duration_days'] == 4).astype(int) * 150

    # Advanced Receipt Multiplier (vectorized)
    conditions = [
        (df['trip_duration_days'] == 1),
        (df['trip_duration_days'] == 5),
        (df['trip_duration_days'] >= 8)
    ]
    choices = [-0.5, 1.04, 0.02]
    df['receipt_multiplier'] = np.select(conditions, choices, default=1.0)
    
    # Apply receipt amount cap
    df['adjusted_receipts'] = np.where(
        df['total_receipts_amount'] > 2000, 
        df['total_receipts_amount'] * 0.25, 
        df['total_receipts_amount']
    )
    df['multiplied_receipts'] = df['adjusted_receipts'] * df['receipt_multiplier']

    # 3-Tier Mileage System (vectorized)
    df['miles_tier1'] = np.clip(df['miles_traveled'], 0, 100)
    df['miles_tier2'] = np.clip(df['miles_traveled'] - 100, 0, 400)
    df['miles_tier3'] = np.clip(df['miles_traveled'] - 500, 0, None)
    
    # Efficiency bonus sweet spot
    df['efficiency_bonus_range'] = (
        (df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)
    ).astype(int)

    # Trip Category Feature (vectorized)
    conditions = [
        (df['trip_duration_days'] <= 2) & (df['miles_per_day'] > 150),
        (df['trip_duration_days'] >= 8),
        (df['miles_per_day'] < 50),
        (df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)
    ]
    choices = ['quick_trip_high_miles', 'long_haul', 'low_efficiency', 'sweet_spot_efficiency']
    df['trip_category'] = np.select(conditions, choices, default='balanced')
    
    # One-hot encode categories
    df = pd.get_dummies(df, columns=['trip_category'], prefix='cat')

    # Interaction features
    df['days_x_miles'] = df['trip_duration_days'] * df['miles_traveled']
    
    return df

def load_models():
    """Load all models once and return dictionaries"""
    print("Loading ensemble models...", file=sys.stderr)
    
    main_models = []
    outlier_models = []
    
    for i in range(ENSEMBLE_SIZE):
        if os.path.exists(MAIN_MODEL_FILES[i]):
            main_models.append(joblib.load(MAIN_MODEL_FILES[i]))
        if os.path.exists(OUTLIER_MODEL_FILES[i]):
            outlier_models.append(joblib.load(OUTLIER_MODEL_FILES[i]))
    
    print(f"Loaded {len(main_models)} main models and {len(outlier_models)} outlier models", file=sys.stderr)
    return main_models, outlier_models

def batch_predict(cases_file='public_cases.json'):
    """Process all cases in a single batch operation"""
    
    # Load all models once
    main_models, outlier_models = load_models()
    
    if not main_models or not outlier_models:
        print("Error: Models not found. Run training first.", file=sys.stderr)
        sys.exit(1)
    
    # Load test cases
    with open(cases_file, 'r') as f:
        data = json.load(f)
    
    print(f"Processing {len(data)} cases...", file=sys.stderr)
    
    # Convert to DataFrame
    df = pd.json_normalize(data)
    df.rename(columns={
        'input.trip_duration_days': 'trip_duration_days',
        'input.miles_traveled': 'miles_traveled',
        'input.total_receipts_amount': 'total_receipts_amount'
    }, inplace=True)
    
    # Feature engineering for all cases at once
    features_df = feature_engineering(df[['trip_duration_days', 'miles_traveled', 'total_receipts_amount']].copy())
    
    # Split into main and outlier cases
    outlier_mask = df['total_receipts_amount'] > OUTLIER_THRESHOLD
    main_cases = features_df[~outlier_mask]
    outlier_cases = features_df[outlier_mask]
    
    # Initialize results array
    predictions = np.zeros(len(df))
    
    # Batch predict main cases
    if len(main_cases) > 0:
        print(f"Processing {len(main_cases)} main cases...", file=sys.stderr)
        
        # Get common features for main models
        main_features = main_models[0].feature_names_in_
        main_data = main_cases.reindex(columns=main_features, fill_value=0)
        
        # Ensemble prediction for main cases
        main_predictions = np.zeros((len(main_cases), len(main_models)))
        for i, model in enumerate(main_models):
            main_predictions[:, i] = model.predict(main_data)
        
        predictions[~outlier_mask] = np.mean(main_predictions, axis=1)
    
    # Batch predict outlier cases
    if len(outlier_cases) > 0:
        print(f"Processing {len(outlier_cases)} outlier cases...", file=sys.stderr)
        
        # Get common features for outlier models
        outlier_features = outlier_models[0].feature_names_in_
        outlier_data = outlier_cases.reindex(columns=outlier_features, fill_value=0)
        
        # Ensemble prediction for outlier cases
        outlier_predictions = np.zeros((len(outlier_cases), len(outlier_models)))
        for i, model in enumerate(outlier_models):
            outlier_predictions[:, i] = model.predict(outlier_data)
        
        predictions[outlier_mask] = np.mean(outlier_predictions, axis=1)
    
    return predictions

def single_predict(days, miles, receipts):
    """Single case prediction (for compatibility with run.sh)"""
    main_models, outlier_models = load_models()
    
    if receipts > OUTLIER_THRESHOLD:
        models = outlier_models
    else:
        models = main_models
    
    if not models:
        print("Error: Models not found.", file=sys.stderr)
        sys.exit(1)
    
    # Create DataFrame
    input_df = pd.DataFrame({
        'trip_duration_days': [days],
        'miles_traveled': [miles],
        'total_receipts_amount': [receipts]
    })
    
    # Feature engineering
    features_df = feature_engineering(input_df)
    
    # Get model features and predict
    model_features = models[0].feature_names_in_
    input_data = features_df.reindex(columns=model_features, fill_value=0)
    
    # Ensemble prediction
    predictions = [model.predict(input_data)[0] for model in models]
    result = np.mean(predictions)
    
    print(f"{result:.2f}")

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'batch':
        # Batch mode for ultra-fast evaluation
        predictions = batch_predict()
        
        # Output all predictions (for use with modified eval script)
        for pred in predictions:
            print(f"{pred:.2f}")
            
    elif len(sys.argv) == 4:
        # Single prediction mode (for compatibility)
        try:
            days = int(sys.argv[1])
            miles = float(sys.argv[2])
            receipts = float(sys.argv[3])
            single_predict(days, miles, receipts)
        except ValueError:
            print("Error: Invalid input. Please provide numeric values.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage:")
        print("  Batch mode: python3 calculate_ultra_fast.py batch")
        print("  Single prediction: python3 calculate_ultra_fast.py <days> <miles> <receipts>")
        sys.exit(1) 