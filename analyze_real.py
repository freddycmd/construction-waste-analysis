"""
Construction Material Usage & Waste Optimization Analysis
=========================================================
Dataset: 500 real construction project records
Goal: Reduce material waste and cost through data-driven insights
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, json

os.makedirs('charts', exist_ok=True)

df = pd.read_csv('material_waste_dataset.csv')

# ============================================================
# 1. EXECUTIVE SUMMARY
# ============================================================
total_ordered = df['Ordered_Qty'].sum()
total_used = df['Used_Qty'].sum()
total_waste = df['Waste_Qty'].sum()
total_waste_cost = df['Waste_Cost'].sum()
avg_waste_pct = df['Waste_%'].mean()
median_waste_pct = df['Waste_%'].median()

print("=" * 65)
print("EXECUTIVE SUMMARY")
print("=" * 65)
print(f"Total Records:             {len(df)}")
print(f"Unique Projects:           {df['Project_ID'].nunique()}")
print(f"Materials:                 {', '.join(df['Material'].unique())}")
print(f"Suppliers:                 {', '.join(df['Supplier'].unique())}")
print(f"Project Types:             {', '.join(df['Project_Type'].unique())}")
print(f"Total Ordered:             {total_ordered:,.1f} units")
print(f"Total Used:                {total_used:,.0f} units")
print(f"Total Wasted:              {total_waste:,.1f} units")
print(f"Overall Waste Rate:        {total_waste/total_ordered*100:.2f}%")
print(f"Mean Waste %:              {avg_waste_pct:.2f}%")
print(f"Median Waste %:            {median_waste_pct:.2f}%")
print(f"Total Waste Cost:          ${total_waste_cost:,.2f}")
print(f"Avg Waste Cost/Record:     ${total_waste_cost/len(df):,.2f}")
print()

# ============================================================
# 2. MATERIAL-LEVEL ANALYSIS
# ============================================================
mat = df.groupby('Material').agg(
    Records=('Project_ID', 'count'),
    Avg_Waste_Pct=('Waste_%', 'mean'),
    Median_Waste_Pct=('Waste_%', 'median'),
    Std_Waste_Pct=('Waste_%', 'std'),
    Total_Waste_Qty=('Waste_Qty', 'sum'),
    Total_Waste_Cost=('Waste_Cost', 'sum'),
    Avg_Unit_Cost=('Unit_Cost', 'mean'),
    Total_Ordered=('Ordered_Qty', 'sum')
).round(2)
mat['Waste_Cost_Share_%'] = (mat['Total_Waste_Cost'] / total_waste_cost * 100).round(1)

print("MATERIAL BREAKDOWN")
print("-" * 65)
for m in mat.index:
    r = mat.loc[m]
    print(f"\n  {m}:")
    print(f"    Records: {int(r.Records)} | Avg Waste: {r.Avg_Waste_Pct}% | Median: {r.Median_Waste_Pct}%")
    print(f"    Total Waste Cost: ${r.Total_Waste_Cost:,.0f} ({r['Waste_Cost_Share_%']}% of total)")
    print(f"    Avg Unit Cost: ${r.Avg_Unit_Cost:.2f}")
print()

# ============================================================
# 3. SUPPLIER PERFORMANCE
# ============================================================
sup = df.groupby(['Supplier']).agg(
    Records=('Project_ID', 'count'),
    Avg_Waste_Pct=('Waste_%', 'mean'),
    Median_Waste_Pct=('Waste_%', 'median'),
    Total_Waste_Cost=('Waste_Cost', 'sum'),
    Avg_Unit_Cost=('Unit_Cost', 'mean')
).round(2).sort_values('Avg_Waste_Pct')

print("SUPPLIER PERFORMANCE (overall)")
print("-" * 65)
print(sup.to_string())
print()

sup_mat = df.groupby(['Material', 'Supplier']).agg(
    Records=('Project_ID', 'count'),
    Avg_Waste_Pct=('Waste_%', 'mean'),
    Total_Waste_Cost=('Waste_Cost', 'sum')
).round(2).sort_values(['Material', 'Avg_Waste_Pct'])

print("SUPPLIER × MATERIAL BREAKDOWN")
print("-" * 65)
print(sup_mat.to_string())
print()

# ============================================================
# 4. PROJECT TYPE ANALYSIS
# ============================================================
proj = df.groupby('Project_Type').agg(
    Records=('Project_ID', 'count'),
    Avg_Waste_Pct=('Waste_%', 'mean'),
    Median_Waste_Pct=('Waste_%', 'median'),
    Total_Waste_Cost=('Waste_Cost', 'sum'),
    Avg_Unit_Cost=('Unit_Cost', 'mean')
).round(2).sort_values('Avg_Waste_Pct', ascending=False)

print("PROJECT TYPE BREAKDOWN")
print("-" * 65)
print(proj.to_string())
print()

# ============================================================
# 5. HIGH-WASTE OUTLIERS
# ============================================================
q75 = df['Waste_%'].quantile(0.75)
q25 = df['Waste_%'].quantile(0.25)
iqr = q75 - q25
upper_fence = q75 + 1.5 * iqr
outlier_threshold = 18  # using a practical threshold

high_waste = df[df['Waste_%'] >= outlier_threshold].sort_values('Waste_Cost', ascending=False)
print(f"HIGH-WASTE RECORDS (Waste% >= {outlier_threshold}%): {len(high_waste)} records")
print(f"Combined waste cost: ${high_waste['Waste_Cost'].sum():,.2f}")
print("-" * 65)
print(high_waste[['Project_ID','Material','Waste_%','Waste_Cost','Supplier','Project_Type']].head(20).to_string(index=False))
print()

# ============================================================
# 6. CORRELATION
# ============================================================
corr_cols = ['Used_Qty', 'Ordered_Qty', 'Unit_Cost', 'Waste_Qty', 'Waste_%', 'Waste_Cost']
print("CORRELATION MATRIX")
print("-" * 65)
print(df[corr_cols].corr().round(3).to_string())
print()

# ============================================================
# CHARTS
# ============================================================
COLORS = {'Concrete': '#636EFA', 'Steel': '#EF553B', 'Asphalt': '#00CC96', 'Wood': '#AB63FA'}
SUP_COLORS = {'Supplier A': '#636EFA', 'Supplier B': '#EF553B', 'Supplier C': '#00CC96', 'Supplier D': '#AB63FA'}

# 1 — Waste % Distribution by Material
fig1 = px.box(df, x='Material', y='Waste_%', color='Material',
              title='Waste % Distribution by Material',
              labels={'Waste_%': 'Waste (%)', 'Material': ''},
              color_discrete_map=COLORS, points='outliers')
fig1.update_layout(showlegend=False, template='plotly_white',
                   font=dict(size=14), title_font_size=20)
fig1.write_html('charts/01_waste_distribution.html')
fig1.write_image('charts/01_waste_distribution.png', width=1000, height=600, scale=2)

# 2 — Total Waste Cost by Material
mc = df.groupby('Material')['Waste_Cost'].sum().reset_index().sort_values('Waste_Cost', ascending=True)
fig2 = px.bar(mc, y='Material', x='Waste_Cost', orientation='h',
              title='Total Waste Cost by Material',
              labels={'Waste_Cost': 'Total Waste Cost ($)', 'Material': ''},
              color='Material', color_discrete_map=COLORS,
              text=mc['Waste_Cost'].apply(lambda x: f'${x:,.0f}'))
fig2.update_traces(textposition='outside')
fig2.update_layout(showlegend=False, template='plotly_white',
                   font=dict(size=14), title_font_size=20)
fig2.write_html('charts/02_waste_cost_by_material.html')
fig2.write_image('charts/02_waste_cost_by_material.png', width=1000, height=500, scale=2)

# 3 — Supplier Avg Waste % by Material
sp = df.groupby(['Material','Supplier'])['Waste_%'].mean().reset_index()
fig3 = px.bar(sp.sort_values(['Material','Waste_%']),
              x='Material', y='Waste_%', color='Supplier', barmode='group',
              title='Avg Waste % by Supplier & Material',
              labels={'Waste_%': 'Avg Waste (%)', 'Material': ''},
              color_discrete_map=SUP_COLORS)
fig3.update_layout(template='plotly_white', font=dict(size=13), title_font_size=20)
fig3.write_html('charts/03_supplier_performance.html')
fig3.write_image('charts/03_supplier_performance.png', width=1100, height=600, scale=2)

# 4 — Order Size vs Waste % (Scatter)
fig4 = px.scatter(df, x='Ordered_Qty', y='Waste_%', color='Material',
                  size='Waste_Cost', size_max=25,
                  hover_data=['Project_ID','Supplier','Project_Type'],
                  title='Order Size vs Waste % (bubble = waste cost)',
                  labels={'Ordered_Qty': 'Ordered Quantity', 'Waste_%': 'Waste (%)'},
                  color_discrete_map=COLORS)
fig4.update_layout(template='plotly_white', font=dict(size=14), title_font_size=20)
fig4.write_html('charts/04_order_vs_waste_scatter.html')
fig4.write_image('charts/04_order_vs_waste_scatter.png', width=1100, height=600, scale=2)

# 5 — Project Type × Material Waste %
pm = df.groupby(['Project_Type','Material'])['Waste_%'].mean().reset_index()
fig5 = px.bar(pm, x='Project_Type', y='Waste_%', color='Material', barmode='group',
              title='Avg Waste % by Project Type & Material',
              labels={'Waste_%': 'Avg Waste (%)', 'Project_Type': ''},
              color_discrete_map=COLORS)
fig5.update_layout(template='plotly_white', font=dict(size=14), title_font_size=20)
fig5.write_html('charts/05_project_type_waste.html')
fig5.write_image('charts/05_project_type_waste.png', width=1100, height=600, scale=2)

# 6 — Waste Cost Treemap
tree = df.groupby(['Material','Supplier']).agg(
    Total_Waste_Cost=('Waste_Cost','sum'),
    Avg_Waste_Pct=('Waste_%','mean')
).reset_index()
fig6 = px.treemap(tree, path=['Material','Supplier'], values='Total_Waste_Cost',
                  color='Avg_Waste_Pct', color_continuous_scale='RdYlGn_r',
                  title='Waste Cost Treemap (color = avg waste %)',
                  labels={'Total_Waste_Cost': 'Waste Cost ($)', 'Avg_Waste_Pct': 'Waste %'})
fig6.update_layout(font=dict(size=14), title_font_size=20)
fig6.write_html('charts/06_waste_treemap.html')
fig6.write_image('charts/06_waste_treemap.png', width=1100, height=700, scale=2)

# 7 — Pareto (Cumulative Waste Cost)
dfs = df.sort_values('Waste_Cost', ascending=False).reset_index(drop=True)
dfs['Cum_Cost'] = dfs['Waste_Cost'].cumsum()
dfs['Cum_Pct'] = dfs['Cum_Cost'] / total_waste_cost * 100
dfs['Rank'] = range(1, len(dfs)+1)

fig7 = make_subplots(specs=[[{"secondary_y": True}]])
fig7.add_trace(go.Bar(x=dfs['Rank'], y=dfs['Waste_Cost'],
                       name='Waste Cost', marker_color='#636EFA', opacity=0.7),
               secondary_y=False)
fig7.add_trace(go.Scatter(x=dfs['Rank'], y=dfs['Cum_Pct'],
                           name='Cumulative %', line=dict(color='#EF553B', width=2.5)),
               secondary_y=True)
fig7.add_hline(y=80, line_dash="dash", line_color="gray", secondary_y=True,
               annotation_text="80% threshold")
n_80 = dfs[dfs['Cum_Pct'] <= 80].shape[0]
fig7.update_layout(title=f'Pareto: Top {n_80} records ({n_80/len(df)*100:.0f}%) = 80% of waste cost',
                   template='plotly_white', font=dict(size=14), title_font_size=18)
fig7.update_xaxes(title_text="Projects (ranked by waste cost)")
fig7.update_yaxes(title_text="Waste Cost ($)", secondary_y=False)
fig7.update_yaxes(title_text="Cumulative %", secondary_y=True)
fig7.write_html('charts/07_pareto_waste.html')
fig7.write_image('charts/07_pareto_waste.png', width=1200, height=600, scale=2)

# 8 — Waste % Histogram with KDE-style overlay
fig8 = px.histogram(df, x='Waste_%', color='Material', nbins=30, barmode='overlay',
                    opacity=0.6, title='Waste % Frequency Distribution',
                    labels={'Waste_%': 'Waste (%)', 'count': 'Records'},
                    color_discrete_map=COLORS)
fig8.update_layout(template='plotly_white', font=dict(size=14), title_font_size=20)
fig8.write_html('charts/08_waste_histogram.html')
fig8.write_image('charts/08_waste_histogram.png', width=1100, height=550, scale=2)

# 9 — Supplier Total Waste Cost (stacked by material)
sup_cost = df.groupby(['Supplier','Material'])['Waste_Cost'].sum().reset_index()
fig9 = px.bar(sup_cost, x='Supplier', y='Waste_Cost', color='Material',
              title='Total Waste Cost by Supplier (stacked by material)',
              labels={'Waste_Cost': 'Waste Cost ($)', 'Supplier': ''},
              color_discrete_map=COLORS)
fig9.update_layout(template='plotly_white', font=dict(size=14), title_font_size=20)
fig9.write_html('charts/09_supplier_cost_stacked.html')
fig9.write_image('charts/09_supplier_cost_stacked.png', width=1100, height=600, scale=2)

# 10 — Unit Cost vs Waste % colored by material
fig10 = px.scatter(df, x='Unit_Cost', y='Waste_%', color='Material',
                   trendline='ols', title='Unit Cost vs Waste % (with trendlines)',
                   labels={'Unit_Cost': 'Unit Cost ($)', 'Waste_%': 'Waste (%)'},
                   color_discrete_map=COLORS)
fig10.update_layout(template='plotly_white', font=dict(size=14), title_font_size=20)
fig10.write_html('charts/10_unitcost_vs_waste.html')
fig10.write_image('charts/10_unitcost_vs_waste.png', width=1100, height=600, scale=2)

print("✅ All 10 charts exported to charts/")

# ============================================================
# 7. OPTIMIZATION SAVINGS
# ============================================================
# Industry benchmarks for waste %
benchmarks = {'Concrete': 8, 'Steel': 8, 'Asphalt': 8, 'Wood': 10}

print("\n" + "=" * 65)
print("OPTIMIZATION SAVINGS POTENTIAL")
print("(Targets: Concrete 8%, Steel 8%, Asphalt 8%, Wood 10%)")
print("=" * 65)

savings_data = []
for material, target in benchmarks.items():
    mdf = df[df['Material'] == material]
    above = mdf[mdf['Waste_%'] > target]
    if len(above) == 0:
        continue
    current = above['Waste_Cost'].sum()
    optimized = (above['Ordered_Qty'] * target / 100 * above['Unit_Cost']).sum()
    saved = current - optimized
    savings_data.append({
        'Material': material,
        'Target_%': target,
        'Projects_Above': len(above),
        'Pct_Above': f"{len(above)/len(mdf)*100:.0f}%",
        'Current_Cost': current,
        'Optimized_Cost': optimized,
        'Savings': saved
    })
    print(f"\n  {material} (target: {target}%):")
    print(f"    Projects above target: {len(above)} of {len(mdf)} ({len(above)/len(mdf)*100:.0f}%)")
    print(f"    Current waste cost:    ${current:,.2f}")
    print(f"    At target waste cost:  ${optimized:,.2f}")
    print(f"    ➜ Potential savings:   ${saved:,.2f}")

total_savings = sum(s['Savings'] for s in savings_data)
print(f"\n{'=' * 65}")
print(f"  TOTAL POTENTIAL SAVINGS:  ${total_savings:,.2f}")
print(f"  That's {total_savings/total_waste_cost*100:.1f}% of current waste spend (${total_waste_cost:,.0f})")
print(f"{'=' * 65}")

# ============================================================
# 8. BEST/WORST SUPPLIER PER MATERIAL
# ============================================================
print("\n\nSUPPLIER RECOMMENDATIONS")
print("-" * 65)
for material in df['Material'].unique():
    mdf = df[df['Material'] == material]
    sg = mdf.groupby('Supplier')['Waste_%'].agg(['mean','count']).sort_values('mean')
    best = sg.index[0]
    worst = sg.index[-1]
    gap = sg.loc[worst,'mean'] - sg.loc[best,'mean']
    print(f"\n  {material}:")
    print(f"    Best:  {best} ({sg.loc[best,'mean']:.1f}% avg, n={int(sg.loc[best,'count'])})")
    print(f"    Worst: {worst} ({sg.loc[worst,'mean']:.1f}% avg, n={int(sg.loc[worst,'count'])})")
    print(f"    Gap:   {gap:.1f} pp — switching to {best} could cut waste significantly")

# Save summary JSON for downstream use
summary = {
    'total_records': len(df),
    'total_waste_cost': round(total_waste_cost, 2),
    'avg_waste_pct': round(avg_waste_pct, 2),
    'median_waste_pct': round(median_waste_pct, 2),
    'total_potential_savings': round(total_savings, 2),
    'savings_pct': round(total_savings/total_waste_cost*100, 1),
    'pareto_80_records': n_80,
    'pareto_80_pct': round(n_80/len(df)*100, 1)
}
with open('summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print("\n\n✅ Analysis complete. summary.json written.")
