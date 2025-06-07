# Top Coder Challenge: Black Box Legacy Reimbursement System

## 🚀 Our Solution Overview

### Approaches Implemented

**Component-Based KISS Approach (Primary Solution)**
We successfully reverse-engineered the legacy system using a systematic, interpretable approach that achieved a **73% improvement** over naive methods:

- **Initial Score**: 93,192 (naive formula)
- **Final Score**: 25,601 (73% improvement)
- **Average Error**: Reduced from $930 to $255

**Key Discoveries:**
1. **5-Day Trip Penalty**: Major breakthrough - 5-day trips have a consistent -$400 penalty
2. **Complex Receipt Processing**: Receipt treatment varies dramatically by trip length:
   - 1-day trips: Heavy penalty (-0.5x for normal amounts)
   - 5-day trips: Full reimbursement (1.04x)
   - 8+ day trips: Severe penalty (0.02x)
3. **Tiered Mileage System**: First 100 miles at $0.75/mile, remainder at $0.50/mile
4. **Efficiency Bonuses**: Sweet spot of 180-220 miles/day earns $50 bonus
5. **Receipt Amount Caps**: $2000+ receipts always get 0.25x multiplier

**Final Formula Structure:**
```
reimbursement = base_per_diem + mileage_component + receipt_component + bonuses/penalties
```

**Machine Learning Approach (Secondary Solution)**
Implemented a dual Decision Tree system with sophisticated feature engineering:
- Separate models for normal vs. high-receipt cases (>$1400 threshold)
- Advanced features: efficiency ratios, trip categorization, interaction effects
- Incorporates all business rules discovered in KISS approach

### Performance Comparison
| Approach | Score | Average Error | Exact Matches |
|----------|-------|---------------|---------------|
| Naive Formula | 93,192 | $930+ | 0 |
| Basic Components | 85,358 | $852 | 0 |
| + 5-Day Penalty | 46,037 | $459 | 0 |
| + Receipt Ratios | 26,000 | $259 | 0 |
| **Final KISS** | **25,601** | **$255** | **0** |
| **ML Approach** | *TBD* | *TBD* | *TBD* |

### Future Optimization Paths

**Phase 1: KISS Refinements (Recommended Next - 1-2 hours)**
- Fine-tune receipt ratios (currently rough estimates)
- Add 4-day trip bonus ($235/day pattern detected)
- Implement 3-tier mileage system (0-100, 100-500, 500+ miles)
- Calibrate efficiency bonus thresholds

**Phase 2: Advanced Business Rules (2-3 hours)**
- Implement Kevin's "6 calculation paths" theory
- Add interaction effects between trip characteristics
- Test temporal/seasonal patterns using case indices

**Phase 3: Machine Learning Approaches (3-5 hours)**
- Feature engineering + interpretable ML models
- Hybrid KISS + ML error correction
- Ensemble methods combining multiple approaches

**Phase 4: Systematic Optimization (2-4 hours)**
- Grid search hyperparameter optimization
- Genetic algorithm for parameter evolution

### Target Goals
- **Short-term**: Achieve first exact matches, score <20,000
- **Medium-term**: Score <15,000 with advanced business rules
- **Long-term**: Score <10,000 with optimized ML approaches

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
