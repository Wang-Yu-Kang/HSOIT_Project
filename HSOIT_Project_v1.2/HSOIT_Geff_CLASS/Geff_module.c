/*****************  HSOIT_Geff_CLASS: Geff_module.c  ************************
 * This module extends the CLASS background to include a time-varying 
 * gravitational constant G_eff(a) with a double-peaked functional form.
 * The model is: 
 *    G_eff(a) = 1 
 *              + A1 * exp[- ((ln a - z1) / s)^2 ] 
 *              + A2 * exp[- ((ln a - z2) / s)^2 ],
 * where A1, A2 set the peak amplitudes and z1, z2 set the center positions 
 * (in terms of ln(a)), and s sets the width of both Gaussian peaks.
 * All parameters A1, A2, z1, z2 (and s) are treated as input variables.
 ***************************************************************************/

#include "background.h"   /* CLASS background structure and definitions */
#include "common.h"      /* CLASS common utilities (for error handling, etc.) */

/* Define default values or declare global variables for G_eff parameters */
#ifndef GEFF_DEFAULT_S
  #define GEFF_DEFAULT_S  1.0  /* default peak width in ln(a) units, if not set */
#endif

/** 
 * Function : background_geff
 * Calculate the effective gravitational constant G_eff at scale factor a.
 *
 * Returns:
 *   - G_eff (dimensionless, normalized to 1 for standard Newton’s constant)
 */
double background_geff(struct background *pba, double a) {
    /* Ensure a is positive to avoid log domain error */
    class_test(a <= 0.0, pba->error_message,
               "scale factor a = %e is non-positive in background_geff()", a);
    double ln_a = log(a);
    
    /* Retrieve parameters (assumed stored in background structure or use defaults) */
    double A1 = pba->Geff_A1;   /* amplitude of first peak */
    double A2 = pba->Geff_A2;   /* amplitude of second peak */
    double z1 = pba->Geff_z1;   /* ln(a) center of first peak */
    double z2 = pba->Geff_z2;   /* ln(a) center of second peak */
    double s  = pba->Geff_s;    /* width of peaks in ln(a) */
    
    /* If not initialized, use default width */
    if (s <= 0.0) {
        s = GEFF_DEFAULT_S;
    }
    
    /* Compute Gaussian terms for each peak */
    double term1 = A1 * exp(- pow((ln_a - z1) / s, 2));
    double term2 = A2 * exp(- pow((ln_a - z2) / s, 2));
    
    /* Effective G = base value 1 + contributions from peaks */
    double Geff = 1.0 + term1 + term2;
    
    return Geff;
}

/** 
 * (Optional initialization function)
 * background_geff_init: Initialize G_eff parameters in the background.
 *
 * This could be called during background initialization to set up default or 
 * user-provided values. For example, it might read input values for A1, A2, z1, z2.
 */
int background_geff_init(struct background *pba) {
    /* Example: set default values if not provided */
    pba->Geff_A1 = 0.0;
    pba->Geff_A2 = 0.0;
    pba->Geff_z1 = 0.0;
    pba->Geff_z2 = 0.0;
    pba->Geff_s  = GEFF_DEFAULT_S;
    /* (In actual implementation, override these with values from input file if given) */
    return _SUCCESS_;
}