"""Stochastic Langevin dynamics for toy inflationary trajectories (vectorized)."""

import numpy as np
from typing import Optional


class StochasticDynamics:
    """Langevin-style evolution for inflaton field.

    d_phi = drift(phi) * dN + noise * dW

    Toy version:
        drift = -V'(phi) / (3 H^2)
        noise = H / (2*pi)
    """

    def __init__(
        self,
        landscape,
        h: float = 1.0,
        dt: float = 0.2,
        seed: Optional[int] = None,
    ):
        self.landscape = landscape
        self.h = h
        self.dt = dt
        self.rng = np.random.default_rng(seed)

    def drift(self, phi: np.ndarray) -> np.ndarray:
        return -np.array([self.landscape.gradient(p) for p in phi]) / (3 * self.h**2)

    def noise(self, phi: np.ndarray) -> np.ndarray:
        return np.full_like(phi, self.h / (2 * np.pi))

    def _vectorized_drift(self, phi: np.ndarray) -> np.ndarray:
        # Approximate gradient using grid interpolation
        phi_grid = self.landscape.phi_grid
        grad_grid = self.landscape.V_prime_grid
        idx = np.searchsorted(phi_grid, phi)
        idx = np.clip(idx, 0, len(grad_grid) - 1)
        return -grad_grid[idx] / (3 * self.h**2)

    def simulate_trajectories(
        self,
        phi0: np.ndarray,
        n_efolds: int,
        n_steps: Optional[int] = None,
    ) -> dict:
        if n_steps is None:
            n_steps = n_efolds * 5

        phi = phi0.copy()
        phi_history = np.zeros((len(phi0), n_steps + 1))
        phi_history[:, 0] = phi

        for step in range(n_steps):
            drift = self._vectorized_drift(phi)
            noise = np.full_like(phi, self.h / (2 * np.pi))
            dW = self.rng.normal(0.0, np.sqrt(self.dt), size=phi.shape)
            phi = phi + drift * self.dt + noise * dW
            phi = np.clip(phi, self.landscape.config.field_min, self.landscape.config.field_max)
            phi_history[:, step + 1] = phi

        basin_final = np.array([self.landscape.identify_basin(p) for p in phi])
        return {
            "phi_history": phi_history,
            "phi_final": phi,
            "basin_final": basin_final,
            "phi_initial": phi0,
        }
