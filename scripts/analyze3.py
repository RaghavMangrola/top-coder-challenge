#!/usr/bin/env python3
import json

# Load data
with open('public_cases.json', 'r') as f:
    data = json.load(f)

print("=== RECEIPT PATTERN ANALYSIS ===")

# Look at high receipt cases
high_receipt_cases = [d for d in data if d['input']['total_receipts_amount'] > 1000]
print(f"\nHIGH RECEIPT CASES (>$1000): {len(high_receipt_cases)} cases")

for d in high_receipt_cases[:10]:
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
    
    # 5-day adjustment
    adjustment = -400 if days == 5 else 0
    
    my_calc = base_per_diem + mileage_comp + receipts + adjustment
    difference = expected - my_calc
    
    # What would the receipt component need to be?
    needed_receipt_comp = expected - base_per_diem - mileage_comp - adjustment
    receipt_ratio = needed_receipt_comp / receipts if receipts > 0 else 0
    
    print(f"  {days}d, {miles:.0f}mi, ${receipts:.2f} -> Expected: ${expected:.2f}")
    print(f"    My calc: ${my_calc:.2f}, Diff: ${difference:.2f}")
    print(f"    Needed receipt comp: ${needed_receipt_comp:.2f} (ratio: {receipt_ratio:.3f})")
    print()

# Look at receipt ratios by trip length
print("\nRECEIPT TREATMENT BY TRIP LENGTH:")
trip_lengths = {}
for d in data:
    days = d['input']['trip_duration_days']
    if days not in trip_lengths:
        trip_lengths[days] = []
    trip_lengths[days].append(d)

for days in sorted(trip_lengths.keys())[:10]:
    if len(trip_lengths[days]) >= 5:
        cases = trip_lengths[days][:10]
        receipt_ratios = []
        
        for d in cases:
            inp = d['input']
            expected = d['expected_output']
            
            base_per_diem = days * 100
            miles = inp['miles_traveled']
            if miles <= 100:
                mileage_comp = miles * 0.75
            else:
                mileage_comp = 100 * 0.75 + (miles - 100) * 0.50
            
            adjustment = -400 if days == 5 else 0
            needed_receipt_comp = expected - base_per_diem - mileage_comp - adjustment
            
            if inp['total_receipts_amount'] > 0:
                ratio = needed_receipt_comp / inp['total_receipts_amount']
                receipt_ratios.append(ratio)
        
        if receipt_ratios:
            avg_ratio = sum(receipt_ratios) / len(receipt_ratios)
            print(f"  {days}-day trips: Avg receipt ratio {avg_ratio:.3f} (1.0 = full reimbursement)")

# Look for receipt caps
print(f"\nRECEIPT CAP ANALYSIS:")
print("Looking for patterns where receipts might be capped...")

# Group by receipt ranges
receipt_ranges = [
    (0, 100, "Low"),
    (100, 500, "Medium"), 
    (500, 1000, "High"),
    (1000, 2000, "Very High"),
    (2000, 5000, "Extreme")
]

for min_r, max_r, label in receipt_ranges:
    range_cases = [d for d in data if min_r <= d['input']['total_receipts_amount'] < max_r]
    if len(range_cases) >= 5:
        ratios = []
        for d in range_cases[:20]:  # Sample 20 cases
            inp = d['input']
            expected = d['expected_output']
            
            days = inp['trip_duration_days']
            miles = inp['miles_traveled']
            base_per_diem = days * 100
            if miles <= 100:
                mileage_comp = miles * 0.75
            else:
                mileage_comp = 100 * 0.75 + (miles - 100) * 0.50
            
            adjustment = -400 if days == 5 else 0
            needed_receipt_comp = expected - base_per_diem - mileage_comp - adjustment
            
            if inp['total_receipts_amount'] > 0:
                ratio = needed_receipt_comp / inp['total_receipts_amount']
                ratios.append(ratio)
        
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            print(f"  {label} receipts (${min_r}-${max_r}): Avg ratio {avg_ratio:.3f} ({len(range_cases)} cases)") 