import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

n = 500

materials = ['Concrete', 'Steel', 'Asphalt', 'Wood']
suppliers = {
    'Concrete': ['MixMaster Inc.', 'SolidBase Supply', 'GreyCrete Co.'],
    'Steel': ['IronClad Industries', 'SteelForge Ltd.', 'MetalPrime Corp.'],
    'Asphalt': ['BlackTop Solutions', 'PavePro Inc.', 'RoadMix Supply'],
    'Wood': ['TimberLine Co.', 'WoodWorks Supply', 'GreenLumber Inc.']
}
project_types = ['Residential', 'Commercial', 'Infrastructure', 'Industrial']

# Unit cost ranges per material (per unit)
unit_cost_ranges = {
    'Concrete': (85, 140),
    'Steel': (600, 1100),
    'Asphalt': (70, 120),
    'Wood': (40, 90)
}

# Waste % distributions per material (mean, std) — realistic
waste_profiles = {
    'Concrete': (8, 4),
    'Steel': (5, 3),
    'Asphalt': (6, 3.5),
    'Wood': (12, 5)
}

records = []
for i in range(n):
    pid = f"PRJ-{1000 + i}"
    material = random.choice(materials)
    project_type = random.choice(project_types)
    supplier = random.choice(suppliers[material])

    # Ordered quantity
    ordered = round(np.random.uniform(50, 2000), 1)

    # Waste %
    mean_w, std_w = waste_profiles[material]
    waste_pct = max(0.5, round(np.random.normal(mean_w, std_w), 2))
    waste_pct = min(waste_pct, 35)  # cap outliers

    waste_qty = round(ordered * waste_pct / 100, 1)
    used_qty = round(ordered - waste_qty, 1)

    lo, hi = unit_cost_ranges[material]
    unit_cost = round(np.random.uniform(lo, hi), 2)
    waste_cost = round(waste_qty * unit_cost, 2)

    records.append({
        'Project_ID': pid,
        'Material': material,
        'Used_Qty': used_qty,
        'Ordered_Qty': ordered,
        'Waste_Qty': waste_qty,
        'Waste_%': waste_pct,
        'Unit_Cost': unit_cost,
        'Waste_Cost': waste_cost,
        'Supplier': supplier,
        'Project_Type': project_type
    })

df = pd.DataFrame(records)
df.to_csv('construction_waste_data.csv', index=False)
print(f"Generated {len(df)} records")
print(f"\nMaterial distribution:\n{df['Material'].value_counts()}")
print(f"\nProject type distribution:\n{df['Project_Type'].value_counts()}")
print(f"\nWaste % summary by material:")
print(df.groupby('Material')['Waste_%'].describe().round(2))
print(f"\nTotal waste cost: ${df['Waste_Cost'].sum():,.2f}")
