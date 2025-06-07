import json
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
import joblib
import sys
import os
import numpy as np

# Ensemble configuration
ENSEMBLE_SIZE = 5
MAIN_MODEL_FILES = [f'ensemble_main_{i}.joblib' for i in range(ENSEMBLE_SIZE)]
OUTLIER_MODEL_FILES = [f'ensemble_outlier_{i}.joblib' for i in range(ENSEMBLE_SIZE)]
RANDOM_SEEDS = [42, 123, 456, 789, 999]  # Different seeds for ensemble diversity

DATA_FILE = 'public_cases.json'
OUTLIER_THRESHOLD = 1400

def feature_engineering(df):
    """
    Engineers features from the raw input data.
    The insights from IMPLEMENTATION_LOG.md and FUTURE_APPROACHES.md are used here.
    """
    # Basic ratios
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Handle potential division by zero if trip_duration_days is 0
    df.fillna(0, inplace=True)

    # Add 4-day trip bonus (from FUTURE_APPROACHES.md)
    df['four_day_bonus'] = (df['trip_duration_days'] == 4).astype(int) * 150 # Add a $150 bonus

    # Advanced Receipt Multiplier (from FUTURE_APPROACHES.md)
    def get_receipt_multiplier(days):
        if days == 1:
            return -0.5  # Heavy penalty
        if days == 5:
            return 1.04  # Full reimbursement
        if days >= 8:
            return 0.02  # Heavy penalty
        return 1.0 # Default

    df['receipt_multiplier'] = df['trip_duration_days'].apply(get_receipt_multiplier)
    
    # Apply receipt amount cap insight
    df['adjusted_receipts'] = df.apply(
        lambda row: row['total_receipts_amount'] * 0.25 if row['total_receipts_amount'] > 2000 else row['total_receipts_amount'],
        axis=1
    )
    # Apply the multiplier
    df['multiplied_receipts'] = df['adjusted_receipts'] * df['receipt_multiplier']

    # Refined 3-Tier Mileage System
    df['miles_tier1'] = df['miles_traveled'].clip(upper=100)
    df['miles_tier2'] = (df['miles_traveled'] - 100).clip(lower=0, upper=400) # 100-500
    df['miles_tier3'] = (df['miles_traveled'] - 500).clip(lower=0)
    
    # Efficiency bonus sweet spot (based on insights)
    df['efficiency_bonus_range'] = ((df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)).astype(int)

    # Trip Category Feature (Kevin's "6 Paths" Theory)
    def get_trip_category(row):
        days = row['trip_duration_days']
        miles_per_day = row['miles_per_day']
        if days <= 2 and miles_per_day > 150:
            return 'quick_trip_high_miles'
        if days >= 8:
            return 'long_haul'
        if miles_per_day < 50:
            return 'low_efficiency'
        if 180 <= miles_per_day <= 220:
            return 'sweet_spot_efficiency'
        return 'balanced'

    df['trip_category'] = df.apply(get_trip_category, axis=1)
    
    # One-hot encode the trip categories
    df = pd.get_dummies(df, columns=['trip_category'], prefix='cat')

    # Interaction features
    df['days_x_miles'] = df['trip_duration_days'] * df['miles_traveled']
    
    # Drop old flags that are now replaced by the multiplier logic
    # df.drop(['is_1_day_trip', 'is_5_day_trip', 'is_long_trip', 'receipt_cap_triggered'], axis=1, inplace=True, errors='ignore')

    return df

