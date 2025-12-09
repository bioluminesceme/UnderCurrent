# HRV Formulas and Calculations for ME/CFS App

## Key Sources
1. **Meeus et al. 2013** - Systematic review: HRV in FM/CFS patients
2. **Burton et al. 2010** - HRV predicts sleep quality in CFS
3. **Boneva et al. 2007** - Population-based study: Higher HR and reduced HRV persist during sleep in CFS

---

## HRV Parameters Definitions

### Time Domain Parameters

#### SDNN (Standard Deviation of NN intervals)
- **Definition**: Standard deviation of all normal R-R intervals
- **Unit**: milliseconds (ms)
- **Indicates**: Overall HRV; both parasympathetic and sympathetic activity
- **Normal range**: Varies by age; typically 50-100 ms at rest
- **CFS Finding**: Reduced in 24h monitoring (FM: 81.6±29.7 vs Controls: 99.4±57.7 ms)

#### RMSSD (Root Mean Square of Successive Differences)
- **Formula**:
  ```
  RMSSD = √(Σ(RRᵢ₊₁ - RRᵢ)² / N)
  ```
  Where:
  - RRᵢ = R-R interval i
  - N = total number of R-R intervals
- **Unit**: ms
- **Indicates**: Parasympathetic (vagal) activity
- **CFS Finding**:
  - Burton et al: CFS 24.6±10.2 ms vs Controls 53.6±40.8 ms (p=0.006)
  - Best predictor of sleep quality and repeated awakenings
  - Boneva et al: CFS 51.1±40.8 ms vs Controls 66.6±87.5 ms

#### PNN50 (Percentage of successive NN intervals differing by >50ms)
- **Formula**:
  ```
  PNN50 = (NN50 / total NN intervals) × 100
  ```
  Where NN50 = number of successive R-R interval pairs differing by >50ms
- **Unit**: Percentage (%)
- **Indicates**: Parasympathetic activity
- **CFS Finding**: Reduced in FM patients during 24h (11.9±14.7% vs 13.5±13.8%)

#### SDANN
- **Definition**: Standard deviation of average NN intervals calculated over 5-minute periods
- **Unit**: ms
- **Indicates**: Long-term HRV components
- **Use**: 24-hour recordings

#### SDNN Index
- **Definition**: Mean of 5-minute standard deviations of NN intervals
- **Unit**: ms
- **Indicates**: Variability due to cycles shorter than 5 min

---

## Frequency Domain Parameters

### Analysis Method
- **Technique**: Power spectral density using autoregressive modeling
- **Sampling rate**: 200 Hz (Boneva et al.)
- **Unit**: ms² (milliseconds squared)

### Frequency Bands

#### HF (High Frequency Power)
- **Frequency range**: 0.15-0.40 Hz
- **Reflects**: **Parasympathetic (vagal) modulation**
- **Respiratory influence**: Mediated by vagal activity; corresponds to respiratory sinus arrhythmia
- **CFS Findings**:
  - Burton et al: CFS 11.0±6.7% vs Controls 30.3±17.3% (p<0.001)
  - Boneva et al: CFS 1493±1062 ms² vs Controls 1669±1276 ms² (NS during sleep)
  - **Key predictor** of sleep quality (β=-0.43, p=0.007)

#### LF (Low Frequency Power)
- **Frequency range**: 0.04-0.15 Hz
- **Reflects**: **Both sympathetic AND parasympathetic modulation**
- **Note**: Interpretation controversial; some suggest predominantly sympathetic
- **CFS Findings**:
  - Boneva et al: CFS 3189±1180 ms² vs Controls 4036±1591 ms² (p=0.02)
  - Reduced absolute LF in FM vs controls
  - When expressed as %, may appear increased due to lower total power

#### VLF (Very Low Frequency Power)
- **Frequency range**: 0.0033-0.04 Hz (some studies: ≤0.004 Hz)
- **Reflects**: State of arousal, thermoregulation, hormonal influences
- **CFS Finding**:
  - Boneva et al: CFS 5465±2425 ms² vs Controls 7329±2892 ms² (p=0.006)
  - Significantly reduced during sleep in CFS

#### ULF (Ultra Low Frequency)
- **Frequency range**: <0.0033 Hz
- **Note**: Only calculable from 24-hour recordings
- **Use**: Circadian rhythm analysis

#### TP (Total Power)
- **Definition**: Variance of all NN intervals; sum of power in all frequency bands
- **Formula**:
  ```
  TP = VLF + LF + HF
  ```
