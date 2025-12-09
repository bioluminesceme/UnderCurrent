import numpy as np
from scipy import signal
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class HRVCalculator:
    """
    Calculates HRV metrics based on ME/CFS research findings.

    References:
    - Meeus et al. (2013) - Systematic review
    - Burton et al. (2010) - HRV predicts sleep quality in CFS
    - Boneva et al. (2007) - Higher HR and reduced HRV persist during sleep in CFS
    """

    def __init__(self, sampling_rate: float = 200.0):
        """
        Initialize HRV calculator.

        Args:
            sampling_rate: ECG sampling rate in Hz (default: 200 Hz per Boneva et al.)
        """
        self.sampling_rate = sampling_rate

    def calculate_time_domain(self, rr_intervals: List[float]) -> Dict[str, float]:
        """
        Calculate time domain HRV parameters.

        Args:
            rr_intervals: List of R-R intervals in milliseconds

        Returns:
            Dictionary containing:
            - mean_rri: Mean R-R interval (ms)
            - mean_hr: Mean heart rate (bpm)
            - sdnn: Standard deviation of NN intervals (ms)
            - rmssd: Root mean square of successive differences (ms)
            - pnn50: Percentage of successive intervals >50ms (%)
        """
        if len(rr_intervals) < 2:
            raise ValueError("Need at least 2 RR intervals for time domain analysis")

        rr_array = np.array(rr_intervals)

        # Mean RR interval
        mean_rri = np.mean(rr_array)

        # Mean heart rate: HR (bpm) = 60,000 ms / mean RR interval (ms)
        mean_hr = 60000.0 / mean_rri

        # SDNN: Standard deviation of all NN intervals
        sdnn = np.std(rr_array, ddof=1)

        # RMSSD: Root mean square of successive differences
        # Formula: RMSSD = √(Σ(RRᵢ₊₁ - RRᵢ)² / N)
        successive_diffs = np.diff(rr_array)
        rmssd = np.sqrt(np.mean(successive_diffs ** 2))

        # PNN50: Percentage of successive NN intervals differing by >50ms
        # Formula: PNN50 = (NN50 / total NN intervals) × 100
        nn50_count = np.sum(np.abs(successive_diffs) > 50)
        pnn50 = (nn50_count / len(successive_diffs)) * 100

        return {
            'mean_rri': float(mean_rri),
            'mean_hr': float(mean_hr),
            'sdnn': float(sdnn),
            'rmssd': float(rmssd),
            'pnn50': float(pnn50)
        }

    def calculate_frequency_domain(
        self,
        rr_intervals: List[float],
        method: str = 'welch'
    ) -> Dict[str, float]:
        """
        Calculate frequency domain HRV parameters using power spectral density.

        Args:
            rr_intervals: List of R-R intervals in milliseconds
            method: 'welch' or 'ar' (autoregressive). Default: 'welch'

        Returns:
            Dictionary containing:
            - vlf_power: Very low frequency power (ms²) [0.0033-0.04 Hz]
            - lf_power: Low frequency power (ms²) [0.04-0.15 Hz]
            - hf_power: High frequency power (ms²) [0.15-0.40 Hz]
            - total_power: Total power (ms²)
            - lf_hf_ratio: LF/HF ratio
            - lf_nu: LF normalized units
            - hf_nu: HF normalized units
        """
        if len(rr_intervals) < 60:
            raise ValueError("Need at least 60 RR intervals for frequency domain analysis")

        rr_array = np.array(rr_intervals)

        # Resample RR intervals to evenly spaced time series (4 Hz standard)
        resampling_rate = 4.0  # Hz
        time_stamps = np.cumsum(rr_array) / 1000.0  # Convert to seconds
        time_stamps = np.insert(time_stamps, 0, 0)  # Add initial 0

        # Create evenly spaced time array
        total_time = time_stamps[-1]
        even_time = np.arange(0, total_time, 1.0 / resampling_rate)

        # Interpolate RR intervals to evenly spaced samples
        rr_interpolated = np.interp(even_time, time_stamps[:-1], rr_array)

        # Calculate power spectral density using Welch's method
        if method == 'welch':
            freqs, psd = signal.welch(
                rr_interpolated,
                fs=resampling_rate,
                nperseg=min(256, len(rr_interpolated)),
                scaling='density'
            )
        else:
            # Autoregressive method (more complex, not implemented in basic version)
            raise NotImplementedError("AR method not yet implemented")

        # Define frequency bands
        vlf_band = (0.0033, 0.04)  # Very low frequency
        lf_band = (0.04, 0.15)     # Low frequency
        hf_band = (0.15, 0.40)     # High frequency

        # Calculate power in each band
        vlf_power = self._calculate_band_power(freqs, psd, vlf_band)
        lf_power = self._calculate_band_power(freqs, psd, lf_band)
        hf_power = self._calculate_band_power(freqs, psd, hf_band)

        # Total power: TP = VLF + LF + HF
        total_power = vlf_power + lf_power + hf_power

        # LF/HF ratio
        lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0.0

        # Normalized units: LF(nu) = [LF / (TP - VLF)] × 100
        total_minus_vlf = total_power - vlf_power
        lf_nu = (lf_power / total_minus_vlf * 100) if total_minus_vlf > 0 else 0.0
        hf_nu = (hf_power / total_minus_vlf * 100) if total_minus_vlf > 0 else 0.0

        return {
            'vlf_power': float(vlf_power),
            'lf_power': float(lf_power),
            'hf_power': float(hf_power),
            'total_power': float(total_power),
            'lf_hf_ratio': float(lf_hf_ratio),
            'lf_nu': float(lf_nu),
            'hf_nu': float(hf_nu)
        }

    def _calculate_band_power(
        self,
        freqs: np.ndarray,
        psd: np.ndarray,
        band: tuple
    ) -> float:
        """
        Calculate power in a specific frequency band.

        Args:
            freqs: Frequency array from PSD
            psd: Power spectral density array
            band: Tuple of (low_freq, high_freq) in Hz

        Returns:
            Power in the specified band (ms²)
        """
        band_mask = (freqs >= band[0]) & (freqs < band[1])
        band_power = np.trapz(psd[band_mask], freqs[band_mask])
        return float(band_power)

    def calculate_all_metrics(
        self,
        rr_intervals: List[float]
    ) -> Dict[str, float]:
        """
        Calculate all HRV metrics (time and frequency domain).

        Args:
            rr_intervals: List of R-R intervals in milliseconds

        Returns:
            Dictionary containing all HRV metrics
        """
        metrics = {}

        # Time domain
        try:
            time_metrics = self.calculate_time_domain(rr_intervals)
            metrics.update(time_metrics)
        except Exception as e:
            logger.error(f"Error calculating time domain metrics: {e}")
            raise

        # Frequency domain
        try:
            freq_metrics = self.calculate_frequency_domain(rr_intervals)
            metrics.update(freq_metrics)
        except Exception as e:
            logger.error(f"Error calculating frequency domain metrics: {e}")
            raise

        return metrics

    def check_data_quality(
        self,
        rr_intervals: List[float],
        max_hr: float = 200.0,
        min_hr: float = 30.0
    ) -> Dict[str, any]:
        """
        Check RR interval data quality and detect artifacts.

        Args:
            rr_intervals: List of R-R intervals in milliseconds
            max_hr: Maximum physiological HR (bpm)
            min_hr: Minimum physiological HR (bpm)

        Returns:
            Dictionary with quality metrics:
            - is_valid: Boolean indicating if data is acceptable
            - artifact_count: Number of potential artifacts
            - artifact_percentage: Percentage of data that are artifacts
            - issues: List of quality issues
        """
        rr_array = np.array(rr_intervals)
        issues = []
        artifact_count = 0

        # Convert HR limits to RR intervals (ms)
        max_rri = 60000.0 / min_hr  # Maximum RR interval
        min_rri = 60000.0 / max_hr  # Minimum RR interval

        # Check for physiologically impossible values
        invalid_rri = (rr_array > max_rri) | (rr_array < min_rri)
        artifact_count += np.sum(invalid_rri)
        if np.any(invalid_rri):
            issues.append(f"Found {np.sum(invalid_rri)} physiologically impossible RR intervals")

        # Check for extreme successive differences (likely artifacts)
        successive_diffs = np.abs(np.diff(rr_array))
        extreme_diffs = successive_diffs > 300  # >300ms change is suspicious
        artifact_count += np.sum(extreme_diffs)
        if np.any(extreme_diffs):
            issues.append(f"Found {np.sum(extreme_diffs)} extreme successive differences")

        # Calculate artifact percentage
        total_intervals = len(rr_intervals)
        artifact_percentage = (artifact_count / total_intervals) * 100 if total_intervals > 0 else 0

        # Data is valid if <5% artifacts and sufficient length
        is_valid = artifact_percentage < 5.0 and total_intervals >= 60

        if artifact_percentage >= 5.0:
            issues.append(f"High artifact rate: {artifact_percentage:.1f}%")
        if total_intervals < 60:
            issues.append(f"Insufficient data: only {total_intervals} intervals")

        return {
            'is_valid': is_valid,
            'artifact_count': int(artifact_count),
            'artifact_percentage': float(artifact_percentage),
            'total_intervals': int(total_intervals),
            'issues': issues
        }