def train_model():
    """
    Loads data, engineers features, splits data into main and outlier sets,
    trains ensemble of Decision Tree Regressors with different random seeds, and saves them.
    """
    print("Training ensemble of main and outlier models...", file=sys.stderr)
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    df.rename(columns={
        'input.trip_duration_days': 'trip_duration_days',
        'input.miles_traveled': 'miles_traveled',
        'input.total_receipts_amount': 'total_receipts_amount',
        'expected_output': 'expected_reimbursement'
    }, inplace=True)

    # Separate data into main and outlier sets
    outlier_df = df[df['total_receipts_amount'] > OUTLIER_THRESHOLD]
    main_df = df[df['total_receipts_amount'] <= OUTLIER_THRESHOLD]

    # Feature engineering for both datasets
    main_features = feature_engineering(main_df.drop('expected_reimbursement', axis=1))
    outlier_features = feature_engineering(outlier_df.drop('expected_reimbursement', axis=1))
    
    X_main = main_features
    y_main = main_df['expected_reimbursement']
    
    X_outlier = outlier_features
    y_outlier = outlier_df['expected_reimbursement']

    # Train ensemble of main models
    print(f"Training {ENSEMBLE_SIZE} main models...", file=sys.stderr)
    for i, seed in enumerate(RANDOM_SEEDS):
        main_model = DecisionTreeRegressor(random_state=seed, max_depth=12, min_samples_leaf=3)
        main_model.fit(X_main, y_main)
        joblib.dump(main_model, MAIN_MODEL_FILES[i])
        print(f"Main model {i+1}/{ENSEMBLE_SIZE} trained with seed {seed}", file=sys.stderr)

    # Train ensemble of outlier models
    print(f"Training {ENSEMBLE_SIZE} outlier models...", file=sys.stderr)
    for i, seed in enumerate(RANDOM_SEEDS):
        outlier_model = DecisionTreeRegressor(random_state=seed, max_depth=8, min_samples_leaf=2)
        outlier_model.fit(X_outlier, y_outlier)
        joblib.dump(outlier_model, OUTLIER_MODEL_FILES[i])
        print(f"Outlier model {i+1}/{ENSEMBLE_SIZE} trained with seed {seed}", file=sys.stderr)

    print("Ensemble training complete!", file=sys.stderr)

def predict(days, miles, receipts):
    """
    Loads the appropriate ensemble of trained models and makes averaged prediction.
    """
    # Check if any ensemble models exist
    main_models_exist = all(os.path.exists(f) for f in MAIN_MODEL_FILES)
    outlier_models_exist = all(os.path.exists(f) for f in OUTLIER_MODEL_FILES)
    
    if not main_models_exist or not outlier_models_exist:
        train_model()
    
    # Decide which ensemble to use
    if receipts > OUTLIER_THRESHOLD:
        model_files = OUTLIER_MODEL_FILES
    else:
        model_files = MAIN_MODEL_FILES
    
    # Load ensemble models
    models = [joblib.load(f) for f in model_files]
    
    # Create a DataFrame for the input
    input_data = {
        'trip_duration_days': [days],
        'miles_traveled': [miles],
        'total_receipts_amount': [receipts]
    }
    input_df = pd.DataFrame(input_data)
    
    # Apply the same feature engineering
    input_features = feature_engineering(input_df)
    
    # Make predictions with all models in ensemble
    predictions = []
    for model in models:
        # Ensure columns match the training set
        training_cols = model.feature_names_in_
        model_features = input_features.reindex(columns=training_cols, fill_value=0)
        pred = model.predict(model_features)[0]
        predictions.append(pred)
    
    # Average the ensemble predictions
    ensemble_prediction = np.mean(predictions)
    print(f"{ensemble_prediction:.2f}")


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'train':
        train_model()
    elif len(sys.argv) == 4:
        try:
            days = int(sys.argv[1])
            miles = float(sys.argv[2]) # Allow float for miles as per insights
            receipts = float(sys.argv[3])
            predict(days, miles, receipts)
        except ValueError:
            print("Error: Invalid input. Please provide numeric values for days, miles, and receipts.")
            sys.exit(1)
    else:
        print("Usage:")
        print("  To train the model: python3 calculate.py train")
        print("  To make a prediction: python3 calculate.py <days> <miles> <receipts>")
        sys.exit(1) 