- **Unit**: ms²
- **Indicates**: Overall HRV
- **CFS Finding**:
  - Boneva et al: CFS 10,297±3,327 ms² vs Controls 13,208±4,278 ms² (p=0.003)
  - Remains significant after adjusting for confounders

---

## Derived Ratios

### LF/HF Ratio
- **Formula**:
  ```
  LF/HF = LF power / HF power
  ```
- **When using normalized units**:
  ```
  LF(nu) = [LF / (TP - VLF)] × 100
  HF(nu) = [HF / (TP - VLF)] × 100
  ```
- **Indicates**: Sympatho-vagal balance
- **Interpretation**:
  - Higher ratio = sympathetic predominance
  - Lower ratio = parasympathetic predominance
- **CFS Findings**:
  - FM: Higher LF/HF during 24h and at night
  - Boneva et al: CFS 2.85±1.68 vs Controls 3.42±2.09 (NS)
  - Increased in FM during supine rest

---

## Heart Rate Calculations

### Heart Rate from R-R Interval
```
HR (bpm) = 60,000 ms / mean RR interval (ms)
```

### Mean RR Interval
```
Mean RRI = Σ(all normal RR intervals) / N
```
Where N = total number of normal RR intervals

### CFS Findings - Heart Rate
- **Boneva et al (during sleep)**:
  - CFS: 71.4 bpm (RRI: 840.4±85.3 ms)
  - Controls: 64.8 bpm (RRI: 925.4±97.8 ms)
  - p<0.0004

- **Boneva et al (awake, supine after 30 min rest)**:
  - CFS: 79.2±9.6 bpm
  - Controls: 72.2±8.7 bpm
  - p=0.003

---

## Normalization and Units

### Measurement Units Used in Studies
1. **Absolute power** (ms²) - most common
2. **Natural logarithm** of ms² [Ln(ms²)]
3. **Normalized units** (nu) - percentage relative to total power
4. **Percentages** (%) - relative to total power

### Converting Between Units
```
Normalized LF = [LF / (TP - VLF)] × 100
Normalized HF = [HF / (TP - VLF)] × 100
```

**Important**: Studies using relative vs absolute measurements show different patterns:
- Absolute LF: Lower in FM
- Relative LF (%): Higher in FM (because TP is much lower)

---

## Recording Requirements

### Minimum Recording Duration
- **Short-term**: 5 minutes (for time and frequency domain)
- **24-hour**: For circadian analysis, VLF, ULF components
- **Overnight sleep**: 2-4 hours of artifact-free data (Burton et al: mean 2:43-3:32 hours)

### Data Quality Requirements
1. **Artifact removal**: Manual removal of:
   - Ectopic beats
   - Movement artifacts
   - Equipment noise

2. **Normal RR intervals only**: Exclude:
   - Abnormal QRS complexes
   - Arrhythmias
   - Premature beats

3. **Stationarity**: Data should be relatively stable (no major HR changes)

### Sampling Rate
- Minimum: 250 Hz for R-wave detection
- Recommended: 500-1000 Hz for precise timing
- Boneva study: 200 Hz

---

## Important Confounders to Control

### 1. Breathing Rate
- **Effect**: Directly affects HF power (respiratory sinus arrhythmia)
- **Solution**:
  - Control/monitor breathing rate
  - Use paced breathing (e.g., 12 breaths/min)
  - Record respiratory rate alongside ECG

### 2. Physical Activity Level
- **Effect**: Deconditioning reduces HRV
- **CFS issue**: By definition, CFS patients have reduced activity
- **Finding**: Even after matching for activity limitation, CFS still had higher HR

### 3. Medications
Medications affecting HRV:
- **Antidepressants**: Increase HR, decrease SDANN, HF, LF
- **Beta blockers**: Decrease HR, decrease SDANN
- **Calcium channel blockers**
- **ACE inhibitors/diuretics**
- **Sympathomimetics**

### 4. Age and Sex
- **Age**: HRV decreases with age
- **Sex**: Women have lower mean LF, VLF, TP compared to men

### 5. BMI
- Higher BMI associated with lower HRV

### 6. Time of Day
- Circadian rhythm affects autonomic balance
- Standardize measurement time

### 7. Stress/Anxiety
- Acute stress reduces HRV
- Chronic stress reduces parasympathetic activity

---

## Clinical Correlations in CFS

### HRV Parameters Correlate With:

