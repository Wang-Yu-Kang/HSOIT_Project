# HSOIT Project v1.2 — Code & Data for *H‑SOIT 23.8.3 Technical Manual – OIF Extension*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.PACKAGE_CONCEPT.svg)](https://doi.org/10.5281/zenodo.PACKAGE_CONCEPT)

**Code+Data (this version):** https://doi.org/10.5281/zenodo.PACKAGE_VERSION  
**Code+Data – concept DOI (latest):** https://doi.org/10.5281/zenodo.PACKAGE_CONCEPT

**Preprint (this version):** https://doi.org/10.5281/zenodo.PREPRINT_VERSION  
**Preprint – concept DOI (series):** https://doi.org/10.5281/zenodo.PREPRINT_CONCEPT

---

## Contents
- `HSOIT_Geff_CLASS/` — CLASS plugin to evolve \(G_{\mathrm{eff}}(a)\)
- `HSOIT_BHwaveforms/` — QNM frequency DB and waveform tools
- `HSOIT_shear_sims/` — shear‑enhancement simulations
- `entropy_tax.py` — entropy‑tax simulation
- `highD_scan.jl` — high‑dimensional parameter scans
- `data/` — CSVs for all figures (β‑function, entropy tax, shear enhancement, QNM shifts)
- `figures/` — rendered figures (auto‑generated)
- `scripts/`, `configs/`, `Symbols_and_Abbr.md`, `LICENSE.txt`, `CHANGELOG.md`

## Requirements
- Python ≥ 3.10 (recommended: 3.11+)
- Julia ≥ 1.9
- CLASS ≥ 2.7 (only if reproducing cosmology runs)
- OS packages: a C/C++ toolchain; `fftw`, `gsl` (for CLASS builds)

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# (Optional) Build CLASS; see HSOIT_Geff_CLASS/README.md
julia --project -e 'using Pkg; Pkg.instantiate()'

Reproduce the paper
   •   Fig. D–1 (β-function fixed point)
python scripts/resum_beta.py → reads data/beta_function_coeffs.csv, writes figures/Figure_D1_fixed_point_curve.png.
   •   Fig. H–1 (shear enhancement (B(\rho,\sigma_v)))
python HSOIT_shear_sims/run_shear.py --cfg configs/h1.yaml
   •   Fig. M–1 (E8 embedding samples)
julia highD_scan.jl --out data/m1_samples.csv

All CSV ↔ figure mappings are documented in each submodule README; checksums accompany datasets under data/.

Data provenance & license
   •   Code: MIT License (LICENSE.txt)
   •   Data: CC BY 4.0 unless noted; each CSV lists its generation script & checksum.

How to cite
   •   Preprint: Wang, Y.-K., H‑SOIT 23.8.3 Technical Manual – OIF Extension. Zenodo. https://doi.org/10.5281/zenodo.PREPRINT_VERSION
(Latest in series: https://doi.org/10.5281/zenodo.PREPRINT_CONCEPT)
   •   Code+Data package: Wang, Y.-K., HSOIT Project v1.2 (Code+Data). Zenodo. https://doi.org/10.5281/zenodo.PACKAGE_VERSION
(Concept DOI: https://doi.org/10.5281/zenodo.PACKAGE_CONCEPT)

Contact

Yu‑Kang Wang · ORCID: 0009‑0002‑0401‑5755 · Wang‑Yu‑Kang@iaaiaa.org.tw