from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # User profile
    age = Column(Integer)
    sex = Column(String)
    bmi = Column(Float)

    # Relationships
    hrv_readings = relationship("HRVReading", back_populates="user")
    baselines = relationship("Baseline", back_populates="user")
    energy_budgets = relationship("EnergyBudget", back_populates="user")

class HRVReading(Base):
    __tablename__ = "hrv_readings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recorded_at = Column(DateTime, nullable=False, index=True)

    # Time domain parameters
    mean_rri = Column(Float)  # Mean R-R interval (ms)
    mean_hr = Column(Float)   # Mean heart rate (bpm)
    sdnn = Column(Float)      # Standard deviation of NN intervals (ms)
    rmssd = Column(Float)     # Root mean square of successive differences (ms)
    pnn50 = Column(Float)     # Percentage of successive intervals >50ms (%)

    # Frequency domain parameters
    vlf_power = Column(Float)  # Very low frequency power (ms²)
    lf_power = Column(Float)   # Low frequency power (ms²)
    hf_power = Column(Float)   # High frequency power (ms²)
    total_power = Column(Float)  # Total power (ms²)
    lf_hf_ratio = Column(Float)  # LF/HF ratio

    # Normalized units
    lf_nu = Column(Float)  # LF in normalized units
    hf_nu = Column(Float)  # HF in normalized units

    # Sleep context
    sleep_duration = Column(Float)  # Hours
    sleep_quality = Column(Float)   # Score 0-100

    # Data quality
    recording_duration = Column(Float)  # Minutes
    artifact_percentage = Column(Float)  # Percentage of data removed

    # Relationships
    user = relationship("User", back_populates="hrv_readings")

class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Baseline period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    days_count = Column(Integer)  # Number of days in baseline

    # HRV baselines
    mean_ln_rmssd = Column(Float)    # Mean of ln(RMSSD)
    sd_ln_rmssd = Column(Float)      # Standard deviation of ln(RMSSD)
    mean_rmssd = Column(Float)       # Mean RMSSD (ms)

    # Heart rate baselines
    mean_hr = Column(Float)          # Mean heart rate (bpm)
    sd_hr = Column(Float)            # Standard deviation of HR

    # Power spectrum baselines
    mean_total_power = Column(Float)
    mean_hf_power = Column(Float)
    mean_lf_power = Column(Float)

    # Status
    is_active = Column(Boolean, default=True)  # Current baseline

    # Relationships
    user = relationship("User", back_populates="baselines")

class EnergyBudget(Base):
    __tablename__ = "energy_budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)

    # Component scores (0-100)
    hrv_score = Column(Float)      # Based on RMSSD z-score
    rhr_score = Column(Float)      # Based on heart rate z-score
    sleep_score = Column(Float)    # From device
    stress_score = Column(Float)   # From device

    # Overall energy budget (0-100)
    energy_budget = Column(Float, nullable=False)

    # Z-scores
    hrv_zscore = Column(Float)
    rhr_zscore = Column(Float)

    # PEM risk indicators
    pem_risk_level = Column(String)  # "low", "moderate", "high"
    consecutive_low_days = Column(Integer)  # Days below baseline

    # Recommendations
    activity_recommendation = Column(String)  # "normal", "reduced", "rest"

    # Relationships
    user = relationship("User", back_populates="energy_budgets")
