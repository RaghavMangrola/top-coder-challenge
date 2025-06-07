import json
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
import joblib
import sys
import os

MAIN_MODEL_FILE = 'main_model_fast.joblib'
OUTLIER_MODEL_FILE = 'outlier_model_fast.joblib'
DATA_FILE = 'public_cases.json'
OUTLIER_THRESHOLD = 1400

def simple_feature_engineering(days, miles, receipts):
    """
    Simplified feature engineering for single predictions - optimized for speed
    """
    # Basic calculations
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    # 4-day bonus
    four_day_bonus = 150 if days == 4 else 0
    
    # Receipt multiplier (simplified logic)
    if days == 1:
        receipt_multiplier = -0.5
    elif days == 5:
        receipt_multiplier = 1.04
    elif days >= 8:
        receipt_multiplier = 0.02
    else:
        receipt_multiplier = 1.0
    
    # Receipt cap
    adjusted_receipts = receipts * 0.25 if receipts > 2000 else receipts
    multiplied_receipts = adjusted_receipts * receipt_multiplier
    
    # 3-tier mileage
    miles_tier1 = min(miles, 100)
    miles_tier2 = max(0, min(miles - 100, 400))
    miles_tier3 = max(0, miles - 500)
    
    # Efficiency bonus
    efficiency_bonus_range = 1 if 180 <= miles_per_day <= 220 else 0
    
    # Trip categories (simplified)
    if days <= 2 and miles_per_day > 150:
        cat_quick_trip_high_miles = 1
        cat_long_haul = cat_low_efficiency = cat_sweet_spot_efficiency = cat_balanced = 0
    elif days >= 8:
        cat_long_haul = 1
        cat_quick_trip_high_miles = cat_low_efficiency = cat_sweet_spot_efficiency = cat_balanced = 0
    elif miles_per_day < 50:
        cat_low_efficiency = 1
        cat_quick_trip_high_miles = cat_long_haul = cat_sweet_spot_efficiency = cat_balanced = 0
    elif 180 <= miles_per_day <= 220:
        cat_sweet_spot_efficiency = 1
        cat_quick_trip_high_miles = cat_long_haul = cat_low_efficiency = cat_balanced = 0
    else:
        cat_balanced = 1
        cat_quick_trip_high_miles = cat_long_haul = cat_low_efficiency = cat_sweet_spot_efficiency = 0
    
    # Interaction features
    days_x_miles = days * miles
    
    # Return as list in correct order
    return [
        days, miles, receipts, miles_per_day, receipts_per_day, four_day_bonus,
        receipt_multiplier, adjusted_receipts, multiplied_receipts,
        miles_tier1, miles_tier2, miles_tier3, efficiency_bonus_range, days_x_miles,
        cat_balanced, cat_long_haul, cat_low_efficiency, 
        cat_quick_trip_high_miles, cat_sweet_spot_efficiency
    ]

def train_fast_model():
    """
    Train lighter, faster models with reduced complexity
    """
    print("Training fast models...", file=sys.stderr)
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    # Convert to simple lists for faster processing
    main_X = []
    main_y = []
    outlier_X = []
    outlier_y = []
    
    for case in data:
        inp = case['input']
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        expected = case['expected_output']
        
        features = simple_feature_engineering(days, miles, receipts)
        
        if receipts > OUTLIER_THRESHOLD:
            outlier_X.append(features)
            outlier_y.append(expected)
        else:
            main_X.append(features)
            main_y.append(expected)
    
    # Train lighter models (reduced complexity for speed)
    main_model = DecisionTreeRegressor(random_state=42, max_depth=8, min_samples_leaf=5)
    main_model.fit(main_X, main_y)
    joblib.dump(main_model, MAIN_MODEL_FILE)
    
    outlier_model = DecisionTreeRegressor(random_state=42, max_depth=6, min_samples_leaf=3)
    outlier_model.fit(outlier_X, outlier_y)
    joblib.dump(outlier_model, OUTLIER_MODEL_FILE)
    
    print(f"Fast models trained and saved", file=sys.stderr)

# Load models once at import time for speed
main_model = None
outlier_model = None

def load_models():
    global main_model, outlier_model
    if main_model is None or outlier_model is None:
        if not os.path.exists(MAIN_MODEL_FILE) or not os.path.exists(OUTLIER_MODEL_FILE):
            train_fast_model()
        main_model = joblib.load(MAIN_MODEL_FILE)
        outlier_model = joblib.load(OUTLIER_MODEL_FILE)

def predict_fast(days, miles, receipts):
    """
    Fast prediction using pre-loaded models and simplified feature engineering
    """
    load_models()
    
    # Choose model based on receipt threshold
    model = outlier_model if receipts > OUTLIER_THRESHOLD else main_model
    
    # Generate features quickly
    features = simple_feature_engineering(days, miles, receipts)
    
    # Make prediction
    prediction = model.predict([features])
    print(f"{prediction[0]:.2f}")

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'train':
        train_fast_model()
    elif len(sys.argv) == 4:
        try:
            days = int(sys.argv[1])
            miles = float(sys.argv[2])
            receipts = float(sys.argv[3])
            predict_fast(days, miles, receipts)
        except ValueError:
            print("Error: Invalid input. Please provide numeric values for days, miles, and receipts.")
            sys.exit(1)
    else:
        print("Usage:")
        print("  To train the model: python3 calculate_fast.py train")
        print("  To make a prediction: python3 calculate_fast.py <days> <miles> <receipts>")
        sys.exit(1) 