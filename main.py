# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 10:34:28 2020

@author: bdobson
"""
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

#Addresses
data_root = os.path.join("C:\\","Users","bdobson","Documents","data","population_data")

shape_fn = os.path.join("C:\\","Users","bdobson","OneDrive - Imperial College London","maps","traced_maps","thames_water_wastewater_zones_traced.shp")
pop_fn = os.path.join(data_root, "household_size.csv") # from https://www.nomisweb.co.uk/census/2011/qs406uk
loc_fn = os.path.join(data_root, "NSPL_NOV_2019_UK.csv") # https://geoportal.statistics.gov.uk/datasets/national-statistics-postcode-lookup-november-2019
oa_fn = os.path.join(data_root, "oa_2_postcode.csv") # https://geoportal.statistics.gov.uk/datasets/80628f9289574ba4b39a76ca7830b7e9_0/data

#Load and format
loc_df = pd.read_csv(loc_fn, sep=',')
loc_df = loc_df[['pcds','oseast1m','osnrth1m']]

oa_df = pd.read_csv(oa_fn, sep=',')
oa_df = pd.merge(oa_df,loc_df, on = 'pcds')
oa_df = oa_df[['oa11', 'oseast1m', 'osnrth1m']]

gdf = gpd.read_file(shape_fn)

#Make geoms and combine
oa_df['geometry'] = [Point(xy) for xy in zip(oa_df.oseast1m, oa_df.osnrth1m)]
oa_df = gpd.GeoDataFrame(oa_df, crs = gdf.crs)

oas_of_interest = gpd.sjoin(gdf, oa_df, op="contains")
oas_of_interest = oas_of_interest[['zone_name', 'oa11']].drop_duplicates()

#Load pop
pop_df = pd.read_csv(pop_fn, sep=',')

#Merge and sum
df = pd.merge(oas_of_interest, pop_df, left_on = 'oa11', right_on = 'geography')
gb = df.drop('date',axis=1).groupby('zone_name').sum()

#Add population
gb['total_population'] = 0
for i in range(1,9):
    gb['total_population'] += gb.iloc[:,i] * i

gb.columns = ['total_households'] + [str(x) + '_person' for x in range(1,9)] + ['total_population']
gb = gb.rename(columns = {'8_person' : '8+_person'})

#Print
gb.to_csv('formatted_population_data.csv', sep=',')
