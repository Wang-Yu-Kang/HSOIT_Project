import csv, math
import numpy as np

# Data structure to hold QNM template entries (by mode and spin)
qnm_data = {}         # keys: (l, n), value: list of entries with fields below
spins_by_mode = {}    # record available spin values for each mode (for interpolation)

def load_QNM_templates(csv_path):
    """Load the QNM template data from CSV into memory."""
    global qnm_data, spins_by_mode
    qnm_data.clear()
    spins_by_mode.clear()
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse numeric values from each column
            a = float(row['a'])
            l = int(row['l'])
            n = int(row['n'])
            omega0_R = float(row['omega0_R'])
            omega0_I = float(row['omega0_I'])
            alpha1 = float(row['alpha1'])
            beta1  = float(row['beta1'])
            alpha2 = float(row['alpha2']) if row['alpha2'] != '' else 0.0
            beta2  = float(row['beta2'])  if row['beta2']  != '' else 0.0
            mode_key = (l, n)
            # Initialize mode list if not exists
            if mode_key not in qnm_data:
                qnm_data[mode_key] = []
            qnm_data[mode_key].append({
                'a': a,
                'omega0_R': omega0_R,
                'omega0_I': omega0_I,
                'alpha1': alpha1,
                'alpha2': alpha2,
                'beta1': beta1,
                'beta2': beta2
            })
    # Sort entries for each mode by spin a
    for mode_key, entries in qnm_data.items():
        entries.sort(key=lambda entry: entry['a'])
        spins_by_mode[mode_key] = [entry['a'] for entry in entries]
    print(f"Loaded QNM data for {len(qnm_data)} modes.")

def interpolate_entry(mode_key, a):
    """Interpolate QNM data for mode (l, n) at given spin a."""
    entries = qnm_data.get(mode_key)
    if entries is None:
        raise ValueError(f"Mode {mode_key} not found in QNM data.")
    # If exact match exists, return it
    for entry in entries:
        if abs(entry['a'] - a) < 1e-6:
            return entry
    # If a outside range, raise error
    min_a = entries[0]['a']
    max_a = entries[-1]['a']
    if a < min_a or a > max_a:
        raise ValueError(f"Spin value {a} out of range [{min_a}, {max_a}] for mode {mode_key}.")
    # Otherwise interpolate linearly between nearest entries
    # Find first entry with spin >= a
    idx_higher = 0
    while entries[idx_higher]['a'] < a:
        idx_higher += 1
    idx_lower = idx_higher - 1
    e_low = entries[idx_lower]
    e_high = entries[idx_higher]
    a_low = e_low['a']
    a_high = e_high['a']
    frac = (a - a_low) / (a_high - a_low)
    # Interpolate each field
    def lerp(x, y):
        return x + frac * (y - x)
    interp_entry = {}
    interp_entry['a'] = a
    for field in ['omega0_R', 'omega0_I', 'alpha1', 'alpha2', 'beta1', 'beta2']:
        interp_entry[field] = lerp(e_low[field], e_high[field])
    return interp_entry

def get_frequency(a, l, n, eps):
    """Return the complex QNM frequency for given spin a, mode (l, n), and hair fraction eps."""
    mode_key = (l, n)
    if mode_key not in qnm_data:
        raise RuntimeError("QNM data not loaded or mode not available.")
    entry = interpolate_entry(mode_key, a)
    # Compute complex frequency: ω = ω0 + α1*eps + α2*eps^2 (real part), similar for imaginary part
    omega_R0 = entry['omega0_R']
    omega_I0 = entry['omega0_I']
    alpha1 = entry['alpha1']
    beta1 = entry['beta1']
    alpha2 = entry.get('alpha2', 0.0)
    beta2 = entry.get('beta2', 0.0)
    # Frequency shifts (assuming eps small)
    delta_omega_R = alpha1 * eps + alpha2 * (eps ** 2)
    delta_omega_I = beta1  * eps + beta2  * (eps ** 2)
    omega_R = omega_R0 + delta_omega_R
    omega_I = omega_I0 + delta_omega_I
    return complex(omega_R, omega_I)

def generate_waveform(mass, spin, eps, modes=[(2, 0)], duration=0.1, dt=1e-5):
    """
    Generate a ringdown waveform for given BH mass (M=1 in geometric units by default), spin, and hair fraction eps.
    Modes is a list of (l, n) modes to include (default: fundamental l=2, n=0).
    Returns time array and strain array.
    """
    # Note: If mass != 1, scale time by M (physical time = t * (G M / c^3)) if needed (not implemented here).
    t = np.arange(0, duration, dt)
    h_total = np.zeros_like(t, dtype=np.float64)
    for (l, n) in modes:
        omega = get_frequency(spin, l, n, eps)  # complex frequency
        omega_R = omega.real
        omega_I = omega.imag  # (negative for decaying mode)
        # Assume unit amplitude and zero initial phase for each mode
        A_ln = 1.0
        # Contribution: Re[A * exp(i ω_R t) * exp(ω_I t)] = A * exp(ω_I t) * cos(ω_R t)
        h_mode = A_ln * np.exp(omega_I * t) * np.cos(omega_R * t)
        h_total += h_mode
    return t, h_total

# If run as script, demonstrate usage
if __name__ == "__main__":
    # Load QNM data (CSV file in data directory)
    load_QNM_templates("data/qnm_freq_shifts.csv")
    # Example query: fundamental mode (l=2,n=0) at a=0.7 with small hair eps=0.01
    omega = get_frequency(a=0.7, l=2, n=0, eps=0.01)
    print(f"QNM frequency for a=0.7, l=2, n=0, eps=0.01: ω = {omega.real:.4f} + {omega.imag:.4f} i")
    # Generate a sample ringdown waveform for that mode
    t, h = generate_waveform(mass=1.0, spin=0.7, eps=0.01, modes=[(2, 0)], duration=0.05, dt=1e-5)
    # (The waveform data t, h could be saved or plotted as needed)