import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from backend.models import HRVReading, Baseline
import logging

logger = logging.getLogger(__name__)

class BaselineTracker:
    """
    Tracks and calculates baseline HRV metrics using 28-day rolling window.

    Based on research:
    - Visible app approach: 28-day rolling baseline with z-score normalization
    - Boneva et al. population values for CFS/healthy controls
    """

    def __init__(self, baseline_days: int = 28):
        """
        Initialize baseline tracker.

        Args:
            baseline_days: Number of days for rolling baseline (default: 28)
        """
        self.baseline_days = baseline_days
        self.min_readings_required = 7  # Minimum readings needed for valid baseline

    def calculate_baseline(
        self,
        db: Session,
        user_id: int,
        end_date: Optional[datetime] = None
    ) -> Optional[Dict[str, float]]:
        """
        Calculate baseline metrics from recent HRV readings.

        Args:
            db: Database session
            user_id: User ID
            end_date: End date for baseline period (default: now)

        Returns:
            Dictionary with baseline metrics or None if insufficient data
        """
        if end_date is None:
            end_date = datetime.utcnow()

        start_date = end_date - timedelta(days=self.baseline_days)

        # Get HRV readings in baseline period
        readings = db.query(HRVReading).filter(
            HRVReading.user_id == user_id,
            HRVReading.recorded_at >= start_date,
            HRVReading.recorded_at <= end_date
        ).order_by(HRVReading.recorded_at).all()

        if len(readings) < self.min_readings_required:
            logger.warning(
                f"Insufficient data for baseline: {len(readings)} readings "
                f"(minimum {self.min_readings_required} required)"
            )
            return None

        # Extract metrics
        rmssd_values = [r.rmssd for r in readings if r.rmssd is not None]
        hr_values = [r.mean_hr for r in readings if r.mean_hr is not None]
        total_power_values = [r.total_power for r in readings if r.total_power is not None]
        hf_power_values = [r.hf_power for r in readings if r.hf_power is not None]
        lf_power_values = [r.lf_power for r in readings if r.lf_power is not None]

        if len(rmssd_values) < self.min_readings_required:
            logger.warning("Insufficient RMSSD readings for baseline")
            return None

        # Calculate ln(RMSSD) baseline (recommended approach)
        ln_rmssd_values = [np.log(r) for r in rmssd_values if r > 0]

        baseline = {
            'start_date': start_date,
            'end_date': end_date,
            'days_count': (end_date - start_date).days,
            'readings_count': len(readings),

            # HRV baselines - ln(RMSSD) approach
            'mean_ln_rmssd': float(np.mean(ln_rmssd_values)),
            'sd_ln_rmssd': float(np.std(ln_rmssd_values, ddof=1)),
            'mean_rmssd': float(np.mean(rmssd_values)),

            # Heart rate baselines
            'mean_hr': float(np.mean(hr_values)) if hr_values else None,
            'sd_hr': float(np.std(hr_values, ddof=1)) if len(hr_values) > 1 else None,

            # Power spectrum baselines
            'mean_total_power': float(np.mean(total_power_values)) if total_power_values else None,
            'mean_hf_power': float(np.mean(hf_power_values)) if hf_power_values else None,
            'mean_lf_power': float(np.mean(lf_power_values)) if lf_power_values else None,
        }

        return baseline

    def save_baseline(
        self,
        db: Session,
        user_id: int,
        baseline_data: Dict[str, any]
    ) -> Baseline:
        """
        Save baseline to database and mark as active.

        Args:
            db: Database session
            user_id: User ID
            baseline_data: Dictionary with baseline metrics

        Returns:
            Created Baseline object
        """
        # Deactivate previous baselines
        db.query(Baseline).filter(
            Baseline.user_id == user_id,
            Baseline.is_active == True
        ).update({'is_active': False})

        # Create new baseline
        baseline = Baseline(
            user_id=user_id,
            calculated_at=datetime.utcnow(),
            is_active=True,
            **baseline_data
        )

        db.add(baseline)
        db.commit()
        db.refresh(baseline)

        logger.info(f"Created new baseline for user {user_id}")
        return baseline

    def get_active_baseline(
        self,
        db: Session,
        user_id: int
    ) -> Optional[Baseline]:
        """
        Get the currently active baseline for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Active Baseline object or None
        """
        return db.query(Baseline).filter(
            Baseline.user_id == user_id,
            Baseline.is_active == True
        ).first()

    def calculate_z_score(
        self,
        value: float,
        baseline_mean: float,
        baseline_sd: float
    ) -> float:
        """
        Calculate z-score for a value relative to baseline.

        Formula: z-score = (value - mean) / SD

        Args:
            value: Current value
            baseline_mean: Baseline mean
            baseline_sd: Baseline standard deviation

        Returns:
            Z-score (positive = above baseline, negative = below baseline)
        """
        if baseline_sd == 0:
            return 0.0

        return (value - baseline_mean) / baseline_sd

    def calculate_hrv_z_score(
        self,
        rmssd: float,
        baseline: Baseline
    ) -> float:
        """
        Calculate HRV z-score using ln(RMSSD).

        Formula: HRV z-score = [ln(today's RMSSD) - mean ln(RMSSD)] / SD

        Args:
            rmssd: Current RMSSD value (ms)
            baseline: Baseline object with mean and SD

        Returns:
            HRV z-score
        """
        if rmssd <= 0:
            raise ValueError("RMSSD must be positive")

        ln_rmssd = np.log(rmssd)
        return self.calculate_z_score(
            ln_rmssd,
            baseline.mean_ln_rmssd,
            baseline.sd_ln_rmssd
        )

    def calculate_hr_z_score(
        self,
        heart_rate: float,
        baseline: Baseline
    ) -> float:
        """
        Calculate heart rate z-score.

        Note: For HR, positive z-score means elevated HR (worse for CFS)

        Args:
            heart_rate: Current heart rate (bpm)
            baseline: Baseline object with mean and SD

        Returns:
            HR z-score
        """
        if baseline.mean_hr is None or baseline.sd_hr is None:
            raise ValueError("Baseline lacks HR statistics")

        return self.calculate_z_score(
            heart_rate,
            baseline.mean_hr,
            baseline.sd_hr
        )

    def interpret_hrv_z_score(self, z_score: float) -> Dict[str, any]:
        """
        Interpret HRV z-score and provide guidance.

        Based on research thresholds:
        - z > 0: Above baseline (better recovery)
        - z < 0: Below baseline (reduced recovery)
        - z < -1: Significant decrease (warning sign)
        - z < -1.5: High concern

        Args:
            z_score: HRV z-score

        Returns:
            Dictionary with interpretation and status
        """
        if z_score >= 0.5:
            status = "excellent"
            interpretation = "Well above baseline - excellent recovery"
            color = "green"
        elif z_score >= 0:
            status = "good"
            interpretation = "Above baseline - good recovery"
            color = "green"
        elif z_score >= -0.5:
            status = "fair"
            interpretation = "Slightly below baseline - monitor closely"
            color = "yellow"
        elif z_score >= -1.0:
            status = "low"
            interpretation = "Below baseline - consider reducing activity"
            color = "orange"
        elif z_score >= -1.5:
            status = "warning"
            interpretation = "Significantly below baseline - rest recommended"
            color = "red"
        else:
            status = "critical"
            interpretation = "Critically low - prioritize rest and recovery"
            color = "red"

        return {
            'z_score': z_score,
            'status': status,
            'interpretation': interpretation,
            'color': color
        }

    def check_population_reference(
        self,
        rmssd: float,
        mean_hr: float
    ) -> Dict[str, any]:
        """
        Compare values against population references from Boneva et al. 2007.

        Population values:
        - Healthy controls (sleep): RMSSD ~66.6ms, HR ~64.8 bpm
        - CFS patients (sleep): RMSSD ~51.1ms, HR ~71.4 bpm
        - Burton et al CFS: RMSSD 24.6ms (very low)

        Args:
            rmssd: Current RMSSD (ms)
            mean_hr: Current heart rate (bpm)

        Returns:
            Dictionary with population comparison
        """
        warnings = []

        # RMSSD thresholds
        if rmssd < 30:
            warnings.append("RMSSD critically low (<30ms) - similar to severe CFS cases")
        elif rmssd < 50:
            warnings.append("RMSSD low (<50ms) - within CFS patient range")

        # Heart rate thresholds
        if mean_hr > 75:
            warnings.append("Heart rate elevated (>75 bpm) - above CFS patient mean")
        elif mean_hr > 70:
            warnings.append("Heart rate elevated (>70 bpm) - within CFS patient range")

        return {
            'rmssd_value': rmssd,
            'hr_value': mean_hr,
            'warnings': warnings,
            'has_concerns': len(warnings) > 0
        }

    def calculate_7day_trend(
        self,
        db: Session,
        user_id: int,
        metric: str = 'rmssd'
    ) -> Optional[Dict[str, float]]:
        """
        Calculate 7-day moving average for a metric.

        Based on research: "Using multi-day trends, not just single nights"

        Args:
            db: Database session
            user_id: User ID
            metric: Metric to track ('rmssd', 'mean_hr', 'total_power')

        Returns:
            Dictionary with trend data or None if insufficient data
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        readings = db.query(HRVReading).filter(
            HRVReading.user_id == user_id,
            HRVReading.recorded_at >= start_date,
            HRVReading.recorded_at <= end_date
        ).order_by(HRVReading.recorded_at).all()

        if len(readings) < 3:
            return None

        values = [getattr(r, metric) for r in readings if getattr(r, metric) is not None]

        if len(values) < 3:
            return None

        return {
            'mean': float(np.mean(values)),
            'std': float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'trend': 'increasing' if values[-1] > values[0] else 'decreasing',
            'readings_count': len(values)
        }
