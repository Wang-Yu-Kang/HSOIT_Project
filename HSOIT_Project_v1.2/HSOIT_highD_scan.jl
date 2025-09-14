# High-dimensional topological flux parameter scan (twin-peak model)
# This Julia script scans quantized flux integers (n1, n2) and computes corresponding twin-peak amplitude parameters A1, A2.

# Define parameter mapping function (based on E8 topology embedding)
function flux_to_amplitudes(n1::Int, n2::Int)
    # Example formula: A1 increases roughly linearly with n1 (with minimum offset), A2 with n2.
    # Include cross-coupling so that large n1, n2 enhance each other.
    A1_base = 0.01 * n1
    if n1 == 0 && n2 > 0
        A1_base = 0.01  # minimal A1 if any flux exists
    end
    # Cross-term coupling (enhance A1 for large n2)
    A1_cross = 0.001 * n1 * n2
    # Small non-linear correction for large n1
    A1_nl = 0.000208 * n1^2
    A1 = A1_base + A1_cross + A1_nl

    # A2 from n2
    A2_base = 0.02 * n2
    # Cross-term coupling (enhance A2 for large n1)
    A2_cross = 0.001404 * n1 * n2
    # (Optional small non-linear correction for A2 using n1^2 or n2^2 if needed)
    A2 = A2_base + A2_cross

    return round(A1, digits=3), round(A2, digits=3)
end

# Open output CSV file
open("magnetic_flux_to_A_params.csv", "w") do file
    # Write header
    write(file, "# n1, n2, A1, A2\n")
    # Loop over flux integer combinations (0 <= n1, n2 <= 49)
    for n1 in 0:49
        for n2 in 0:49
            A1, A2 = flux_to_amplitudes(n1, n2)
            write(file, "$(n1), $(n2), $(A1 < 0 ? "-" : "")$(A1), $(A2 < 0 ? "-" : "")$(A2)\n")
        end
    end
end