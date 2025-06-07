import json
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
import joblib
import sys
import os

# Model files - keeping the successful two-model architecture but adding specialization
MAIN_MODEL_FILE = 'main_model_fast.joblib'
OUTLIER_MODEL_FILE = 'outlier_model_fast.joblib'
SHORT_TRIP_MODEL_FILE = 'short_specialized.joblib'
LONG_TRIP_MODEL_FILE = 'long_specialized.joblib'
DATA_FILE = 'public_cases.json'
OUTLIER_THRESHOLD = 1400

def feature_engineering(df):
    """
    Exact feature engineering from breakthrough model - maintaining accuracy
    """
    # Basic ratios
    df['miles_per_day'] = df['miles_traveled'] / df['trip_duration_days']
    df['receipts_per_day'] = df['total_receipts_amount'] / df['trip_duration_days']
    
    # Handle potential division by zero
    df.fillna(0, inplace=True)

    # Add 4-day trip bonus (from breakthrough)
    df['four_day_bonus'] = (df['trip_duration_days'] == 4).astype(int) * 150

    # Advanced Receipt Multiplier (exact from breakthrough)
    def get_receipt_multiplier(days):
        if days == 1:
            return -0.5  # Heavy penalty
        if days == 5:
            return 1.04  # Full reimbursement
        if days >= 8:
            return 0.02  # Heavy penalty
        return 1.0 # Default

    df['receipt_multiplier'] = df['trip_duration_days'].apply(get_receipt_multiplier)
    
    # Apply receipt amount cap insight (exact from breakthrough)
    df['adjusted_receipts'] = df.apply(
        lambda row: row['total_receipts_amount'] * 0.25 if row['total_receipts_amount'] > 2000 else row['total_receipts_amount'],
        axis=1
    )
    # Apply the multiplier
    df['multiplied_receipts'] = df['adjusted_receipts'] * df['receipt_multiplier']

    # Refined 3-Tier Mileage System (exact from breakthrough)
    df['miles_tier1'] = df['miles_traveled'].clip(upper=100)
    df['miles_tier2'] = (df['miles_traveled'] - 100).clip(lower=0, upper=400)
    df['miles_tier3'] = (df['miles_traveled'] - 500).clip(lower=0)
    
    # Efficiency bonus sweet spot (exact from breakthrough)
    df['efficiency_bonus_range'] = ((df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)).astype(int)

    # Trip Category Feature (Kevin's "6 Paths" Theory - exact from breakthrough)
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
    
    # One-hot encode the trip categories (exact from breakthrough)
    df = pd.get_dummies(df, columns=['trip_category'], prefix='cat')

    # Interaction features (exact from breakthrough)
    df['days_x_miles'] = df['trip_duration_days'] * df['miles_traveled']
    
    return df

def train_advanced_multi_models():
    """
    Train the breakthrough model + specialized models for extreme cases
    """
    print("Training advanced multi-model system...", file=sys.stderr)
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    df.rename(columns={
        'input.trip_duration_days': 'trip_duration_days',
        'input.miles_traveled': 'miles_traveled',
        'input.total_receipts_amount': 'total_receipts_amount',
        'expected_output': 'expected_reimbursement'
    }, inplace=True)

    # Separate data like the breakthrough model
    outlier_df = df[df['total_receipts_amount'] > OUTLIER_THRESHOLD]
    main_df = df[df['total_receipts_amount'] <= OUTLIER_THRESHOLD]

    # Feature engineering for both datasets
    main_features = feature_engineering(main_df.drop('expected_reimbursement', axis=1))
    outlier_features = feature_engineering(outlier_df.drop('expected_reimbursement', axis=1))
    
    X_main = main_features
    y_main = main_df['expected_reimbursement']
    
    X_outlier = outlier_features
    y_outlier = outlier_df['expected_reimbursement']

    # Train the main models (exact from breakthrough)
    main_model = DecisionTreeRegressor(random_state=42, max_depth=12, min_samples_leaf=3)
    main_model.fit(X_main, y_main)
    joblib.dump(main_model, MAIN_MODEL_FILE)
    print(f"Main model trained: {len(main_df)} cases", file=sys.stderr)

    outlier_model = DecisionTreeRegressor(random_state=42, max_depth=8, min_samples_leaf=2)
    outlier_model.fit(X_outlier, y_outlier)
    joblib.dump(outlier_model, OUTLIER_MODEL_FILE)
    print(f"Outlier model trained: {len(outlier_df)} cases", file=sys.stderr)

    # Add specialized models for extreme trip lengths
    # Short trips (1-2 days) - often have different logic
    short_df = df[df['trip_duration_days'] <= 2]
    if len(short_df) >= 20:
        short_features = feature_engineering(short_df.drop('expected_reimbursement', axis=1))
        short_model = DecisionTreeRegressor(random_state=42, max_depth=10, min_samples_leaf=2)
        short_model.fit(short_features, short_df['expected_reimbursement'])
        joblib.dump(short_model, SHORT_TRIP_MODEL_FILE)
        print(f"Short trip specialist trained: {len(short_df)} cases", file=sys.stderr)

    # Long trips (8+ days) - also have different logic
    long_df = df[df['trip_duration_days'] >= 8]
    if len(long_df) >= 20:
        long_features = feature_engineering(long_df.drop('expected_reimbursement', axis=1))
        long_model = DecisionTreeRegressor(random_state=42, max_depth=10, min_samples_leaf=2)
        long_model.fit(long_features, long_df['expected_reimbursement'])
        joblib.dump(long_model, LONG_TRIP_MODEL_FILE)
        print(f"Long trip specialist trained: {len(long_df)} cases", file=sys.stderr)

