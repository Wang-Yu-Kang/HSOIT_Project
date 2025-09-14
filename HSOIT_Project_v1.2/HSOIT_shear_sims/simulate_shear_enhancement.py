import csv
import math

# Global containers for sigma_v and B values (loaded from CSV)
_sigma_values = []
_B_low_values = []
_B_high_values = []

def _load_data(csv_file="shear_enhancement.csv"):
    """
    Internal helper to load shear enhancement data from a CSV file.
    Expects columns: sigma_v, B_low_rho, B_high_rho (with a header or comments).
    Populates the global lists _sigma_values, _B_low_values, _B_high_values.
    """
    global _sigma_values, _B_low_values, _B_high_values
    _sigma_values = []
    _B_low_values = []
    _B_high_values = []
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                # Skip empty lines or comments
                if not row or row[0].strip().startswith('#'):
                    continue
                if len(row) < 3:
                    continue  # skip if incomplete data
                try:
                    sigma = float(row[0])
                    B_low = float(row[1])
                    B_high = float(row[2])
                except ValueError:
                    # skip lines that cannot be parsed to float (e.g., text headers)
                    continue
                _sigma_values.append(sigma)
                _B_low_values.append(B_low)
                _B_high_values.append(B_high)
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file '{csv_file}' not found.")

# Load data immediately on module import
_load_data()

def interpolate_B(sigma_v, mode="low"):
    """
    Interpolate the shear enhancement factor B for a given velocity dispersion sigma_v.
    
    Parameters:
        sigma_v (float): Velocity dispersion in km/s for which to interpolate B.
        mode (str): "low" for low-density scenario B_low, "high" for high-density scenario B_high.
    
    Returns:
        float: Interpolated B value (dimensionless enhancement factor).
    
    Notes:
        - If sigma_v is outside the range of the data, the function will return the boundary value 
          (no extrapolation beyond the data range is performed).
        - Linear interpolation is used between known data points.
    """
    # Ensure data is loaded
    if not _sigma_values:
        _load_data()
    # Choose the corresponding B series
    if mode == "low":
        values = _B_low_values
    elif mode == "high":
        values = _B_high_values
    else:
        raise ValueError("Mode must be 'low' or 'high'.")
    # If sigma_v is outside the data range, clamp to nearest value
    if sigma_v <= _sigma_values[0]:
        return values[0]
    if sigma_v >= _sigma_values[-1]:
        return values[-1]
    # Find interval for interpolation
    # (Linear search or binary search for simplicity; data is sorted ascending by sigma_v)
    for i in range(1, len(_sigma_values)):
        if sigma_v < _sigma_values[i]:
            # sigma_v lies between _sigma_values[i-1] and _sigma_values[i]
            sigma_low = _sigma_values[i-1]
            sigma_high = _sigma_values[i]
            B_low = values[i-1]
            B_high = values[i]
            # Linear interpolation formula
            frac = (sigma_v - sigma_low) / (sigma_high - sigma_low)
            return B_low + frac * (B_high - B_low)
    # If we reach here (which is unlikely due to earlier checks), return last value
    return values[-1]

def plot_B_vs_sigma(save_path=None):
    """
    Plot the shear enhancement factor B as a function of sigma_v for both low and high density modes.
    
    If save_path is provided, the plot will be saved to the specified file. 
    If save_path is None, the plot will be displayed interactively.
    """
    import matplotlib.pyplot as plt
    # Ensure data is loaded and available
    if not _sigma_values:
        _load_data()
    # Plot data for low and high modes
    plt.figure(figsize=(6,4))
    plt.plot(_sigma_values, _B_low_values, label="B (low density ρ)", marker='o', linestyle='-')
    plt.plot(_sigma_values, _B_high_values, label="B (high density ρ)", marker='s', linestyle='--')
    plt.xlabel("Velocity dispersion $\sigma_v$ (km/s)")
    plt.ylabel("Enhancement factor B")
    plt.title("Shear Enhancement vs. Velocity Dispersion")
    plt.legend()
    plt.tight_layout()
    if save_path:
        # Save plot to the given file path
        plt.savefig(save_path)
        plt.close()
    else:
        # Show plot interactively
        plt.show()

# Example usage (if run as a script):
if __name__ == "__main__":
    # Interpolate B for an example sigma_v
    example_sigma = 500  # km/s
    B_low_val = interpolate_B(example_sigma, mode="low")
    B_high_val = interpolate_B(example_sigma, mode="high")
    print(f"For sigma_v = {example_sigma} km/s: B_low = {B_low_val:.3f}, B_high = {B_high_val:.3f}")
    # Generate and save the plot
    plot_B_vs_sigma(save_path="shear_enhancement_plot.png")
    print("Plot saved as 'shear_enhancement_plot.png'")