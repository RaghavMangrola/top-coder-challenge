# Future Approaches for Black Box Reimbursement Challenge

## Current Status (Baseline for Future Work)
- **Current Score**: 25,601 (started at 93,192)
- **Average Error**: $255.01 (started at $930+)
- **Exact Matches**: 0% (need to improve)
- **Close Matches**: 2 cases within $1
- **Total Improvement**: 73% better

## Current KISS Implementation
```bash
# Component-based model:
reimbursement = base_per_diem + mileage_component + receipt_component + bonuses

# Base: $100/day
# Mileage: 0.75 first 100mi, 0.50 after
# Receipts: Complex ratios by trip length + amount caps
# Bonuses: 5-day penalty (-$400) + efficiency bonus (50-20-0)
```

---

## APPROACH 1: Continue KISS Refinements (Recommended Next)

### Immediate Optimizations (1-2 hours)
1. **Fine-tune receipt ratios**: Current ratios are rough estimates
   - Analyze per-trip-length receipt performance
   - A/B test different ratio values (±0.1 increments)
   - Consider receipt amount sub-thresholds (e.g., $500, $1500)

2. **Refine mileage tiers**: Currently simple 2-tier
   - Test 3-tier system: 0-100, 100-500, 500+ miles
   - Analyze high-mileage diminishing returns curve
   - Consider total trip distance vs daily distance

3. **Add 4-day bonus**: Analysis showed 4-day trips have unusually high per-day rates ($235/day)
   - Test +$100-200 bonus for 4-day trips

4. **Calibrate efficiency bonuses**: Current values (50/20/0) are guesses
   - Analyze actual efficiency bonus amounts in data
   - Test different thresholds (150-200, 200-250 mi/day)

### Target: Get to <20,000 score and achieve first exact matches

---

## APPROACH 2: Advanced KISS with Business Rules

### Implement Kevin's Advanced Theories (2-3 hours)
1. **Multiple calculation paths**: Kevin mentioned ~6 different paths
   - Cluster analysis on trip characteristics
   - Separate formulas for: quick-high-mileage, long-low-mileage, balanced, etc.

2. **Interaction effects**: 
   - Trip length × efficiency multipliers
   - Spending per day × total mileage adjustments
   - Receipt amount × trip duration caps

3. **Seasonal/temporal effects**: Kevin mentioned lunar cycles, quarterly patterns
   - Use case index as proxy for temporal factors
   - Test modulo operations on case numbers

4. **User profile simulation**: Kevin suspected user history affects results
   - Track "previous trip" characteristics in evaluation order

### Target: Get to <15,000 score

---

## APPROACH 3: Machine Learning Approaches

### Option A: Feature Engineering + Simple ML (3-4 hours)
**Pros**: Captures complex interactions while staying interpretable
**Cons**: Need to implement ML in bash (challenging)

**Implementation**:
```python
# Features to engineer:
- miles_per_day = miles / days
- spending_per_day = receipts / days  
- trip_category = categorize(days, miles, receipts)
- efficiency_score = complex function of miles/days
- receipt_penalty_factor = function of receipts and days

# Models to try:
- Linear regression with polynomial features
- Decision tree (can export to bash if/else)
- Random forest (ensemble of trees)
```

**Workaround for bash**: Train model in Python, export as lookup table or nested if/else

### Option B: Pure ML Black Box (4-5 hours)
**Pros**: Maximum accuracy potential
**Cons**: No interpretability, complex deployment

**Implementation**:
- Neural network with hidden layers
- Gradient boosting (XGBoost/LightGBM)
- Ensemble of multiple models

**Deployment**: Python script called from bash, or model export to ONNX/simple format

---

## APPROACH 4: Hybrid Approaches

### Option A: KISS + ML Corrections (2-3 hours)
1. Use current KISS model as base
2. Train small ML model on residual errors
3. Final prediction = KISS_prediction + ML_correction

### Option B: Ensemble of Multiple KISS Models (1-2 hours)
1. Create 3-5 different KISS variants
2. Weight them based on trip characteristics
3. Ensemble prediction = weighted average

---

## APPROACH 5: Systematic Optimization

### Hyperparameter Grid Search (2-3 hours)
Current model has ~10-15 parameters that could be optimized:
- Mileage rates (0.75, 0.50)
- Receipt ratios (per trip length)
- Efficiency thresholds and bonuses
- Trip length adjustments

**Method**: 
1. Define parameter ranges
2. Grid search or random search
3. Cross-validation on public cases

### Genetic Algorithm (Advanced, 4-6 hours)
Evolve the parameter values using genetic algorithms

---

## Critical Insights for Next Conversation

### Data Patterns Discovered
1. **5-day trips have -$400 penalty** (most important finding)
2. **Receipt treatment varies drastically by trip length**:
   - 1-day: Heavy penalty (-0.5x for normal, +0.25x for extreme receipts)
   - 5-day: Full reimbursement (1.04x)
   - 8+ day: Heavy penalty (0.02x)
3. **Mileage is tiered**: First 100 miles at higher rate
4. **Efficiency bonuses exist**: 180-220 miles/day sweet spot
5. **Receipt amount caps**: $2000+ always get 0.25x regardless of trip length

### Implementation Lessons
1. **Floating point validation**: Miles can be decimal, not just integers
2. **Negative values**: Watch for negative outputs with penalty ratios
3. **bc for math**: Bash needs `bc` for floating point arithmetic
4. **Component isolation**: Base per diem + mileage + receipts + bonuses structure works well

### Performance Benchmarks
- **Naive approach**: ~93,000 score
- **Basic components**: ~85,000 score  
- **With 5-day penalty**: ~46,000 score
- **With receipt ratios**: ~26,000 score
- **Current with efficiency**: ~25,600 score

### Next Most Promising Direction
1. **Fine-tune receipt ratios** (highest ROI - they're currently rough estimates)
2. **Add 4-day bonus** (clear signal in data)
3. **Test 3-tier mileage system** (current 2-tier may be too simple)

---

## Files to Continue From
- `run.sh` - Current implementation
- `IMPLEMENTATION_LOG.md` - Detailed progress log
- `analyze.py`, `analyze2.py`, `analyze3.py` - Data analysis scripts
- `public_cases.json` - Training data
- `eval.sh` - Evaluation script

## Commands to Resume
```bash
# Quick test
./run.sh 3 93 1.42  # Should output ~364 (expected 364.51)

# Full evaluation
./eval.sh | grep -E "(Exact matches|Average error|Your Score)"

# Generate final results
./generate_results.sh  # When ready to submit
``` 