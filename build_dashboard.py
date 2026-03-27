"""
Construction Waste Optimization — Interactive Dashboard
=======================================================
Self-contained HTML dashboard with all charts and KPIs.
No server needed — just open dashboard.html in any browser.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

df = pd.read_csv('material_waste_dataset.csv')

COLORS = {'Concrete': '#636EFA', 'Steel': '#EF553B', 'Asphalt': '#00CC96', 'Wood': '#AB63FA'}
SUP_COLORS = {'Supplier A': '#636EFA', 'Supplier B': '#EF553B', 'Supplier C': '#00CC96', 'Supplier D': '#AB63FA'}

# ============================================================
# KPI CALCULATIONS
# ============================================================
total_waste_cost = df['Waste_Cost'].sum()
avg_waste_pct = df['Waste_%'].mean()
total_records = len(df)
total_ordered = df['Ordered_Qty'].sum()
total_wasted = df['Waste_Qty'].sum()
high_waste_count = len(df[df['Waste_%'] >= 18])
high_waste_cost = df[df['Waste_%'] >= 18]['Waste_Cost'].sum()

benchmarks = {'Concrete': 8, 'Steel': 8, 'Asphalt': 8, 'Wood': 10}
total_savings = 0
for mat, target in benchmarks.items():
    mdf = df[(df['Material'] == mat) & (df['Waste_%'] > target)]
    current = mdf['Waste_Cost'].sum()
    optimized = (mdf['Ordered_Qty'] * target / 100 * mdf['Unit_Cost']).sum()
    total_savings += current - optimized

# ============================================================
# CHART 1: Material Waste % Box Plot
# ============================================================
fig1 = px.box(df, x='Material', y='Waste_%', color='Material',
              color_discrete_map=COLORS, points='outliers')
fig1.update_layout(showlegend=False, template='plotly_white', margin=dict(t=30, b=40),
                   yaxis_title='Waste %', xaxis_title='', height=350)

# ============================================================
# CHART 2: Waste Cost by Material (Donut)
# ============================================================
mc = df.groupby('Material')['Waste_Cost'].sum().reset_index()
fig2 = go.Figure(go.Pie(labels=mc['Material'], values=mc['Waste_Cost'],
                        hole=0.5, marker_colors=[COLORS[m] for m in mc['Material']],
                        textinfo='label+percent', textposition='outside',
                        hovertemplate='%{label}<br>$%{value:,.0f}<extra></extra>'))
fig2.update_layout(showlegend=False, margin=dict(t=30, b=30, l=20, r=20), height=350)

# ============================================================
# CHART 3: Supplier × Material Heatmap
# ============================================================
heat = df.groupby(['Supplier', 'Material'])['Waste_%'].mean().reset_index()
heat_pivot = heat.pivot(index='Supplier', columns='Material', values='Waste_%')
fig3 = go.Figure(go.Heatmap(
    z=heat_pivot.values,
    x=heat_pivot.columns.tolist(),
    y=heat_pivot.index.tolist(),
    colorscale='RdYlGn_r',
    text=np.round(heat_pivot.values, 1),
    texttemplate='%{text}%',
    textfont=dict(size=14),
    hovertemplate='%{y} × %{x}<br>Waste: %{z:.1f}%<extra></extra>',
    colorbar=dict(title='Waste %')
))
fig3.update_layout(template='plotly_white', margin=dict(t=30, b=40), height=350,
                   xaxis_title='', yaxis_title='')

# ============================================================
# CHART 4: Supplier Avg Waste % Grouped Bar
# ============================================================
sp = df.groupby(['Material', 'Supplier'])['Waste_%'].mean().reset_index()
fig4 = px.bar(sp.sort_values(['Material', 'Waste_%']),
              x='Material', y='Waste_%', color='Supplier', barmode='group',
              color_discrete_map=SUP_COLORS)
fig4.update_layout(template='plotly_white', margin=dict(t=30, b=40), height=350,
                   yaxis_title='Avg Waste %', xaxis_title='', legend=dict(orientation='h', y=-0.15))

# ============================================================
# CHART 5: Order Qty vs Waste % Scatter
# ============================================================
fig5 = px.scatter(df, x='Ordered_Qty', y='Waste_%', color='Material',
                  size='Waste_Cost', size_max=20,
                  hover_data=['Project_ID', 'Supplier'],
                  color_discrete_map=COLORS)
fig5.update_layout(template='plotly_white', margin=dict(t=30, b=40), height=370,
                   xaxis_title='Ordered Quantity', yaxis_title='Waste %',
                   legend=dict(orientation='h', y=-0.15))

# ============================================================
# CHART 6: Project Type Comparison
# ============================================================
proj = df.groupby('Project_Type').agg(
    Avg_Waste=('Waste_%', 'mean'),
    Total_Cost=('Waste_Cost', 'sum'),
    Records=('Project_ID', 'count')
).reset_index().sort_values('Avg_Waste', ascending=True)

fig6 = make_subplots(specs=[[{"secondary_y": True}]])
fig6.add_trace(go.Bar(x=proj['Project_Type'], y=proj['Total_Cost'],
                       name='Total Waste Cost', marker_color='#636EFA', opacity=0.7),
               secondary_y=False)
fig6.add_trace(go.Scatter(x=proj['Project_Type'], y=proj['Avg_Waste'],
                           name='Avg Waste %', mode='lines+markers',
                           line=dict(color='#EF553B', width=3), marker=dict(size=10)),
               secondary_y=True)
fig6.update_layout(template='plotly_white', margin=dict(t=30, b=40), height=350,
                   legend=dict(orientation='h', y=-0.15))
fig6.update_yaxes(title_text="Waste Cost ($)", secondary_y=False)
fig6.update_yaxes(title_text="Avg Waste %", secondary_y=True)

# ============================================================
# CHART 7: Pareto
# ============================================================
dfs = df.sort_values('Waste_Cost', ascending=False).reset_index(drop=True)
dfs['Cum_Cost'] = dfs['Waste_Cost'].cumsum()
dfs['Cum_Pct'] = dfs['Cum_Cost'] / total_waste_cost * 100
dfs['Rank'] = range(1, len(dfs) + 1)
n_80 = dfs[dfs['Cum_Pct'] <= 80].shape[0]

fig7 = make_subplots(specs=[[{"secondary_y": True}]])
fig7.add_trace(go.Bar(x=dfs['Rank'], y=dfs['Waste_Cost'],
                       name='Waste Cost', marker_color='#636EFA', opacity=0.6),
               secondary_y=False)
fig7.add_trace(go.Scatter(x=dfs['Rank'], y=dfs['Cum_Pct'],
                           name='Cumulative %', line=dict(color='#EF553B', width=2.5)),
               secondary_y=True)
fig7.add_hline(y=80, line_dash="dash", line_color="gray", secondary_y=True)
fig7.update_layout(template='plotly_white', margin=dict(t=30, b=40), height=370,
                   legend=dict(orientation='h', y=-0.15))
fig7.update_xaxes(title_text="Projects (ranked)")
fig7.update_yaxes(title_text="Cost ($)", secondary_y=False)
fig7.update_yaxes(title_text="Cumulative %", secondary_y=True)

# ============================================================
# CHART 8: Treemap
# ============================================================
tree = df.groupby(['Material', 'Supplier']).agg(
    Total_Waste_Cost=('Waste_Cost', 'sum'),
    Avg_Waste_Pct=('Waste_%', 'mean')
).reset_index()
fig8 = px.treemap(tree, path=['Material', 'Supplier'], values='Total_Waste_Cost',
                  color='Avg_Waste_Pct', color_continuous_scale='RdYlGn_r')
fig8.update_layout(margin=dict(t=30, b=10), height=400)

# ============================================================
# CHART 9: Waste % Distribution Histogram
# ============================================================
fig9 = px.histogram(df, x='Waste_%', color='Material', nbins=25, barmode='overlay',
                    opacity=0.6, color_discrete_map=COLORS)
fig9.update_layout(template='plotly_white', margin=dict(t=30, b=40), height=350,
                   xaxis_title='Waste %', yaxis_title='Count',
                   legend=dict(orientation='h', y=-0.15))

# ============================================================
# CHART 10: Top 15 Worst Records Table
# ============================================================
worst = df.nlargest(15, 'Waste_Cost')[['Project_ID','Material','Supplier','Project_Type',
                                        'Ordered_Qty','Waste_%','Waste_Cost']]
fig10 = go.Figure(go.Table(
    header=dict(values=['Project','Material','Supplier','Type','Ordered','Waste %','Waste $'],
                fill_color='#636EFA', font=dict(color='white', size=13),
                align='left', height=32),
    cells=dict(values=[worst[c] for c in worst.columns],
               fill_color=[['#f8f9fa','white']*8],
               font=dict(size=12), align='left', height=28,
               format=[None, None, None, None, ',.0f', '.1f', '$,.0f'])
))
fig10.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=470)

# ============================================================
# SAVINGS CHART
# ============================================================
savings_data = []
for mat, target in benchmarks.items():
    mdf = df[(df['Material'] == mat) & (df['Waste_%'] > target)]
    current = mdf['Waste_Cost'].sum()
    optimized = (mdf['Ordered_Qty'] * target / 100 * mdf['Unit_Cost']).sum()
    savings_data.append({'Material': mat, 'Current': current, 'Optimized': optimized,
                         'Savings': current - optimized, 'Target': f'{target}%'})

sdf = pd.DataFrame(savings_data)
fig11 = go.Figure()
fig11.add_trace(go.Bar(x=sdf['Material'], y=sdf['Optimized'], name='At Target',
                        marker_color='#00CC96'))
fig11.add_trace(go.Bar(x=sdf['Material'], y=sdf['Savings'], name='Savings',
                        marker_color='#EF553B'))
fig11.update_layout(barmode='stack', template='plotly_white',
                    margin=dict(t=30, b=40), height=350,
                    yaxis_title='Waste Cost ($)',
                    legend=dict(orientation='h', y=-0.15))

# ============================================================
# BUILD HTML DASHBOARD
# ============================================================

def fig_to_div(fig, div_id):
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=div_id)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Construction Waste Optimization Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #0f1117; color: #e0e0e0; }}
  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
             padding: 28px 40px; border-bottom: 2px solid #636EFA; }}
  .header h1 {{ font-size: 26px; font-weight: 700; color: #fff; }}
  .header p {{ color: #8892b0; margin-top: 6px; font-size: 14px; }}
  .kpi-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
              gap: 16px; padding: 24px 40px; }}
  .kpi {{ background: #1a1a2e; border-radius: 12px; padding: 20px 24px;
          border-left: 4px solid #636EFA; }}
  .kpi.red {{ border-left-color: #EF553B; }}
  .kpi.green {{ border-left-color: #00CC96; }}
  .kpi.purple {{ border-left-color: #AB63FA; }}
  .kpi-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1px;
                color: #8892b0; margin-bottom: 6px; }}
  .kpi-value {{ font-size: 28px; font-weight: 700; color: #fff; }}
  .kpi-sub {{ font-size: 12px; color: #636EFA; margin-top: 4px; }}
  .kpi.red .kpi-sub {{ color: #EF553B; }}
  .kpi.green .kpi-sub {{ color: #00CC96; }}
  .kpi.purple .kpi-sub {{ color: #AB63FA; }}
  .dashboard {{ padding: 0 40px 40px; }}
  .section {{ margin-top: 32px; }}
  .section-title {{ font-size: 18px; font-weight: 600; color: #fff;
                    margin-bottom: 16px; padding-bottom: 8px;
                    border-bottom: 1px solid #2a2a3e; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }}
  .card {{ background: #1a1a2e; border-radius: 12px; padding: 16px; overflow: hidden; }}
  .card-title {{ font-size: 13px; font-weight: 600; color: #8892b0;
                 text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
  .card-full {{ grid-column: 1 / -1; }}
  .recommendations {{ background: #1a1a2e; border-radius: 12px; padding: 24px;
                       margin-top: 20px; }}
  .rec-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }}
  .rec {{ background: #0f1117; border-radius: 8px; padding: 16px;
          border-left: 3px solid #00CC96; }}
  .rec h4 {{ color: #00CC96; font-size: 14px; margin-bottom: 6px; }}
  .rec p {{ color: #b0b0c0; font-size: 13px; line-height: 1.5; }}
  .footer {{ text-align: center; padding: 30px; color: #555; font-size: 12px; }}
  @media (max-width: 900px) {{
    .grid-2, .grid-3, .rec-grid {{ grid-template-columns: 1fr; }}
    .kpi-row {{ padding: 16px 20px; }}
    .dashboard {{ padding: 0 20px 20px; }}
    .header {{ padding: 20px; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>🏗️ Construction Material Waste Optimization</h1>
  <p>500 records · 4 materials · 4 suppliers · 3 project types — Interactive analysis dashboard</p>
</div>

<div class="kpi-row">
  <div class="kpi">
    <div class="kpi-label">Total Waste Cost</div>
    <div class="kpi-value">${total_waste_cost:,.0f}</div>
    <div class="kpi-sub">Across {total_records} records</div>
  </div>
  <div class="kpi red">
    <div class="kpi-label">Average Waste Rate</div>
    <div class="kpi-value">{avg_waste_pct:.1f}%</div>
    <div class="kpi-sub">{total_wasted:,.0f} of {total_ordered:,.0f} units wasted</div>
  </div>
  <div class="kpi green">
    <div class="kpi-label">Potential Savings</div>
    <div class="kpi-value">${total_savings:,.0f}</div>
    <div class="kpi-sub">{total_savings/total_waste_cost*100:.1f}% reduction achievable</div>
  </div>
  <div class="kpi purple">
    <div class="kpi-label">High-Waste Alerts</div>
    <div class="kpi-value">{high_waste_count}</div>
    <div class="kpi-sub">${high_waste_cost:,.0f} in records ≥18% waste</div>
  </div>
</div>

<div class="dashboard">

  <div class="section">
    <div class="section-title">📊 Material Analysis</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Waste % Distribution by Material</div>
        {fig_to_div(fig1, 'chart1')}
      </div>
      <div class="card">
        <div class="card-title">Waste Cost Share by Material</div>
        {fig_to_div(fig2, 'chart2')}
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">🏢 Supplier Performance</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Waste % Heatmap (Supplier × Material)</div>
        {fig_to_div(fig3, 'chart3')}
      </div>
      <div class="card">
        <div class="card-title">Avg Waste % by Supplier & Material</div>
        {fig_to_div(fig4, 'chart4')}
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">🔍 Deep Dive</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Order Size vs Waste % (bubble = cost)</div>
        {fig_to_div(fig5, 'chart5')}
      </div>
      <div class="card">
        <div class="card-title">Project Type: Cost vs Waste Rate</div>
        {fig_to_div(fig6, 'chart6')}
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">📈 Concentration & Distribution</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Pareto: Top {n_80} records = 80% of waste cost</div>
        {fig_to_div(fig7, 'chart7')}
      </div>
      <div class="card">
        <div class="card-title">Waste % Frequency Distribution</div>
        {fig_to_div(fig9, 'chart9')}
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">🗺️ Waste Cost Breakdown</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Treemap: Material → Supplier (color = waste %)</div>
        {fig_to_div(fig8, 'chart8')}
      </div>
      <div class="card">
        <div class="card-title">Savings Potential by Material</div>
        {fig_to_div(fig11, 'chart11')}
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">🚨 Top 15 Highest Waste-Cost Records</div>
    <div class="card card-full">
      {fig_to_div(fig10, 'chart10')}
    </div>
  </div>

  <div class="recommendations">
    <div class="section-title" style="border:none; margin:0; padding:0;">💡 Optimization Recommendations</div>
    <div class="rec-grid">
      <div class="rec">
        <h4>1. Material-Specific Supplier Routing</h4>
        <p>Route Concrete & Steel to <strong>Supplier D</strong> (11.4% / 12.2%), Asphalt to <strong>Supplier C</strong> (11.7%), Wood to <strong>Supplier A</strong> (11.8%). Each supplier has a material sweet spot.</p>
      </div>
      <div class="rec">
        <h4>2. Audit 74 High-Waste Records (≥18%)</h4>
        <p>These represent 14.8% of records but <strong>$955K in waste</strong>. Root-cause analysis here delivers the fastest ROI. Top offender: PRJ-1000 wasted $41K alone.</p>
      </div>
      <div class="rec">
        <h4>3. Fix Demand Forecasting</h4>
        <p>Ordered_Qty vs Waste_Qty correlation is <strong>r=0.84</strong> — larger orders waste proportionally more. Implement just-in-time ordering with 5% buffer instead of blanket over-ordering.</p>
      </div>
      <div class="rec">
        <h4>4. Set Waste KPI Thresholds</h4>
        <p>Flag any project exceeding <strong>15% waste</strong> for immediate review. Target benchmarks: Concrete/Steel/Asphalt at 8%, Wood at 10%. This alone saves <strong>$1.53M</strong>.</p>
      </div>
    </div>
  </div>

</div>

<div class="footer">
  Construction Waste Optimization Dashboard · Generated from 500 project records · github.com/freddycmd/construction-waste-analysis
</div>

</body>
</html>'''

with open('dashboard.html', 'w') as f:
    f.write(html)

print(f"✅ Dashboard written: dashboard.html ({len(html):,} bytes)")
