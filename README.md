# 🏗️ Construction Material Usage & Waste Optimization

**Goal:** Reduce material waste and cost through data-driven analysis of 500 construction project records.

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| Total Records | 500 |
| Total Ordered | 504,436 units |
| Total Used | 463,457 units |
| **Total Wasted** | **40,978 units (8.1%)** |
| **Total Waste Cost** | **$8,889,316** |
| **Potential Savings** | **$4,510,481 (50.7%)** |

## 🔍 Key Findings

### Material Waste Rankings
1. **Wood** — Highest waste at 12.4% avg (industry benchmark: 8%) → $1.16M wasted
2. **Concrete** — 7.6% avg waste (benchmark: 5%) → $1.0M wasted
3. **Asphalt** — 6.0% avg waste (benchmark: 4%) → $706K wasted
4. **Steel** — Lowest waste rate at 5.6% but **highest cost impact** → **$6.03M wasted** (due to $844/unit avg cost)

### Supplier Performance
- **Best performers:** IronClad Industries (Steel, 5.0%), PavePro Inc. (Asphalt, 5.5%)
- **Worst performers:** TimberLine Co. (Wood, 13.0%), GreyCrete Co. (Concrete, 8.7%)
- Supplier spread within the same material reaches 1-2 percentage points — switching suppliers can save hundreds of thousands

### Project Type Insights
- **Residential** projects have the highest average waste (8.5%)
- **Industrial** projects are most efficient (7.2%)

### Pareto Concentration
- Top 30% of projects account for ~80% of total waste cost — targeted intervention on these projects yields outsized returns

## 💰 Optimization Strategies

| Strategy | Target | Estimated Savings |
|----------|--------|-------------------|
| Reduce Steel waste to 3% benchmark | 102 projects | **$3,296,428** |
| Reduce Wood waste to 8% benchmark | 106 projects | **$455,473** |
| Reduce Concrete waste to 5% benchmark | 82 projects | **$436,373** |
| Reduce Asphalt waste to 4% benchmark | 82 projects | **$322,206** |

### Actionable Recommendations
1. **Steel is priority #1** — Low waste %, but each wasted unit costs $861. Even 1% reduction = massive savings
2. **Consolidate Wood suppliers** — Switch from TimberLine Co. to WoodWorks Supply (1.1% lower waste)
3. **Audit Residential projects** — Consistently higher waste across all materials; likely over-ordering
4. **Implement just-in-time ordering** — Correlation shows order size weakly tied to waste % (r=0.07), meaning bulk orders aren't inherently wasteful — the problem is forecasting accuracy
5. **Flag top 47 outlier projects** (>15% waste) — These alone cost $706K in waste

## 📁 Project Structure

```
construction_waste_analysis/
├── generate_data.py          # Dataset generation (500 realistic records)
├── analyze.py                # Full analysis + chart generation
├── construction_waste_data.csv   # Raw dataset
├── charts/
│   ├── 01_waste_distribution.html/png
│   ├── 02_waste_cost_by_material.html/png
│   ├── 03_supplier_performance.html/png
│   ├── 04_order_vs_waste_scatter.html/png
│   ├── 05_project_type_waste.html/png
│   ├── 06_waste_treemap.html/png
│   └── 07_pareto_waste.html/png
└── README.md
```

## 🛠️ Tech Stack
- Python, pandas, NumPy
- Plotly (interactive HTML charts + PNG exports)
- Matplotlib, Seaborn

## ▶️ Run It
```bash
pip install pandas numpy plotly matplotlib seaborn kaleido
python generate_data.py
python analyze.py
```

---
*Industry relevance: Construction material waste typically runs 5-15%, costing the US construction industry ~$160B annually. Data-driven waste reduction is one of the highest-ROI improvements a construction firm can make.*
