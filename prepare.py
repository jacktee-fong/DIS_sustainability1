import pandas as pd


df = pd.read_csv("store/clean_data.csv")
df_basic = pd.read_csv("store/basic_data.csv")

# calculate gfa
gfa_dict = {}
for index, rows in df_basic.iterrows():
    net_area = rows["net_area"].replace(",", "")
    net_area = int(net_area)
    gfa_dict[rows["code"]] = net_area / 10.764


for i in range(len(df)):
    df.at[i, "gfa"] = gfa_dict[df.iloc[i]["code"]]


df["EUI"] = df["energy"] / df["gfa"]

df.to_csv("store/clean_data.csv", index=False)
df.to_excel("store/clean_data.xlsx", index=False)
