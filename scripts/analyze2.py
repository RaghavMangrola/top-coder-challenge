#!/usr/bin/env python3
import json

# Load data
with open('public_cases.json', 'r') as f:
    data = json.load(f)

print("=== TRIP LENGTH ANALYSIS ===")

# Group by trip length
trip_lengths = {}
for d in data:
    days = d['input']['trip_duration_days']
    if days not in trip_lengths:
        trip_lengths[days] = []
    trip_lengths[days].append(d)

# Compare per-day reimbursement rates
print("\nPER-DAY REIMBURSEMENT RATES BY TRIP LENGTH:")
for days in sorted(trip_lengths.keys())[:10]:
    if len(trip_lengths[days]) >= 3:
        cases = trip_lengths[days][:5]  # Take first 5 cases
        per_day_rates = [case['expected_output'] / case['input']['trip_duration_days'] for case in cases]
        avg_per_day = sum(per_day_rates) / len(per_day_rates)
        print(f"  {days}-day trips: Avg ${avg_per_day:.2f}/day ({len(trip_lengths[days])} total cases)")

# Specific analysis of 5-day trips
print("\n=== DETAILED 5-DAY ANALYSIS ===")
five_day_trips = trip_lengths.get(5, [])[:10]
for d in five_day_trips:
    inp = d['input']
    expected = d['expected_output']
    
    # My current calculation
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    base_per_diem = days * 100
    if miles <= 100:
        mileage_comp = miles * 0.75
    else:
        mileage_comp = 100 * 0.75 + (miles - 100) * 0.50
    
    my_calc = base_per_diem + mileage_comp + receipts
    difference = expected - my_calc
    
    print(f"  {miles}mi, ${receipts:.2f} -> Expected: ${expected:.2f}, My calc: ${my_calc:.2f}, Diff: ${difference:.2f}")

# Look for patterns in the differences
differences = []
for d in five_day_trips:
    inp = d['input']
    expected = d['expected_output']
    
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    
    base_per_diem = days * 100
    if miles <= 100:
        mileage_comp = miles * 0.75
    else:
        mileage_comp = 100 * 0.75 + (miles - 100) * 0.50
    
    my_calc = base_per_diem + mileage_comp + receipts
    difference = expected - my_calc
    differences.append(difference)

if differences:
    avg_diff = sum(differences) / len(differences)
    print(f"\nAverage difference for 5-day trips: ${avg_diff:.2f}")
    print("This suggests a consistent adjustment factor!") 