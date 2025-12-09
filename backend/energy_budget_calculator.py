import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from backend.models import HRVReading, Baseline, EnergyBudget
from backend.baseline_tracker import BaselineTracker
import logging

logger = logging.getLogger(__name__)

class EnergyBudgetCalculator:
    """
    Calculates daily readiness score for ME/CFS management.

    Based on research-validated approach:
    - 40% HRV (RMSSD + HF power)
    - 30% RHR (deviation from baseline)
    - 20% Sleep quality
    - 10% Stress
    """

    def __init__(self):
        self.baseline_tracker = BaselineTracker()

        # Component weights (must sum to 1.0)
        self.weights = {
            'hrv': 0.40,
            'rhr': 0.30,
            'sleep': 0.20,
            'stress': 0.10
        }

    def calculate_readiness(
        self,
        db: Session,
        user_id: int,
        hrv_reading: HRVReading,
        baseline: Baseline
    ) -> Dict[str, any]:
        """
        Calculate overall readiness score from HRV reading and baseline.

        Args:
            db: Database session
            user_id: User ID
            hrv_reading: Latest HRV reading
            baseline: Active baseline

        Returns:
            Dictionary with readiness metrics
        """
        # Calculate component scores
        hrv_score = self._calculate_hrv_score(hrv_reading, baseline)
        rhr_score = self._calculate_rhr_score(hrv_reading, baseline)
        sleep_score = self._calculate_sleep_score(hrv_reading)
        stress_score = self._calculate_stress_score(hrv_reading)

        # Calculate weighted readiness score (0-100)
        energy_budget = (
            hrv_score * self.weights['hrv'] +
            rhr_score * self.weights['rhr'] +
            sleep_score * self.weights['sleep'] +
            stress_score * self.weights['stress']
        )

        # Calculate z-scores
        hrv_zscore = self.baseline_tracker.calculate_hrv_z_score(
            hrv_reading.rmssd,
            baseline
        )
        rhr_zscore = self.baseline_tracker.calculate_hr_z_score(
            hrv_reading.mean_hr,
            baseline
        )

        # Assess PEM risk
        pem_risk = self._assess_pem_risk(
            db, user_id, hrv_zscore, rhr_zscore, hrv_reading.recorded_at
        )

        # Generate activity recommendation
        activity_rec = self._generate_activity_recommendation(
            energy_budget, pem_risk['level'], hrv_zscore
        )

        return {
            'energy_budget': float(energy_budget),
            'hrv_score': float(hrv_score),
            'rhr_score': float(rhr_score),
            'sleep_score': float(sleep_score),
            'stress_score': float(stress_score),
            'hrv_zscore': float(hrv_zscore),
            'rhr_zscore': float(rhr_zscore),
            'pem_risk_level': pem_risk['level'],
            'consecutive_low_days': pem_risk['consecutive_days'],
            'activity_recommendation': activity_rec
        }

    def _calculate_hrv_score(
        self,
        reading: HRVReading,
        baseline: Baseline
    ) -> float:
        """
        Calculate HRV component score (0-100).

        Based on RMSSD z-score and HF power relative to baseline.

        Args:
            reading: HRV reading
            baseline: Baseline

        Returns:
            Score 0-100 (higher is better)
        """
        # Calculate RMSSD z-score
        hrv_zscore = self.baseline_tracker.calculate_hrv_z_score(
            reading.rmssd,
            baseline
        )

        # Convert z-score to 0-100 scale
        # z=0 → 50, z=+1 → 70, z=+2 → 85, z=-1 → 30, z=-2 → 15
        # Using sigmoid-like transformation
        hrv_score_from_rmssd = 50 + (20 * hrv_zscore)

        # Clamp to 0-100
        hrv_score_from_rmssd = max(0, min(100, hrv_score_from_rmssd))

        # If HF power available, factor it in (HF reflects parasympathetic activity)
        if reading.hf_power and baseline.mean_hf_power:
            hf_ratio = reading.hf_power / baseline.mean_hf_power
            hf_score = 50 + (50 * (hf_ratio - 1))  # 1.0 ratio = 50 points
            hf_score = max(0, min(100, hf_score))

            # Average RMSSD and HF scores
            hrv_score = (hrv_score_from_rmssd * 0.7) + (hf_score * 0.3)
        else:
            hrv_score = hrv_score_from_rmssd

        return hrv_score

    def _calculate_rhr_score(
        self,
        reading: HRVReading,
        baseline: Baseline
    ) -> float:
        """
        Calculate resting heart rate component score (0-100).

        Lower HR is better for CFS patients.

        Args:
            reading: HRV reading
            baseline: Baseline

        Returns:
            Score 0-100 (higher is better = lower HR)
        """
        if not baseline.mean_hr or not baseline.sd_hr:
            return 50.0  # Default neutral score

        rhr_zscore = self.baseline_tracker.calculate_hr_z_score(
            reading.mean_hr,
            baseline
        )

        # For HR, negative z-score is good (below baseline HR)
        # z=0 → 50, z=-1 → 70, z=-2 → 85, z=+1 → 30, z=+2 → 15
        rhr_score = 50 - (20 * rhr_zscore)

        # Clamp to 0-100
        return max(0, min(100, rhr_score))

    def _calculate_sleep_score(self, reading: HRVReading) -> float:
        """
        Calculate sleep quality component score (0-100).

        Uses sleep_quality from device if available.

        Args:
            reading: HRV reading

        Returns:
            Score 0-100
        """
        if reading.sleep_quality is not None:
            return float(reading.sleep_quality)

        # If no sleep quality, use sleep duration as proxy
        if reading.sleep_duration:
            # Optimal sleep: 7-9 hours
            if 7 <= reading.sleep_duration <= 9:
                return 80.0
            elif 6 <= reading.sleep_duration <= 10:
                return 60.0
            elif 5 <= reading.sleep_duration <= 11:
                return 40.0
            else:
                return 30.0

        return 50.0  # Default neutral score

    def _calculate_stress_score(self, reading: HRVReading) -> float:
        """
        Calculate stress component score (0-100).

        Can be derived from LF/HF ratio or device stress score.

        Args:
            reading: HRV reading

        Returns:
            Score 0-100 (higher is better = lower stress)
        """
        # Use LF/HF ratio as stress indicator
        if reading.lf_hf_ratio is not None:
            # Normal LF/HF: 1-3
            # Higher ratio = more sympathetic (stress)
            # Lower ratio = more parasympathetic (relaxed)

            if reading.lf_hf_ratio <= 1.5:
                stress_score = 90.0  # Very relaxed
            elif reading.lf_hf_ratio <= 2.5:
                stress_score = 70.0  # Normal
            elif reading.lf_hf_ratio <= 4.0:
                stress_score = 50.0  # Moderate stress
            elif reading.lf_hf_ratio <= 6.0:
                stress_score = 30.0  # High stress
            else:
                stress_score = 15.0  # Very high stress

            return stress_score

        return 50.0  # Default neutral score

    def _assess_pem_risk(
        self,
        db: Session,
        user_id: int,
        hrv_zscore: float,
        rhr_zscore: float,
        current_date: datetime
    ) -> Dict[str, any]:
        """
        Assess Post-Exertional Malaise (PEM) risk.

        PEM risk factors from research:
        - 3+ consecutive days of HRV below -1 SD
        - HR elevated >10% above baseline (approx z>1.4)
        - RMSSD drop >25% from baseline (approx z<-1.3)

        Args:
            db: Database session
            user_id: User ID
            hrv_zscore: Current HRV z-score
            rhr_zscore: Current RHR z-score
            current_date: Current date

        Returns:
            Dictionary with risk level and consecutive low days
        """
        # Get last 7 days of readiness scores
        start_date = current_date - timedelta(days=7)
        recent_scores = db.query(EnergyBudget).filter(
            EnergyBudget.user_id == user_id,
            EnergyBudget.date >= start_date,
            EnergyBudget.date <= current_date
        ).order_by(EnergyBudget.date.desc()).all()

        # Count consecutive low HRV days
        consecutive_low_days = 0
        for score in recent_scores:
            if score.hrv_zscore < -1.0:
                consecutive_low_days += 1
            else:
                break

        # Determine risk level
        risk_level = "low"

        if consecutive_low_days >= 3:
            risk_level = "high"
        elif consecutive_low_days >= 2:
            risk_level = "moderate"
        elif hrv_zscore < -1.5 or rhr_zscore > 1.4:
            risk_level = "moderate"
        elif hrv_zscore < -1.0:
            risk_level = "moderate"

        return {
            'level': risk_level,
            'consecutive_days': consecutive_low_days
        }

    def _generate_activity_recommendation(
        self,
        energy_budget: float,
        pem_risk_level: str,
        hrv_zscore: float
    ) -> str:
        """
        Generate activity recommendation based on readiness and PEM risk.

        Args:
            energy_budget: Overall readiness (0-100)
            pem_risk_level: "low", "moderate", "high"
            hrv_zscore: HRV z-score

        Returns:
            Activity recommendation string
        """
        if pem_risk_level == "high":
            return "rest"

        if energy_budget >= 70:
            return "normal"
        elif energy_budget >= 50:
            return "light"
        elif energy_budget >= 30:
            return "reduced"
        else:
            return "rest"

    def save_energy_budget(
        self,
        db: Session,
        user_id: int,
        date: datetime,
        readiness_data: Dict[str, any]
    ) -> EnergyBudget:
        """
        Save readiness score to database.

        Args:
            db: Database session
            user_id: User ID
            date: Date for this readiness score
            readiness_data: Dictionary with readiness metrics

        Returns:
            Created EnergyBudget object
        """
        score = EnergyBudget(
            user_id=user_id,
            date=date,
            **readiness_data
        )

        db.add(score)
        db.commit()
        db.refresh(score)

        logger.info(f"Created readiness score for user {user_id}: {readiness_data['energy_budget']:.1f}")
        return score

    def get_readiness_trend(
        self,
        db: Session,
        user_id: int,
        days: int = 7
    ) -> List[Dict[str, any]]:
        """
        Get readiness score trend over specified days.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to retrieve

        Returns:
            List of readiness scores with dates
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        scores = db.query(EnergyBudget).filter(
            EnergyBudget.user_id == user_id,
            EnergyBudget.date >= start_date,
            EnergyBudget.date <= end_date
        ).order_by(EnergyBudget.date).all()

        return [
            {
                'date': score.date.isoformat(),
                'energy_budget': score.energy_budget,
                'hrv_score': score.hrv_score,
                'rhr_score': score.rhr_score,
                'sleep_score': score.sleep_score,
                'stress_score': score.stress_score,
                'pem_risk_level': score.pem_risk_level,
                'activity_recommendation': score.activity_recommendation
            }
            for score in scores
        ]
