code_dict = {
    "SGX Centre 1": "SGX1",
    "SGX Centre 2": "SGX2",
    "Tampines Plaza 1": "TP1",
    "Tampines Plaza 2": "TP2",
    "Stamford Court": "SC",
    "SingaporeLand Tower": "SLT",
    "UIC Buildng": "UIC",
    "The Gateway": "GWY"
}

icon_dict = {
    "energy": "fa fa-bolt",
    "water": "fa fa-bath",
    "arrow_up": "fa fa-arrow-up",
    "arrow_down": "fa fa-arrow-down"
}


color_dict = {
    "water": (90/255, 219/255, 255/255),
    "energy": (179/255, 222/255, 193/255),
    "EUI": (55/255, 169/255, 89/255),
    "WEI_Area": (58/255, 134/255, 255/255),
    "WEI_People": (0/255, 78/255, 204/255),
    "carbon_index": (255/255, 190/255, 11/255),
    "carbon_total": (163/255, 120/255, 0/255),
    "carbon_energy": (51/255, 113/255, 83/255),
    "carbon_water": (0/255, 47/255, 122/255),
    "carbon_waste": (0/255, 16/255, 41/255),
    "WDI": (0/255, 0/255, 0/255),

}


kpi_dict = {
    "water": {"name": "Water", "unit": "m3/month", "color": color_dict["water"]},
    "energy": {"name": "Electricity", "unit": "kwh/month", "color": color_dict["energy"]},
    "EUI": {"name": "Energy Utilisation Index", "unit": "kwh/m2/year", "color": color_dict["EUI"]},
    "WEI_Area": {"name": "Water Efficiency Index (Area)", "unit": "m3/m2/year", "color": color_dict["WEI_Area"]},
    "WEI_People": {"name": "Water Efficiency Index (People)", "unit": "l/person/day",
                   "color": color_dict["WEI_People"]},
    "carbon_index": {"name": "Carbon Index", "unit": "kg/m2/person", "color": color_dict["energy"]},
    "carbon_total": {"name": "Total CO2 Emission", "unit": "kg/year CO2e", "color": color_dict["energy"]},
    "carbon_energy": {"name": "Total CO2 Emission (Electricity)", "unit": "kg/year CO2e",
                      "color": color_dict["energy"]},
    "carbon_water": {"name": "Total CO2 Emission (Water)", "unit": "kg/year CO2e", "color": color_dict["energy"]},
    "carbon_waste": {"name": "Total CO2 Emission (Waste)", "unit": "kg/year CO2e", "color": color_dict["energy"]},
    "WDI": {"name": "Waste Disposal Index", "unit": "kg/year", "color": color_dict["energy"]},
}

benchmark_dict = {"EUI": {"type": "SUM",
                          "benchmark": {"EUI_Benchmark": [215, 215, 211, 211, 211, 211, 211]},
                          "month_unit": "kwh/m2/month", "year_unit": "kwh/m2/year"},
                  "WEI_Area": {"type": "SUM",
                               "benchmark": {"Office Top10": [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
                                             "Office Median": [1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13]},
                               "month_unit": "m3/m2/month", "year_unit": "m3/m2/year"},
                  "WEI_People": {"type": "AVERAGE",
                                 "benchmark": {"Retail Top 10": [1.6, 1.6, 1.6, 1.6, 1.6, 1.6, 1.6],
                                               "Retail Median": [3.05, 3.05, 3.05, 3.05, 3.05, 3.05, 3.05]},
                                 "month_unit": "l/person/day", "year_unit": "l/person/day"},
                  "carbon_index": {"type": "AVERAGE", "benchmark": {},
                                   "month_unit": "kg/m2/person", "year_unit": "kg/m2/person"},
                  "carbon_total": {"type": "SUM", "benchmark": {},
                                   "month_unit": "kg/month CO2e", "year_unit": "kg/year CO2e"},
                  "carbon_energy": {"type": "SUM", "benchmark": {},
                                    "month_unit": "kg/month CO2e", "year_unit": "kg/year CO2e"},
                  "carbon_water": {"type": "SUM", "benchmark": {},
                                   "month_unit": "kg/month CO2e", "year_unit": "kg/year CO2e"},
                  "carbon_waste": {"type": "SUM", "benchmark": {},
                                   "month_unit": "kg/month CO2e", "year_unit": "kg/year CO2e"},
                  "WDI": {"type": "SUM", "benchmark": {},
                          "month_unit": "kg/month CO2e", "year_unit": "kg/year CO2e"},
                  }
