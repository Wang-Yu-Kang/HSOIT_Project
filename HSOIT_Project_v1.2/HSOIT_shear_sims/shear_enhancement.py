# Simulation of shear enhancement function B(rho, sigma_v) for galaxy clusters
# This script computes B_low_rho and B_high_rho as functions of velocity dispersion sigma_v.

import math
import csv

# Model parameters (tuned to H-SOIT predictions)
B_max = 0.30       # maximum gravity boost (~30% at extreme conditions)
sigma_ref = 900.0  # reference velocity dispersion (km/s) for mid-range
f_high = 0.15      # suppression factor in high-density environment

def B_low(sigma_v):
    """Shear enhancement B for low-density environment."""
    # Use a smooth tanh-based increase
    return 1.0 + B_max * math.tanh(sigma_v / 2064.0)

def B_high(sigma_v):
    """Shear enhancement B for high-density environment."""
    # High-density: scaled down by factor f_high
    return 1.0 + f_high * B_max * math.tanh(sigma_v / 2064.0)

# Generate shear enhancement values for sigma_v from 0 to 4000 km/s (step 50)
with open("shear_enhancement.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["sigma_v (km/s)", "B_low_rho", "B_high_rho"])
    for sigma in range(0, 4001, 50):
        writer.writerow([sigma, f"{B_low(sigma):.3f}", f"{B_high(sigma):.3f}"])