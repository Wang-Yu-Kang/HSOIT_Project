/*
 * twinpeak_geff.c - Plugin for CLASS to implement a time-varying Newton's constant G_eff(a)
 * 
 * This module provides a function G_eff(a) with two "twin-peak" features at scale factors a1 and a2.
 * The amplitude of each peak is set by parameters A1 and A2, and locations by ln(a1) = z1, ln(a2) = z2.
 * (Here z1, z2 correspond to entries in Symbols_and_Abbr.md for twin-peak positions.)
 */

#include <math.h>

/* Default twin-peak model parameters (can be adjusted as needed) */
static const double A1 = 0.10;    // amplitude of first peak (fractional increase in G)
static const double A2 = 0.05;    // amplitude of second peak
static const double z1 = -8.0;    // ln(a) location of first peak (early Universe peak)
static const double z2 = -0.5;    // ln(a) location of second peak (late-time peak)
static const double width1 = 0.5; // width of first peak (in ln(a) units)
static const double width2 = 0.5; // width of second peak

/* Function to compute G_eff/G_N at given scale factor a */
double G_eff_over_GN(double a) {
    double x = log(a);
    // Two Gaussian peaks in ln(a):
    double peak1 = A1 * exp(-0.5 * pow((x - z1) / width1, 2));
    double peak2 = A2 * exp(-0.5 * pow((x - z2) / width2, 2));
    double Geff_ratio = 1.0 + peak1 + peak2;
    return Geff_ratio;
}

/* Example: modify CLASS background evolution to use G_eff */
double hubble_with_Geff(double a, double rho_tot) {
    // Original Friedmann: H^2 = (8πG/3) * rho_tot
    // Here we replace G by G_eff(a):
    const double G_N = 6.67430e-11; // Newton's G (in SI units, if rho_tot in SI as well)
    double Geff = G_N * G_eff_over_GN(a);
    double H_sq = (8.0 * M_PI * Geff / 3.0) * rho_tot;
    if (H_sq < 0) H_sq = 0;
    return sqrt(H_sq);
}

/*
 * Integration with CLASS:
 * To use this plugin, incorporate G_eff_over_GN(a) into CLASS where gravitational constant appears.
 * For example, in CLASS's background.c, multiply relevant density terms by G_eff_over_GN(a).
 * Ensure to recompile CLASS after adding this module.
 */