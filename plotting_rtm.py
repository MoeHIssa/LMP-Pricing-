import pandas as pd
import matplotlib.pyplot as plt
import os

# Define file paths
file_paths = {
    "CAISO_load": "path/to/CAISO_Historical_Ems_Hourly_Load.xlsx",
    "DAM": "path/to/2023_2024_LMP_DAM_Data.xlsx",
    "RTM_2023": "path/to/2023_LMP_RTM_Data.xlsx",
    "RTM_2024": "path/to/2024_LMP_RTM_Data.xlsx"
}

# Time range
start_date = "2023-01-01"
end_date = "2024-11-30"

# Node mapping for renaming
node_map = {
    "WESTWING_5_N501": "WestWing",
    "PALOVRDE_ASR-APND": "Palo Verde",
    "WILOWBCH_6_ND001": "Willow Beach"
}

# Function to save plot
def save_plot(fig, filename):
    output_path = f"{filename}.png"
    fig.savefig(output_path)
    print(f"Plot saved to {output_path}")
    plt.close(fig)

# Load CAISO data and plot
caiso_data = pd.read_excel(file_paths["CAISO_load"])
caiso_data["Date"] = pd.to_datetime(caiso_data["Date"])
caiso_data = caiso_data[(caiso_data["Date"] >= start_date) & (caiso_data["Date"] <= end_date)]

# Plot CAISO Load
fig, ax = plt.subplots()
ax.plot(caiso_data["Date"], caiso_data["CAISO"], label="CAISO Load", color="blue")
ax.set_title("CAISO Historical EMS Hourly Load")
ax.set_xlabel("Date")
ax.set_ylabel("Load (MW)")
ax.grid(True)
save_plot(fig, "CAISO_Historical_Load")

# Load LMP data
lmp_dam = pd.read_excel(file_paths["DAM"])
lmp_rtm_2023 = pd.read_excel(file_paths["RTM_2023"])
lmp_rtm_2024 = pd.read_excel(file_paths["RTM_2024"])

# Combine RTM data
lmp_rtm = pd.concat([lmp_rtm_2023, lmp_rtm_2024])

# Filter LMP data
lmp_dam["OPR_DT"] = pd.to_datetime(lmp_dam["OPR_DT"])
lmp_rtm["OPR_DT"] = pd.to_datetime(lmp_rtm["OPR_DT"])
lmp_dam = lmp_dam[(lmp_dam["OPR_DT"] >= start_date) & (lmp_dam["OPR_DT"] <= end_date)]
lmp_rtm = lmp_rtm[(lmp_rtm["OPR_DT"] >= start_date) & (lmp_rtm["OPR_DT"] <= end_date)]

# Rename nodes
lmp_dam["NODE_ID"] = lmp_dam["NODE_ID"].replace(node_map)
lmp_rtm["NODE_ID"] = lmp_rtm["NODE_ID"].replace(node_map)

# Plot LMP Total Pricing by Node (DAM)
for node in node_map.values():
    node_data = lmp_dam[lmp_dam["NODE_ID"] == node]
    fig, ax = plt.subplots()
    ax.plot(node_data["OPR_DT"], node_data["$/MWh"], label=f"{node} Total LMP", color="green")
    ax.set_title(f"LMP Total Pricing - {node} (DAM)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($/MWh)")
    ax.grid(True)
    save_plot(fig, f"LMP_Total_Pricing_{node}_DAM")

# Combined Nodes Plot (DAM)
fig, ax = plt.subplots()
for node in node_map.values():
    node_data = lmp_dam[lmp_dam["NODE_ID"] == node]
    ax.plot(node_data["OPR_DT"], node_data["$/MWh"], label=node)
ax.set_title("LMP Total Pricing - All Nodes (DAM)")
ax.set_xlabel("Date")
ax.set_ylabel("Price ($/MWh)")
ax.legend()
ax.grid(True)
save_plot(fig, "LMP_Total_Pricing_All_Nodes_DAM")

# Aggregated LMP Pricing (DAM)
lmp_dam["Day"] = lmp_dam["OPR_DT"].dt.date
lmp_dam_daily = lmp_dam.groupby(["Day", "NODE_ID"])["$/MWh"].mean().reset_index()

fig, ax = plt.subplots()
for node in node_map.values():
    node_data = lmp_dam_daily[lmp_dam_daily["NODE_ID"] == node]
    ax.plot(node_data["Day"], node_data["$/MWh"], label=node)
ax.set_title("Aggregated Daily LMP Pricing (DAM)")
ax.set_xlabel("Date")
ax.set_ylabel("Average Price ($/MWh)")
ax.legend()
ax.grid(True)
save_plot(fig, "Aggregated_Daily_LMP_Pricing_DAM")

# Plot LMP Total Pricing by Node (RTM)
for node in node_map.values():
    node_data = lmp_rtm[lmp_rtm["NODE_ID"] == node]
    fig, ax = plt.subplots()
    ax.plot(node_data["OPR_DT"], node_data["$/MWh"], label=f"{node} Total LMP", color="orange")
    ax.set_title(f"LMP Total Pricing - {node} (RTM)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($/MWh)")
    ax.grid(True)
    save_plot(fig, f"LMP_Total_Pricing_{node}_RTM")

# Combined Nodes Plot (RTM)
fig, ax = plt.subplots()
for node in node_map.values():
    node_data = lmp_rtm[lmp_rtm["NODE_ID"] == node]
    ax.plot(node_data["OPR_DT"], node_data["$/MWh"], label=node)
ax.set_title("LMP Total Pricing - All Nodes (RTM)")
ax.set_xlabel("Date")
ax.set_ylabel("Price ($/MWh)")
ax.legend()
ax.grid(True)
save_plot(fig, "LMP_Total_Pricing_All_Nodes_RTM")

# Aggregated LMP Pricing (RTM)
lmp_rtm["Day"] = lmp_rtm["OPR_DT"].dt.date
lmp_rtm_daily = lmp_rtm.groupby(["Day", "NODE_ID"])["$/MWh"].mean().reset_index()

fig, ax = plt.subplots()
for node in node_map.values():
    node_data = lmp_rtm_daily[lmp_rtm_daily["NODE_ID"] == node]
    ax.plot(node_data["Day"], node_data["$/MWh"], label=node)
ax.set_title("Aggregated Daily LMP Pricing (RTM)")
ax.set_xlabel("Date")
ax.set_ylabel("Average Price ($/MWh)")
ax.legend()
ax.grid(True)
save_plot(fig, "Aggregated_Daily_LMP_Pricing_RTM")

print("All plots have been generated and saved.")
