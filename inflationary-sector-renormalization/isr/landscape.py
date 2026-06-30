"""Toy inflationary landscape potential and basin identification."""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class LandscapeConfig:
    """Configuration for the toy inflationary landscape."""
    base_type: str = "quadratic"
    mass_squared: float = 0.1
    wells: list = None  # List of (amplitude, mu, sigma)
    bumps: list = None
    field_min: float = -8.0
    field_max: float = 8.0
    resolution: int = 2000

    def __post_init__(self):
        if self.wells is None:
            self.wells = []
        if self.bumps is None:
            self.bumps = []


class InflationaryLandscape:
    """Toy 1D inflationary potential: V(phi) = base + sum of Gaussian wells/bumps."""

    def __init__(self, config: LandscapeConfig):
        self.config = config
        self.phi_grid = np.linspace(config.field_min, config.field_max, config.resolution)
        self.V_grid = self._compute_potential(self.phi_grid)
        self.V_prime_grid = self._compute_gradient(self.phi_grid)

    def _base_potential(self, phi: np.ndarray) -> np.ndarray:
        if self.config.base_type == "quadratic":
            return 0.5 * self.config.mass_squared * phi**2
        elif self.config.base_type == "quartic":
            return 0.25 * self.config.mass_squared * phi**4
        else:
            raise ValueError(f"Unknown base type: {self.config.base_type}")

    def _base_gradient(self, phi: np.ndarray) -> np.ndarray:
        if self.config.base_type == "quadratic":
            return self.config.mass_squared * phi
        elif self.config.base_type == "quartic":
            return self.config.mass_squared * phi**3
        else:
            raise ValueError(f"Unknown base type: {self.config.base_type}")

    def _compute_potential(self, phi: np.ndarray) -> np.ndarray:
        V = self._base_potential(phi)
        for amp, mu, sigma in self.config.wells:
            V -= amp * np.exp(-((phi - mu) ** 2) / (2 * sigma**2))
        for amp, mu, sigma in self.config.bumps:
            V += amp * np.exp(-((phi - mu) ** 2) / (2 * sigma**2))
        return V

    def _compute_gradient(self, phi: np.ndarray) -> np.ndarray:
        dV = self._base_gradient(phi)
        for amp, mu, sigma in self.config.wells:
            dV += amp * ((phi - mu) / sigma**2) * np.exp(-((phi - mu) ** 2) / (2 * sigma**2))
        for amp, mu, sigma in self.config.bumps:
            dV -= amp * ((phi - mu) / sigma**2) * np.exp(-((phi - mu) ** 2) / (2 * sigma**2))
        return dV

    def potential(self, phi: float) -> float:
        idx = np.searchsorted(self.phi_grid, phi)
        idx = np.clip(idx, 0, len(self.V_grid) - 1)
        return self.V_grid[idx]

    def gradient(self, phi: float) -> float:
        idx = np.searchsorted(self.phi_grid, phi)
        idx = np.clip(idx, 0, len(self.V_prime_grid) - 1)
        return self.V_prime_grid[idx]

    def identify_basin(self, phi: float) -> int:
        """Assign a field value to a vacuum basin based on nearest local minimum."""
        idx = np.searchsorted(self.phi_grid, phi)
        idx = np.clip(idx, 0, len(self.phi_grid) - 1)
        local_window = max(1, int(0.2 * len(self.phi_grid)))
        start = max(0, idx - local_window)
        end = min(len(self.phi_grid), idx + local_window)
        window_phi = self.phi_grid[start:end]
        window_V = self.V_grid[start:end]
        # Find all local minima in window
        minima = []
        for i in range(1, len(window_V) - 1):
            if window_V[i] < window_V[i-1] and window_V[i] < window_V[i+1]:
                minima.append(window_phi[i])
        if not minima:
            # Fallback: closest well center
            well_centers = [mu for _, mu, _ in self.config.wells]
            if well_centers:
                return int(np.argmin(np.abs(np.array(well_centers) - phi)))
            return 0
        # Return basin id of nearest minimum
        distances = np.abs(np.array(minima) - phi)
        nearest_min = minima[int(np.argmin(distances))]
        if self.config.wells:
            return int(np.argmin(np.abs([mu for _, mu, _ in self.config.wells] - nearest_min)))
        return 0

    def compute_barrier_distance(self, basin_a: int, basin_b: int) -> float:
        """Compute barrier height between two basins."""
        if basin_a == basin_b:
            return 0.0
        phi_a = self.config.wells[basin_a][1]
        phi_b = self.config.wells[basin_b][1]
        midpoint = (phi_a + phi_b) / 2.0
        V_mid = self.potential(midpoint)
        V_a = self.potential(phi_a)
        return max(0.0, V_mid - V_a)
