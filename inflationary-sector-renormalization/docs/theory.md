# Theory

## Conceptual proposal

ISR treats other inflationary domains as **hidden sectors** of a shared inflationary field system. The observable patch, $x_0$, is one sector among many. Unobservable sectors are not counted equally; instead, their influence is integrated out through a locality-weighted measure.

## The measure

Naive counting is problematic because inflationary models can produce infinitely many unobservable pocket universes. Different regularization choices give different probability predictions.

ISR proposes replacing the global census:

$$P(\theta) = \frac{\text{count all sectors with } \theta}{\text{count all sectors}}$$

with a locality-weighted measure:

$$P_{\text{ISR}}(\theta | x_0) \propto \int dx \, P(\theta | x) \, K[d(x, x_0)]$$

where $K[d] = \exp(-d^2 / 2\ell^2)$ or a graph-distance kernel.

## Why not naive counting?

- Naive counting is sensitive to cutoff.
- It overweights runaway sectors.
- It gives no special status to sectors physically connected to our observable patch.

## Effective parameters

Hidden sectors can shift effective local parameters:

$$c_{\text{eff}} = c_0 + \Delta c_{\text{hidden}} = c_0 + \sum_i K[d(x_i, x_0)] \, \text{sector\_coupling}(x_i)$$

## Relation to stochastic inflation

The toy model borrows the Langevin dynamics discipline from stochastic inflation, where coarse-grained long-wavelength modes evolve stochastically while short-wavelength modes act as an environment. ISR uses this open quantum system / renormalization-group framing without overclaiming physical results.

## Limits

This is a toy model. Success is producing stable cutoff behavior and a rigorous sensitivity table, not proving the multiverse.