#### From Boneva et al. 2007:
**Heart Rate correlations (Spearman r, p<0.001):**
- SF-36 Vitality: r = -0.49
- MFI General Fatigue: r = 0.46
- MFI Physical Fatigue: r = 0.43
- MFI Activity Reduction: r = 0.41
- SF-36 Physical Function: r = -0.39
- SF-36 Bodily Pain: r = -0.39

**HRV Parameters:**
- Total Power correlates with vitality, physical function, activity reduction
- RMSSD: Best predictor of subjective sleep quality and repeated awakenings

### Interpretation:
- **Higher HR** → More fatigue, less vitality, more impairment
- **Lower HRV** → Worse sleep quality, more fatigue

---

## Baseline Calculation Methods (For App)

### 1. HRV Baseline (from research + Visible app approach)

**Recommended Approach**:
```
Individual baseline = ln(RMSSD)
Rolling window = 28 days (Visible app uses this)
Update frequency = Daily
```

**Z-score normalization**:
```
HRV z-score = [Today's ln(RMSSD) - Mean baseline ln(RMSSD)] / SD baseline
```

**Interpretation**:
- Z-score > 0: Above baseline (better recovery)
- Z-score < 0: Below baseline (reduced recovery)
- Z-score < -1: Significant decrease (warning sign)

### 2. Resting Heart Rate Baseline

**From Boneva study - Population values**:
- Healthy controls (sleep): 64.8 ± 7.0 bpm
- CFS patients (sleep): 71.4 ± 7.6 bpm
- Healthy controls (awake, rested): 72.2 ± 8.7 bpm
- CFS patients (awake, rested): 79.2 ± 9.6 bpm

**Individual baseline approach**:
```
Personal baseline RHR = Mean(overnight HR) over 7-14 days
Z-score = [Today's RHR - Baseline RHR] / SD baseline
```

### 3. Multi-day Trends
From systematic review: "Using multi-day trends, not just single nights, is aligned with the literature"

**Recommended**:
- Calculate 7-day moving average
- Track deviation from 28-day baseline
- Flag consecutive days below baseline

---

## Key Findings Summary for App Development

### Most Reliable CFS Markers:
1. **Elevated resting HR** (during sleep and awake)
   - Persistent across all studies
   - Correlates with fatigue severity

2. **Reduced RMSSD** (parasympathetic activity)
   - Best predictor of sleep quality
   - Predictor of repeated awakenings

3. **Reduced Total Power**
   - Indicates overall reduced HRV
   - Significant even after controlling for confounders

4. **Reduced HF Power**
   - Vagal dysfunction
   - Predicts subjective sleep quality

5. **LF/HF Ratio** direction depends on measurement:
   - FM: Often elevated (sympathetic predominance)
   - But interpretation complex due to measurement units

### Red Flags for Your App:
1. Overnight HR consistently >10% above personal baseline
2. RMSSD <30 ms (especially if personal baseline >50 ms)
3. HRV z-score < -1.5 for 3+ consecutive days
4. Total Power < 10,000 ms² during sleep

---

## Next Steps for App Algorithm

### Data to Collect:
1. **Overnight ECG** (via Garmin or compatible device)
2. **Calculate**:
   - Mean HR during sleep
   - RMSSD
   - HF, LF, VLF, TP
   - LF/HF ratio

3. **Track over time**:
   - 28-day rolling baseline
   - Daily z-scores
   - 7-day trends

### Readiness Score Components (from plan):
Suggested weighting based on research:
- **40% HRV** (RMSSD + HF power)
- **30% RHR** (deviation from baseline)
- **20% Sleep quality** (Garmin sleep score)
- **10% Stress** (Garmin stress level)

### PEM Risk Prediction:
Monitor for:
- 3+ consecutive days of HRV below -1 SD
- HR elevated >10% above baseline
- RMSSD drop >25% from baseline
- Combined with increased activity on previous day

---

## References
- Meeus et al. (2013). Heart rate variability in patients with fibromyalgia and chronic fatigue syndrome. Seminars in Arthritis and Rheumatism, 43(2), 279-287.
- Burton et al. (2010). Reduced heart rate variability predicts poor sleep quality in chronic fatigue syndrome. Exp Brain Res, 204:71-78.
- Boneva et al. (2007). Higher heart rate and reduced HRV persist during sleep in CFS. Autonomic Neuroscience, 137:94-101.
- Task Force of the European Society of Cardiology (1996). Heart rate variability: Standards of measurement, physiological interpretation, and clinical use.
