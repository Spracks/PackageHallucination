# We Have a Package for You!  
_A Comprehensive Analysis of Package Hallucinations by Code-Generating LLMs_

[![Conference](https://img.shields.io/badge/Conference-USENIX%20Security%20'25-blue)](https://www.usenix.org/conference/usenixsecurity25)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data](https://img.shields.io/badge/Data-Zenodo-4c7e9b.svg)](https://zenodo.org/records/14676377)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14676377.svg)](https://doi.org/10.5281/zenodo.14676377)

This repository contains the **code, data, and instructions** for reproducing the experiments and results from our paper:

> **We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs**  
> Joseph Spracklen, Raveen Wijewickrama, A H M Nazmus Sakib, Anindya Maiti, Bimal Viswanath, Murtuza Jadliwala  
> In *Proceedings of the USENIX Security Symposium*, 2025.  
> [📄 Paper PDF](https://www.usenix.org/system/files/conference/usenixsecurity25/sec25cycle1-prepub-742-spracklen.pdf)

---

## 🔦 Highlights (TL;DR)
- Large-scale study across **16** LLMs (commercial + open-source), **Python** and **JavaScript**  
- **576,000** code samples analyzed; **19.7%** of recommended packages were hallucinations  
- **205,474** unique hallucinated package names discovered  
- Effective mitigations evaluated: **RAG**, **self-detection**, **fine-tuning** (largest reduction from fine-tuning)

---

## 📌 Table of Contents
- [Overview](#-overview)
- [Repository Structure](#-repository-structure)
- [Setup](#-setup)
- [Usage](#-usage)
- [Data](#-data)
- [Reproducing Results](#-reproducing-results)
- [Mitigation Experiments](#-mitigation-experiments)
- [Hardware & Runtime Notes](#-hardware--runtime-notes)
- [Security & Ethics](#-security--ethics)
- [Troubleshooting](#-troubleshooting)
- [Citation](#-citation)
- [License](#-license)
- [Contact](#-contact)

---

## 🔍 Overview
Package hallucinations occur when an LLM generates code that references a **non-existent package** (e.g., via `pip install xyz` or `npm install xyz` where `xyz` does not exist).  
This creates a **software supply-chain risk**: adversaries can upload a malicious package using that hallucinated name.

This repo provides:
- End-to-end pipeline to **generate code**, **extract package names**, and **measure hallucinations**
- Prompt datasets (Stack Overflow–derived and LLM-generated)
- Code to reproduce **figures/tables** and **mitigation experiments**

---

## 📂 Repository Structure
```bash
.
├── run_test.py                 # Runs a full hallucination detection experiment
├── Models/                     # Place tested models here (one default model included)
├── Data/                       # Prompt datasets & per-language resources
│   ├── Python/
│   │   ├── LLM_AT.json
│   │   ├── LLM_LY.json
│   │   ├── SO_AT.json
│   │   └── SO_LY.json
│   └── JavaScript/
│       ├── LLM_AT.json
│       ├── LLM_LY.json
│       ├── SO_AT.json
│       └── SO_LY.json
├── Tests/                      # Output directory for experiment results (starts empty)
├── Mitigation/                 # Mitigation experiments
│   ├── run_model_RAG.py
│   ├── run_model_SD.py
│   ├── run_model_combined.py
│   ├── Data/                   # RAG DB + build data
│   ├── Fine_tuned/             # Fine-tuned & quantized models used in mitigation testing
│   └── RAG_setup.py            # Builds the vector DB from Mitigation/Data
├── Plots/                      # Code and data to reproduce paper figures
├── environment.yml             # Conda environment
├── requirements.txt            # (Optional) pip dependencies
└── README.md
```

---

## ⚙️ Setup

### 1) Clone
```bash
git clone https://github.com/Spracks/PackageHallucination.git
cd PackageHallucination
```

### 2) Create environment
Using Conda (recommended):
```bash
conda env create -f environment.yml
conda activate pkg-hallucination
```

Or using pip:
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The environment listed is bloated, really just need PyTorch + transformers and the associated dependencies.

---

## 🚀 Usage

Run a **full hallucination detection** experiment for one model:
```bash
python run_test.py DeepSeek_1B --language Python
# or
python run_test.py DeepSeek_1B --language JavaScript
```

**What it does**
- Generates code for prompts in `Data/<LANG>/`
- Extracts package names via the paper’s three heuristics
- Compares against master lists to mark hallucinations
- Writes results/artifacts under `Tests/`

**Notes**
- Ensure your chosen model is available under `Models/`
- End-to-end runs can take **24–72 hours** depending on model size and hardware

---

## 📊 Data

**Included prompt datasets (per language):**
- `LLM_AT.json` – LLM-generated prompts based on **all-time** most popular packages  
- `LLM_LY.json` – LLM-generated prompts based on **last-year** most popular packages  
- `SO_AT.json` – Top Stack Overflow questions (all-time)  
- `SO_LY.json` – Top Stack Overflow questions (last-year)

Each language directory also contains the **master list of valid package names** used for detection.

> We **do not** publish the master list of hallucinated package names or per-prompt detailed results (see [Security & Ethics](#-security--ethics)). Verified researchers can request access.

---

## 📈 Reproducing Results

Reproduce main tables/figures by re-running experiments and then building plots:

```bash
# 1) Run experiments (example)
python run_test.py DeepSeek_1B --language Python
python run_test.py CodeLlama_7B --language Python
# ... (repeat for desired model/language combinations)

# 2) Build figures
cd Plots
python reproduce_figures.py
```

Where applicable, figure scripts read from `Tests/` to regenerate the paper plots.

---

## 🛠 Mitigation Experiments

We provide three mitigation strategies:

1. **RAG (Retrieval-Augmented Generation)**  
   Augments prompts with retrieved package-context from a vector DB built from package descriptions.

   ```bash
   # Build RAG DB (once)
   python Mitigation/RAG_setup.py
   # Run RAG experiment
   python Mitigation/run_model_RAG.py DeepSeek_1B --language Python
   ```

2. **Self-Detection / Self-Refinement**  
   The model checks its own suggested package list; if invalid, regenerate with constraints.

   ```bash
   python Mitigation/run_model_SD.py CodeLlama_7B --language Python
   ```

3. **Fine-Tuning**  
   Fine-tune on valid (non-hallucinated) package recommendations derived from the pipeline.

   ```bash
   # Use the fine-tuned checkpoints under Mitigation/Fine_tuned/
   python Mitigation/run_model_combined.py DeepSeek_1B --language Python
   ```

> See paper for comparative results; fine-tuning produced the **largest** hallucination reduction.

---

## 🧰 Hardware & Runtime Notes
- Open-source models were evaluated in **quantized** form to mimic realistic hardware constraints.
- A single full run can take **24–72 hours** depending on model size/GPU availability.
- For reproducibility, stick to the provided `environment.yml` and keep decoding parameters consistent unless you are explicitly testing RQ2-style variations.

---

## 🔒 Security & Ethics
- We **do not** publicly release:
  - The master list of hallucinated package names
  - Per-prompt detailed results
- Rationale: releasing these could enable **package confusion attacks** at scale.
- **Access policy:** verified researchers may request full results for academic use.  
- See the paper’s **Ethics Considerations** for additional detail.

---

## 🧪 Troubleshooting
- **Environment fails to resolve:** ensure you’re using the listed CUDA/PyTorch versions in `environment.yml`.
- **Model not found:** confirm the checkpoint is placed under `Models/` and the name matches your CLI arg.
- **Very slow runs:** you’re likely on CPU; use a CUDA GPU where possible.
- **Different hallucination rates than reported:** minor variation is expected across hardware/versions; ensure decoding params and temperatures match defaults in the code.

---

## 📜 Citation
If you use this repository, please cite:
```bibtex
@inproceedings{spracklen2025packagehallucination,
  title     = {We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs},
  author    = {Joseph Spracklen and Raveen Wijewickrama and A H M Nazmus Sakib and Anindya Maiti and Bimal Viswanath and Murtuza Jadliwala},
  booktitle = {USENIX Security Symposium},
  year      = {2025}
}
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---

## 📬 Contact
Questions or collaboration:
- **Joseph Spracklen** — joseph.spracklen@utsa.edu  
- Or open an issue on the repository
