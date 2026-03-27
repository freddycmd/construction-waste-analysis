"""
Construction Material Usage & Waste Optimization Analysis
=========================================================
Dataset: 500 construction project records
Goal: Reduce material waste and cost through data-driven insights
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

os.makedirs('charts', exist_ok=True)

df = pd.read_csv('construction_waste_data.csv')

# ============================================================
# 1. EXECUTIVE SUMMARY METRICS
# ============================================================
total_ordered = df['Ordered_Qty'].sum()
total_used = df['Used_Qty'].sum()
total_waste = df['Waste_Qty'].sum()
total_waste_cost = df['Waste_Cost'].sum()
avg_waste_pct = df['Waste_%'].mean()

print("=" * 60)
print("EXECUTIVE SUMMARY")
print("=" * 60)
print(f"Total Records:           {len(df)}")
print(f"Total Ordered:           {total_ordered:,.1f} units")
print(f"Total Used:              {total_used:,.1f} units")
print(f"Total Wasted:            {total_waste:,.1f} units ({total_waste/total_ordered*100:.1f}%)")
print(f"Total Waste Cost:        ${total_waste_cost:,.2f}")
print(f"Avg Waste %:             {avg_waste_pct:.2f}%")
print()

# ============================================================
# 2. MATERIAL-LEVEL ANALYSIS
# ============================================================
mat_summary = df.groupby('Material').agg(
    Records=('Project_ID', 'count'),
    Avg_Waste_Pct=('Waste_%', 'mean'),
    Median_Waste_Pct=('Waste_%', 'median'),
    Total_Waste_Qty=('Waste_Qty', 'sum'),
    Total_Waste_Cost=('Waste_Cost', 'sum'),
    Avg_Unit_Cost=('Unit_Cost', 'mean'),
    Total_Ordered=('Ordered_Qty', 'sum')
).round(2)
mat_summary['Cost_per_Wasted_Unit'] = (mat_summary['Total_Waste_Cost'] / mat_summary['Total_Waste_Qty']).round(2)

print("MATERIAL BREAKDOWN")
print("-" * 60)
print(mat_summary.to_string())
print()

# ============================================================
# 3. SUPPLIER PERFORMANCE
# ============================================================
sup_summary = df.groupby(['Material', 'Supplier']).agg(
    Records=('Project_ID', 'count'),
    Avg_Waste_Pct=('Waste_%', 'mean'),
    Total_Waste_Cost=('Waste_Cost', 'sum'),
    Avg_Ordered=('Ordered_Qty', 'mean')
).round(2).sort_values(['Material', 'Avg_Waste_Pct'])

print("SUPPLIER PERFORMANCE (sorted by waste %)")
print("-" * 60)
print(sup_summary.to_string())
print()

# ============================================================
# 4. PROJECT TYPE ANALYSIS
# ============================================================
proj_summary = df.groupby('Project_Type').agg(
    Records=('Project_ID', 'count'),
    Avg_Waste_Pct=('Waste_%', 'mean'),
    Total_Waste_Cost=('Waste_Cost', 'sum'),
    Avg_Unit_Cost=('Unit_Cost', 'mean')
).round(2).sort_values('Avg_Waste_Pct', ascending=False)

print("PROJECT TYPE BREAKDOWN")
print("-" * 60)
print(proj_summary.to_string())
print()

# ============================================================
# 5. HIGH-WASTE OUTLIERS (Waste% > 15)
# ============================================================
outliers = df[df['Waste_%'] > 15].sort_values('Waste_Cost', ascending=False)
print(f"HIGH-WASTE OUTLIERS (Waste% > 15): {len(outliers)} records")
print(f"Combined waste cost of outliers: ${outliers['Waste_Cost'].sum():,.2f}")
print("-" * 60)
print(outliers[['Project_ID', 'Material', 'Waste_%', 'Waste_Cost', 'Supplier', 'Project_Type']].head(15).to_string(index=False))
print()

# ============================================================
# 6. CORRELATION: Order Size vs Waste%
# ============================================================
corr = df[['Ordered_Qty', 'Waste_%', 'Unit_Cost', 'Waste_Cost']].corr()
print("CORRELATION MATRIX")
print("-" * 60)
print(corr.round(3).to_string())
print()

# ============================================================
# CHARTS — Plotly (interactive HTML) + PNG exports
# ============================================================

# Chart 1: Waste % Distribution by Material (Box Plot)
fig1 = px.box(df, x='Material', y='Waste_%', color='Material',
              title='Material Waste % Distribution',
              labels={'Waste_%': 'Waste (%)', 'Material': ''},
              color_discrete_sequence=px.colors.qualitative.Set2)
fig1.update_layout(showlegend=False, template='plotly_white',
                   font=dict(size=14), title_font_size=20)
fig1.write_html('charts/01_waste_distribution.html')
fig1.write_image('charts/01_waste_distribution.png', width=1000, height=600, scale=2)

# Chart 2: Total Waste Cost by Material (Bar)
mat_cost = df.groupby('Material')['Waste_Cost'].sum().reset_index().sort_values('Waste_Cost', ascending=True)
fig2 = px.bar(mat_cost, y='Material', x='Waste_Cost', orientation='h',
              title='Total Waste Cost by Material',
              labels={'Waste_Cost': 'Total Waste Cost ($)', 'Material': ''},
              color='Material', color_discrete_sequence=px.colors.qualitative.Set2,
              text=mat_cost['Waste_Cost'].apply(lambda x: f'${x:,.0f}'))
fig2.update_traces(textposition='outside')
fig2.update_layout(showlegend=False, template='plotly_white',
                   font=dict(size=14), title_font_size=20)
fig2.write_html('charts/02_waste_cost_by_material.html')
fig2.write_image('charts/02_waste_cost_by_material.png', width=1000, height=500, scale=2)

# Chart 3: Supplier Performance Heatmap
sup_pivot = df.groupby(['Material', 'Supplier'])['Waste_%'].mean().reset_index()
fig3 = px.bar(sup_pivot.sort_values(['Material', 'Waste_%']),
              x='Supplier', y='Waste_%', color='Material', barmode='group',
              title='Average Waste % by Supplier & Material',
              labels={'Waste_%': 'Avg Waste (%)', 'Supplier': ''},
              color_discrete_sequence=px.colors.qualitative.Set2)
fig3.update_layout(template='plotly_white', font=dict(size=12),
                   title_font_size=20, xaxis_tickangle=-30)
fig3.write_html('charts/03_supplier_performance.html')
fig3.write_image('charts/03_supplier_performance.png', width=1200, height=600, scale=2)

# Chart 4: Order Qty vs Waste % Scatter
fig4 = px.scatter(df, x='Ordered_Qty', y='Waste_%', color='Material',
                  size='Waste_Cost', hover_data=['Project_ID', 'Supplier'],
                  title='Order Size vs Waste % (bubble = waste cost)',
                  labels={'Ordered_Qty': 'Ordered Quantity', 'Waste_%': 'Waste (%)'},
                  color_discrete_sequence=px.colors.qualitative.Set2)
fig4.update_layout(template='plotly_white', font=dict(size=14), title_font_size=20)
fig4.write_html('charts/04_order_vs_waste_scatter.html')
fig4.write_image('charts/04_order_vs_waste_scatter.png', width=1100, height=600, scale=2)

# Chart 5: Project Type Waste Comparison
proj_mat = df.groupby(['Project_Type', 'Material'])['Waste_%'].mean().reset_index()
fig5 = px.bar(proj_mat, x='Project_Type', y='Waste_%', color='Material', barmode='group',
              title='Avg Waste % by Project Type & Material',
              labels={'Waste_%': 'Avg Waste (%)', 'Project_Type': ''},
              color_discrete_sequence=px.colors.qualitative.Set2)
fig5.update_layout(template='plotly_white', font=dict(size=14), title_font_size=20)
fig5.write_html('charts/05_project_type_waste.html')
fig5.write_image('charts/05_project_type_waste.png', width=1100, height=600, scale=2)

# Chart 6: Waste Cost Treemap
tree_data = df.groupby(['Material', 'Supplier']).agg(
    Total_Waste_Cost=('Waste_Cost', 'sum'),
    Avg_Waste_Pct=('Waste_%', 'mean')
).reset_index()
fig6 = px.treemap(tree_data, path=['Material', 'Supplier'], values='Total_Waste_Cost',
                  color='Avg_Waste_Pct', color_continuous_scale='RdYlGn_r',
                  title='Waste Cost Treemap (color = avg waste %)',
                  labels={'Total_Waste_Cost': 'Waste Cost ($)', 'Avg_Waste_Pct': 'Waste %'})
fig6.update_layout(font=dict(size=14), title_font_size=20)
fig6.write_html('charts/06_waste_treemap.html')
fig6.write_image('charts/06_waste_treemap.png', width=1100, height=700, scale=2)

# Chart 7: Cumulative Waste Cost (Pareto-style)
df_sorted = df.sort_values('Waste_Cost', ascending=False).reset_index(drop=True)
df_sorted['Cumulative_Waste_Cost'] = df_sorted['Waste_Cost'].cumsum()
df_sorted['Cumulative_Pct'] = df_sorted['Cumulative_Waste_Cost'] / total_waste_cost * 100
df_sorted['Record_Rank'] = range(1, len(df_sorted) + 1)

fig7 = make_subplots(specs=[[{"secondary_y": True}]])
fig7.add_trace(go.Bar(x=df_sorted['Record_Rank'], y=df_sorted['Waste_Cost'],
                       name='Individual Waste Cost', marker_color='#66c2a5', opacity=0.7),
               secondary_y=False)
fig7.add_trace(go.Scatter(x=df_sorted['Record_Rank'], y=df_sorted['Cumulative_Pct'],
                           name='Cumulative %', line=dict(color='#e41a1c', width=2.5)),
               secondary_y=True)
fig7.add_hline(y=80, line_dash="dash", line_color="gray", secondary_y=True,
               annotation_text="80% threshold")
fig7.update_layout(title='Pareto: Waste Cost Concentration',
                   template='plotly_white', font=dict(size=14), title_font_size=20)
fig7.update_xaxes(title_text="Projects (ranked by waste cost)")
fig7.update_yaxes(title_text="Waste Cost ($)", secondary_y=False)
fig7.update_yaxes(title_text="Cumulative %", secondary_y=True)
fig7.write_html('charts/07_pareto_waste.html')
fig7.write_image('charts/07_pareto_waste.png', width=1200, height=600, scale=2)

print("✅ All 7 charts exported to charts/")

# ============================================================
# 7. SAVINGS POTENTIAL
# ============================================================
# If we reduce waste to industry benchmarks
benchmarks = {'Concrete': 5, 'Steel': 3, 'Asphalt': 4, 'Wood': 8}

print("\n" + "=" * 60)
print("OPTIMIZATION SAVINGS POTENTIAL")
print("=" * 60)

total_savings = 0
for material, target in benchmarks.items():
    mat_df = df[df['Material'] == material]
    above_target = mat_df[mat_df['Waste_%'] > target]
    if len(above_target) == 0:
        continue
    current_waste_cost = above_target['Waste_Cost'].sum()
    # Recalculate at target waste%
    target_waste_qty = above_target['Ordered_Qty'] * target / 100
    target_waste_cost = (target_waste_qty * above_target['Unit_Cost']).sum()
    savings = current_waste_cost - target_waste_cost
    total_savings += savings
    pct_projects = len(above_target) / len(mat_df) * 100
    print(f"\n{material} (target: {target}%):")
    print(f"  Projects above target: {len(above_target)} ({pct_projects:.0f}%)")
    print(f"  Current waste cost:    ${current_waste_cost:,.2f}")
    print(f"  Optimized waste cost:  ${target_waste_cost:,.2f}")
    print(f"  Potential savings:     ${savings:,.2f}")

print(f"\n{'=' * 60}")
print(f"TOTAL POTENTIAL SAVINGS:  ${total_savings:,.2f}")
print(f"That's {total_savings/total_waste_cost*100:.1f}% of current waste spend")
print(f"{'=' * 60}")

# ============================================================
# 8. WORST SUPPLIERS (to flag for review)
# ============================================================
print("\n\nSUPPLIER RED FLAGS (avg waste > material average + 1σ)")
print("-" * 60)
for material in df['Material'].unique():
    mat_df = df[df['Material'] == material]
    mat_mean = mat_df['Waste_%'].mean()
    mat_std = mat_df['Waste_%'].std()
    threshold = mat_mean + mat_std
    for supplier in mat_df['Supplier'].unique():
        sup_df = mat_df[mat_df['Supplier'] == supplier]
        sup_avg = sup_df['Waste_%'].mean()
        if sup_avg > threshold:
            print(f"  ⚠️  {supplier} ({material}): {sup_avg:.1f}% avg waste "
                  f"(threshold: {threshold:.1f}%)")

print("\n✅ Analysis complete. Files in construction_waste_analysis/")