# Load models once for speed
models = {}

def load_models():
    global models
    if not models:
        if not os.path.exists(MAIN_MODEL_FILE) or not os.path.exists(OUTLIER_MODEL_FILE):
            train_advanced_multi_models()
        
        models['main'] = joblib.load(MAIN_MODEL_FILE)
        models['outlier'] = joblib.load(OUTLIER_MODEL_FILE)
        
        # Load specialist models if available
        if os.path.exists(SHORT_TRIP_MODEL_FILE):
            models['short_specialist'] = joblib.load(SHORT_TRIP_MODEL_FILE)
        if os.path.exists(LONG_TRIP_MODEL_FILE):
            models['long_specialist'] = joblib.load(LONG_TRIP_MODEL_FILE)

def predict_advanced_multi(days, miles, receipts):
    """
    Advanced prediction using the breakthrough model + specialists
    """
    load_models()
    
    # Create input DataFrame exactly like breakthrough model
    input_data = {
        'trip_duration_days': [days],
        'miles_traveled': [miles],
        'total_receipts_amount': [receipts]
    }
    input_df = pd.DataFrame(input_data)
    
    # Apply exact feature engineering from breakthrough
    input_features = feature_engineering(input_df)
    
    # Primary model selection (breakthrough logic)
    if receipts > OUTLIER_THRESHOLD:
        primary_model = models['outlier']
    else:
        primary_model = models['main']
    
    # Ensure columns match the training set
    training_cols = primary_model.feature_names_in_
    input_features = input_features.reindex(columns=training_cols, fill_value=0)
    
    primary_prediction = primary_model.predict(input_features)[0]
    
    # Check if we should use specialist models
    predictions = [primary_prediction]
    weights = [0.8]  # Primary model gets most weight
    
    # Use short trip specialist for 1-2 day trips
    if days <= 2 and 'short_specialist' in models:
        specialist_pred = models['short_specialist'].predict(input_features)[0]
        predictions.append(specialist_pred)
        weights.append(0.2)
    
    # Use long trip specialist for 8+ day trips  
    elif days >= 8 and 'long_specialist' in models:
        specialist_pred = models['long_specialist'].predict(input_features)[0]
        predictions.append(specialist_pred)
        weights.append(0.2)
    
    # Weighted ensemble
    if len(predictions) > 1:
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        final_prediction = sum(p * w for p, w in zip(predictions, normalized_weights))
    else:
        final_prediction = primary_prediction
    
    print(f"{final_prediction:.2f}")

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'train':
        train_advanced_multi_models()
    elif len(sys.argv) == 4:
        try:
            days = int(sys.argv[1])
            miles = float(sys.argv[2])
            receipts = float(sys.argv[3])
            predict_advanced_multi(days, miles, receipts)
        except ValueError:
            print("Error: Invalid input. Please provide numeric values for days, miles, and receipts.")
            sys.exit(1)
    else:
        print("Usage:")
        print("  To train models: python3 calculate_advanced_multi.py train")
        print("  To predict: python3 calculate_advanced_multi.py <days> <miles> <receipts>")
        sys.exit(1) 