import math

# Physical constants
k_B = 1.380649e-23  # Boltzmann constant (J/K)
ln2 = math.log(2.0)

def simulate_landauer_erasure(T, E, gamma, t_max, dt):
    """
    Simulate the erasure of a single bit (two-level system) coupled to a heat bath at temperature T.

    - T: temperature of the bath in Kelvin.
    - E: energy gap of the two-level system (Joules). The excited state has energy E, ground state 0.
    - gamma: base transition rate (1/s) for spontaneous relaxation at T=0.
    - t_max: simulation time (s).
    - dt: time step (s).

    Returns: (times, P_excited, Q_env)
      times: list of time points,
      P_excited: list of excited state population over time,
      Q_env: total heat dissipated to environment up to each time point.
    """
    # Derived parameters
    # Thermal occupancy of energy E at temperature T (Bose-Einstein statistic for simplicity)
    if T <= 0:
        n_th = 0.0
    else:
        # Thermal occupation number for energy E (approximation using Bose-Einstein formula)
        # For a two-level system, use f = 1/(exp(E/(k_B T)) - 1). Treat bath coupling similarly.
        n_th = 1.0 / (math.exp(E/(k_B * T)) - 1.0) if E/(k_B * T) > 1e-6 else 0.0

    gamma_down = gamma * (n_th + 1.0)  # decay rate (|1> -> |0|)
    gamma_up   = gamma * n_th          # excitation rate (|0> -> |1>) from bath

    # Initialize state: at t=0, bit is in a maximally mixed state (50% in |1>)
    P_excited = 0.5
    system_energy = P_excited * E
    Q_env = 0.0  # cumulative heat released to environment

    times = []
    P_values = []
    Q_values = []

    for step in range(int(t_max/dt) + 1):
        t = step * dt
        # Record current state
        times.append(t)
        P_values.append(P_excited)
        Q_values.append(Q_env)

        # Compute population change (Euler integration of master equation)
        dP_dt = -gamma_down * P_excited + gamma_up * (1.0 - P_excited)
        P_excited += dP_dt * dt
        # Bound P_excited between 0 and 1
        if P_excited < 0:
            P_excited = 0.0
        if P_excited > 1:
            P_excited = 1.0

        # Compute instantaneous heat flow:
        # When population changes by dP, energy change of system = d(P_excited)*E.
        # If P_excited decreases, system energy lost is released as heat to bath.
        # If P_excited increases, heat is absorbed from bath (Q_env decreases).
        dE_system = (P_excited * E) - system_energy
        system_energy += dE_system
        Q_env -= dE_system  # subtract change in system energy (if system loses energy, Q_env gains)

    return times, P_values, Q_values

def compute_chi0_from_theory(c=None):
    """
    Compute the entropy tax coefficient chi0 from the theoretical formula, if available.

    If central charge c is provided (from CFT or high-dimensional topology), use χ0 = c/(12π).
    Otherwise, return the default chi0 from the paper (~0.02 for typical parameters).
    """
    if c is not None:
        return c / (12.0 * math.pi)
    # Default value from H-SOIT analysis (~0.01–0.02 range)
    return 0.02

def compute_chi0_from_simulation(T, E, gamma, t_max, dt):
    """
    Estimate χ0 by simulating an erasure at temperature T and comparing dissipated heat to Landauer's limit.

    Returns the estimated chi0 = (Q_actual / Q_min) - 1.
    """
    times, P, Q = simulate_landauer_erasure(T, E, gamma, t_max, dt)
    Q_actual = Q[-1]  # total heat at end of simulation
    Q_min = k_B * T * ln2  # Landauer limit for erasing one bit
    if Q_min == 0:
        return None
    chi0_est = (Q_actual / Q_min) - 1.0
    return chi0_est

# Example usage (if run as a script):
if __name__ == "__main__":
    # Example: simulate erasure at T = 300 mK
    T = 0.300  # K
    E = 1.0e-20  # J (choose energy scale; arbitrary for demo)
    gamma = 1e3  # 1000 s^-1 base decay rate
    t_max = 0.01  # 0.01 s simulation
    dt = 1e-5    # time step

    est_chi = compute_chi0_from_simulation(T, E, gamma, t_max, dt)
    print(f"Simulated chi0 at T={T} K: {est_chi:.3f}")
    # Theoretical chi0 (using default or a given c)
    print(f"Theoretical chi0 (default): {compute_chi0_from_theory():.3f}")