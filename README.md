# Top Coder Challenge: Black Box Legacy Reimbursement System

## 🚀 Our Solution Overview

### Approaches Implemented

**Machine Learning Approach (Primary Solution)**
We successfully reverse-engineered the legacy system using advanced machine learning with sophisticated feature engineering that achieved a **95% improvement** over naive methods:

- **Initial Score**: 93,192 (naive formula)
- **Final Score**: 4,866 (95% improvement)
- **Average Error**: Reduced from $930 to $47.66

**Key Breakthrough:**
1. **Trip Categorization**: Implemented Kevin's "6 calculation paths" theory using one-hot encoded trip categories
2. **Two-Model Architecture**: Separate specialized models for normal vs high-receipt cases (>$1400 threshold)
3. **Advanced Feature Engineering**: Captured complex business rules from interviews in ML features
4. **Decision Tree Regressor**: With tuned hyperparameters (max_depth=12, min_samples_leaf=3)

**Component-Based KISS Approach (Previous Solution)**
Our initial interpretable approach that laid the foundation:

- **Score**: 25,601 (73% improvement over naive)
- **Average Error**: $255

**Key Discoveries:**
1. **5-Day Trip Penalty**: Major breakthrough - 5-day trips have a consistent -$400 penalty
2. **Complex Receipt Processing**: Receipt treatment varies dramatically by trip length:
   - 1-day trips: Heavy penalty (-0.5x for normal amounts)
   - 5-day trips: Full reimbursement (1.04x)
   - 8+ day trips: Severe penalty (0.02x)
3. **Tiered Mileage System**: First 100 miles at $0.75/mile, remainder at $0.50/mile
4. **Efficiency Bonuses**: Sweet spot of 180-220 miles/day earns $50 bonus
5. **Receipt Amount Caps**: $2000+ receipts always get 0.25x multiplier

### Performance Comparison
| Approach | Score | Average Error | Close Matches (±$1) |
|----------|-------|---------------|---------------------|
| Naive Formula | 93,192 | $930+ | 0 |
| Basic Components | 85,358 | $852 | 0 |
| + 5-Day Penalty | 46,037 | $459 | 0 |
| + Receipt Ratios | 26,000 | $259 | 0 |
| **KISS Final** | **25,601** | **$255** | **2** |
| **ML Breakthrough** | **4,866** | **$47.66** | **20** |

### Current Architecture

**Machine Learning Model Features:**
- Trip categories: `quick_trip_high_miles`, `long_haul`, `low_efficiency`, `sweet_spot_efficiency`, `balanced`
- 3-tier mileage system with explicit tiers
- Receipt multipliers based on trip length and amount
- Efficiency bonuses for optimal miles/day ratios
- Interaction features (days × miles)
- Separate models for normal vs outlier cases

**Implementation:**
```python
# Two-model architecture
if receipts > 1400:
    model = outlier_model  # Specialized for high-receipt cases
else:
    model = main_model     # Optimized for standard cases

reimbursement = model.predict(engineered_features)
```

### Next Optimization Goals
- **Immediate Target**: Achieve first exact matches, score <1,000
- **Advanced Target**: Score <500 with refined outlier handling
- **Ultimate Goal**: Multiple exact matches with score <100

---

**Reverse-engineer a 60-year-old travel reimbursement system using only historical data and employee interviews.**

ACME Corp's legacy reimbursement system has been running for 60 years. No one knows how it works, but it's still used daily.

8090 has built them a new system, but ACME Corp is confused by the differences in results. Your mission is to figure out the original business logic so we can explain why ours is different and better.

Your job: create a perfect replica of the legacy system by reverse-engineering its behavior from 1,000 historical input/output examples and employee interviews.

## What You Have

### Input Parameters

The system takes three inputs:

- `trip_duration_days` - Number of days spent traveling (integer)
- `miles_traveled` - Total miles traveled (integer)
- `total_receipts_amount` - Total dollar amount of receipts (float)

## Documentation

- A PRD (Product Requirements Document)
- Employee interviews with system hints

### Output

- Single numeric reimbursement amount (float, rounded to 2 decimal places)

### Historical Data

- `public_cases.json` - 1,000 historical input/output examples

## Getting Started

1. **Analyze the data**: 
   - Look at `public_cases.json` to understand patterns
   - Look at `PRD.md` to understand the business problem
   - Look at `INTERVIEWS.md` to understand the business logic
2. **Create your implementation**:
   - Copy `run.sh.template` to `run.sh`
   - Implement your calculation logic
   - Make sure it outputs just the reimbursement amount
3. **Test your solution**: 
   - Run `./eval.sh` to see how you're doing
   - Use the feedback to improve your algorithm
4. **Submit**:
   - Run `./generate_results.sh` to get your final results.
   - Add `arjun-krishna1` to your repo.
   - Complete [the submission form](https://forms.gle/sKFBV2sFo2ADMcRt8).

## Implementation Requirements

Your `run.sh` script must:

- Take exactly 3 parameters: `trip_duration_days`, `miles_traveled`, `total_receipts_amount`
- Output a single number (the reimbursement amount)
- Run in under 5 seconds per test case
- Work without external dependencies (no network calls, databases, etc.)

Example:

```bash
./run.sh 5 250 150.75
# Should output something like: 487.25
```

## Evaluation

Run `./eval.sh` to test your solution against all 1,000 cases. The script will show:

- **Exact matches**: Cases within ±$0.01 of the expected output
- **Close matches**: Cases within ±$1.00 of the expected output
- **Average error**: Mean absolute difference from expected outputs
- **Score**: Lower is better (combines accuracy and precision)

Your submission will be tested against `private_cases.json` which does not include the outputs.

## Submission

When you're ready to submit:

1. Push your solution to a GitHub repository
2. Add `arjun-krishna1` to your repository
3. Submit via the [submission form](https://forms.gle/sKFBV2sFo2ADMcRt8).
4. When you submit the form you will submit your `private_results.txt` which will be used for your final score.

---

**Good luck and Bon Voyage!**
