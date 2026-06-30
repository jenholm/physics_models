# Simulation Design

## Landscapes

1D potential with quadratic base plus Gaussian well perturbations:

$$V(\phi) = \frac{1}{2} m^2 \phi^2 - \sum_i A_i \exp\left(-\frac{(\phi - \mu_i)^2}{2\sigma_i^2}\right)$$

Each well creates a vacuum basin. Wells are assigned effective physics vectors $\theta$ in `landscapes.yaml`.

## Dynamics

Langevin stochastic evolution:

$$d\phi = -\frac{V'(\phi)}{3H^2} dN + \frac{H}{2\pi} dW$$

Where $H$ is the Hubble parameter during inflation (set to 1 in the toy model).

## Sector identification

Each trajectory endpoint is assigned:
- Final field value $\phi$
- Vacuum basin ID (nearest local minimum)
- Effective physics vector $\theta$ from basin assignment

## Distance metrics

- **Field distance**: $|\phi_i - \phi_j|$
- **Ancestry distance**: graph steps through parent sectors (currently proxied by e-fold difference)
- **Effective distance**: Euclidean norm of $\theta$ vectors

## Cutoffs tested

- Number of sectors: $N \in \{100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000\}$
- E-fold limits: $N_{\max} \in \{10, 25, 50, 100, 150, 200\}$
- Field-distance limits
- Ancestry depth

## Kernels

Five kernels tested: gaussian, exponential, graph, causal_cone, same_basin.
