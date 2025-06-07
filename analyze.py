#!/usr/bin/env python3
import json

# Load data
with open('public_cases.json', 'r') as f:
    data = json.load(f)

print("=== REVISED PATTERN ANALYSIS ===")

# Test different base per diem rates
print("\n1. TESTING DIFFERENT BASE RATES:")
test_cases = data[:5]
for base_rate in [50, 60, 70, 80, 90, 100, 110, 120]:
    errors = []
    for d in test_cases:
        inp = d['input']
        expected = d['expected_output']
        # Test: base_rate * days + miles * 0.58
        calc = base_rate * inp['trip_duration_days'] + inp['miles_traveled'] * 0.58
        error = abs(expected - calc)
        errors.append(error)
    avg_error = sum(errors) / len(errors)
    print(f"  Base rate ${base_rate}/day: Avg error ${avg_error:.2f}")

# Look at receipt patterns - maybe they're penalties?
print(f"\n2. RECEIPT ANALYSIS - testing if receipts are penalties:")
sample_cases = data[:10]
for d in sample_cases:
    inp = d['input']
    expected = d['expected_output']
    
    # Test different receipt treatments
    base_calc = 85 * inp['trip_duration_days'] + inp['miles_traveled'] * 0.5  # rough approximation
    
    # Option 1: Receipts added
    option1 = base_calc + inp['total_receipts_amount']
    
    # Option 2: Receipts subtracted (penalty)
    option2 = base_calc - inp['total_receipts_amount']
    
    # Option 3: Receipt penalty based on percentage
    option3 = base_calc - (inp['total_receipts_amount'] * 0.5)
    
    error1 = abs(expected - option1)
    error2 = abs(expected - option2)
    error3 = abs(expected - option3)
    
    print(f"  {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f} -> ${expected:.2f}")
    print(f"    +receipts: ${option1:.2f} (err: ${error1:.2f}), -receipts: ${option2:.2f} (err: ${error2:.2f}), -50%receipts: ${option3:.2f} (err: ${error3:.2f})")

# Look for mileage tiers
print(f"\n3. MILEAGE TIER ANALYSIS:")
one_day_trips = [d for d in data if d['input']['trip_duration_days'] == 1 and d['input']['total_receipts_amount'] < 50][:10]
for d in one_day_trips:
    inp = d['input']
    expected = d['expected_output']
    
    # Assume base per diem of ~85 and see what mileage rate fits
    remaining = expected - 85 - inp['total_receipts_amount']  # if receipts are added
    remaining2 = expected - 85 + inp['total_receipts_amount']  # if receipts are subtracted
    
    rate1 = remaining / inp['miles_traveled'] if inp['miles_traveled'] > 0 else 0
    rate2 = remaining2 / inp['miles_traveled'] if inp['miles_traveled'] > 0 else 0
    
    print(f"  {inp['miles_traveled']} miles, ${inp['total_receipts_amount']:.2f} -> ${expected:.2f}")
    print(f"    If +receipts: rate ${rate1:.3f}/mi, If -receipts: rate ${rate2:.3f}/mi") 