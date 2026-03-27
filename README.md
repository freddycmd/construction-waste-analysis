# 🏗️ Construction Material Usage & Waste Optimization

> Data-driven analysis of 500 construction project records to identify waste inefficiencies and recommend optimization strategies.

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| Total Records | 500 (99 unique projects) |
| Materials | Concrete, Steel, Asphalt, Wood |
| Suppliers | Supplier A, B, C, D |
| Project Types | Residential, Commercial, Infrastructure |
| **Overall Waste Rate** | **12.89%** |
| **Total Waste Cost** | **$4,111,396** |
| **Potential Savings** | **$1,525,292 (37.1%)** |

## 🔍 Key Findings

### 1. Material Waste is Uniformly High (~12-13%)
All four materials show similar average waste rates (12.5–13.1%), suggesting the problem is **systemic** rather than material-specific:
- **Steel** — Highest at 13.1% avg waste → $976K wasted
- **Wood** — 12.9% avg → $1.02M wasted
- **Concrete** — 12.6% avg → **$1.24M wasted** (largest cost share at 30.2%)
- **Asphalt** — 12.5% avg → $875K wasted

### 2. Supplier Performance Varies by Material
No single supplier is best across all materials — **the optimal supplier depends on the material**:

| Material | Best Supplier | Waste % | Worst Supplier | Waste % | Gap |
|----------|--------------|---------|----------------|---------|-----|
| Concrete | Supplier D | 11.4% | Supplier B | 13.2% | 1.9 pp |
| Steel | Supplier D | 12.2% | Supplier C | 13.7% | 1.6 pp |
| Asphalt | Supplier C | 11.7% | Supplier A | 13.1% | 1.3 pp |
| Wood | Supplier A | 11.8% | Supplier D | 14.6% | 2.7 pp |

### 3. Pareto Concentration
Top ~40% of records account for 80% of total waste cost — **targeted intervention on these projects yields outsized returns**.

### 4. 74 High-Waste Records (≥18%) Cost $955K
These extreme cases represent 14.8% of records but **23.2% of total waste cost**. The worst single record: Project 1000 (Wood, Supplier C) wasted **$41,379**.

### 5. Unit Cost Doesn't Correlate with Waste
Correlation between Unit_Cost and Waste_% is near zero (r=0.033), meaning **expensive materials aren't wasted more or less than cheap ones** — the problem is process, not material value awareness.

## 💰 Optimization Strategies

### Savings by Reaching Industry Benchmarks

| Material | Target | Projects Affected | Current Cost | Savings |
|----------|--------|-------------------|-------------|---------|
| Concrete | 8% | 117 (77%) | $1.11M | **$486,189** |
| Steel | 8% | 100 (82%) | $900K | **$403,105** |
| Asphalt | 8% | 91 (83%) | $809K | **$344,701** |
| Wood | 10% | 82 (70%) | $845K | **$291,296** |
| **Total** | | | | **$1,525,292** |

### Actionable Recommendations

1. **Implement material-specific supplier routing** — Route Concrete/Steel orders to Supplier D, Asphalt to Supplier C, Wood to Supplier A
2. **Audit the top 74 high-waste records** (≥18%) — These alone represent $955K in waste; root-cause analysis here has highest ROI
3. **Improve demand forecasting** — Ordered_Qty and Waste_Qty are strongly correlated (r=0.84), indicating systematic over-ordering
4. **Standardize procurement across project types** — Commercial projects show slightly higher waste (12.9%) vs Infrastructure (12.5%)
5. **Set waste KPIs per project** — Flag any project exceeding 15% waste for immediate review

## 📈 Charts

| # | Chart | Description |
|---|-------|-------------|
| 01 | Waste Distribution | Box plot: waste % spread by material |
| 02 | Waste Cost by Material | Horizontal bar: total $ wasted per material |
| 03 | Supplier Performance | Grouped bar: avg waste % by supplier × material |
| 04 | Order vs Waste Scatter | Bubble chart: order size vs waste %, sized by cost |
| 05 | Project Type Waste | Grouped bar: waste % by project type × material |
| 06 | Waste Treemap | Treemap: cost breakdown by material → supplier |
| 07 | Pareto Analysis | Dual-axis: individual + cumulative waste cost |
| 08 | Waste Histogram | Overlaid histogram: waste % frequency distribution |
| 09 | Supplier Cost Stack | Stacked bar: supplier total waste cost by material |
| 10 | Unit Cost vs Waste | Scatter + OLS trendlines: cost vs waste relationship |

Interactive HTML versions are in `charts/` — open in any browser.

## 📁 Project Structure

```
├── material_waste_dataset.csv    # Source dataset (500 records)
├── analyze_real.py               # Full analysis + 10 charts
├── summary.json                  # Key metrics (machine-readable)
├── charts/
│   ├── 01–10_*.html              # Interactive Plotly charts
│   └── 01–10_*.png               # Static exports
└── README.md
```

## ▶️ Run It

```bash
pip install pandas numpy plotly matplotlib seaborn kaleido statsmodels
python analyze_real.py
```

## 🛠️ Tech Stack
- **Python** — pandas, NumPy, Plotly, statsmodels
- **Visualization** — Plotly (interactive HTML + PNG via Kaleido)
- **Analysis** — Descriptive stats, correlation, Pareto, OLS trendlines

---

*Industry context: Construction material waste typically runs 5–15% of total material cost. At 12.9% average waste, this dataset sits at the high end. Bringing waste rates down to 8–10% benchmarks would save **$1.53M** — a 37% reduction in waste spend with zero change in output quality.*
