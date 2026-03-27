"""
Export Tableau-ready dataset with calculated fields and clean formatting.
"""
import pandas as pd

df = pd.read_csv('/home/ubuntu/.openclaw/workspace/construction_waste_analysis/material_waste_dataset.csv')

# Add calculated fields Tableau users would want
df['Waste_Rate_Category'] = pd.cut(df['Waste_%'], 
    bins=[0, 8, 12, 15, 20], 
    labels=['Low (<8%)', 'Moderate (8-12%)', 'High (12-15%)', 'Critical (>15%)'])

df['Efficiency_%'] = round(100 - df['Waste_%'], 2)

# Cost metrics
df['Total_Material_Cost'] = round(df['Ordered_Qty'] * df['Unit_Cost'], 2)
df['Used_Material_Cost'] = round(df['Used_Qty'] * df['Unit_Cost'], 2)
df['Cost_Efficiency_%'] = round(df['Used_Material_Cost'] / df['Total_Material_Cost'] * 100, 2)

# Industry benchmarks for comparison
benchmarks = {'Concrete': 8, 'Steel': 8, 'Asphalt': 8, 'Wood': 10}
df['Industry_Benchmark_%'] = df['Material'].map(benchmarks)
df['Above_Benchmark'] = df['Waste_%'] > df['Industry_Benchmark_%']
df['Excess_Waste_%'] = round((df['Waste_%'] - df['Industry_Benchmark_%']).clip(lower=0), 2)
df['Excess_Waste_Cost'] = round(
    (df['Excess_Waste_%'] / 100) * df['Ordered_Qty'] * df['Unit_Cost'], 2
)

# Supplier rank per material (1 = best)
sup_rank = df.groupby(['Material', 'Supplier'])['Waste_%'].mean().reset_index()
sup_rank['Supplier_Rank'] = sup_rank.groupby('Material')['Waste_%'].rank(method='dense').astype(int)
df = df.merge(sup_rank[['Material', 'Supplier', 'Supplier_Rank']], on=['Material', 'Supplier'], how='left')

# Order size buckets
df['Order_Size'] = pd.cut(df['Ordered_Qty'],
    bins=[0, 200, 500, 800, 1300],
    labels=['Small (<200)', 'Medium (200-500)', 'Large (500-800)', 'XL (>800)'])

# Reorder columns logically for Tableau
col_order = [
    'Project_ID', 'Material', 'Project_Type', 'Supplier', 'Supplier_Rank',
    'Ordered_Qty', 'Used_Qty', 'Waste_Qty', 'Order_Size',
    'Unit_Cost', 'Total_Material_Cost', 'Used_Material_Cost', 'Waste_Cost',
    'Waste_%', 'Efficiency_%', 'Waste_Rate_Category',
    'Industry_Benchmark_%', 'Above_Benchmark', 'Excess_Waste_%', 'Excess_Waste_Cost',
    'Cost_Efficiency_%'
]
df = df[col_order]

# Save
df.to_csv('/home/ubuntu/.openclaw/workspace/construction_waste_analysis/tableau_waste_analysis.csv', index=False)
df.to_excel('/home/ubuntu/.openclaw/workspace/construction_waste_analysis/tableau_waste_analysis.xlsx', index=False, sheet_name='Waste Data')

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"\nColumns:\n{chr(10).join(df.columns)}")
print(f"\nSample:")
print(df.head(3).to_string())
print(f"\n✅ Exported: tableau_waste_analysis.csv + .xlsx")
