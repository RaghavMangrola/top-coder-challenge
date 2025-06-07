#!/usr/bin/env python3
import json
import subprocess
import statistics

# Load test cases
with open('public_cases.json', 'r') as f:
    data = json.load(f)

# Test first 50 cases for quick evaluation
test_cases = data[:50]

print("Quick Multi-Model Evaluation (50 cases)")
print("="*50)

errors_advanced = []
errors_breakthrough = []

for i, case in enumerate(test_cases):
    inp = case['input']
    expected = case['expected_output']
    
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    # Test advanced multi-model
    try:
        result_advanced = subprocess.run([
            'python3', 'calculate_advanced_multi.py', 
            str(days), str(miles), str(receipts)
        ], capture_output=True, text=True, timeout=5)
        
        if result_advanced.returncode == 0:
            pred_advanced = float(result_advanced.stdout.strip())
            error_advanced = abs(pred_advanced - expected)
            errors_advanced.append(error_advanced)
        else:
            print(f"Error in advanced model for case {i}")
            errors_advanced.append(1000)  # Large penalty for errors
    
    except Exception as e:
        print(f"Exception in advanced model for case {i}: {e}")
        errors_advanced.append(1000)
    
    # Test breakthrough model
    try:
        result_breakthrough = subprocess.run([
            'python3', 'calculate_fast.py', 
            str(days), str(miles), str(receipts)
        ], capture_output=True, text=True, timeout=5)
        
        if result_breakthrough.returncode == 0:
            pred_breakthrough = float(result_breakthrough.stdout.strip())
            error_breakthrough = abs(pred_breakthrough - expected)
            errors_breakthrough.append(error_breakthrough)
        else:
            print(f"Error in breakthrough model for case {i}")
            errors_breakthrough.append(1000)
    
    except Exception as e:
        print(f"Exception in breakthrough model for case {i}: {e}")
        errors_breakthrough.append(1000)

# Calculate results
if errors_advanced and errors_breakthrough:
    avg_error_advanced = statistics.mean(errors_advanced)
    avg_error_breakthrough = statistics.mean(errors_breakthrough)
    
    score_advanced = sum(errors_advanced)
    score_breakthrough = sum(errors_breakthrough)
    
    print(f"\nResults on {len(test_cases)} test cases:")
    print(f"Advanced Multi-Model:")
    print(f"  Average Error: ${avg_error_advanced:.2f}")
    print(f"  Score: {score_advanced:.2f}")
    
    print(f"\nBreakthrough Model:")
    print(f"  Average Error: ${avg_error_breakthrough:.2f}")
    print(f"  Score: {score_breakthrough:.2f}")
    
    improvement = (score_breakthrough - score_advanced) / score_breakthrough * 100
    print(f"\nImprovement: {improvement:.1f}%")
    
    if improvement > 0:
        print("✅ Advanced multi-model is BETTER!")
    else:
        print("❌ Breakthrough model is still better")
else:
    print("Error: Could not evaluate models") 