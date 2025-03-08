import os.path
import pdb

import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import numpy as np


throughputs_path = '..\\throughputs\\'
required_cols = ['Geography', 'GEO_TYPE_ABBR_EN', 'ALT_GEO_CODE_EN', 'PR_CODE_EN']
test_geo = ["Bay Roberts", "Conception Bay South", "St. John's", "Corner Brook", "Sylvan Lake"]

class PrepareTables:
    def __init__(self, master_data_filepath, transit_filepath):
        self.master_data_filepath = master_data_filepath
        self.transit_filepath = transit_filepath

        print('Reading Input master data...')
        self.master_data = PrepareTables.clean_input_data(
            pd.read_excel(self.master_data_filepath, sheet_name='Master - All geos', header=[1]))
        
        print('Input master data loaded...')

        self.transit_data = pd.read_csv(self.transit_filepath)


    def prepare_output_1(self, future=''):
        print("Preparing Output 1")

        output_1_columns = ['CSDUID', f'200m{future}Transit_Access', 
                             f'200m{future}Transit_PerHHAccess', 
                            f'800m{future}Transit_Access', f'800m{future}Transit_PerHHAccess']
        
        try:
            output_1 = self.transit_data[output_1_columns].rename(columns={
                'CSDUID': 'ALT_GEO_CODE_EN'})

        except KeyError:
            print('Some columns from output 1 were not found')

        output_1_long = output_1.melt(id_vars=output_1.columns[0], var_name="Data", value_name="Value")
        output_1_long['Characteristic'] = np.where(output_1_long['Data'].str.contains('200'), 
                                                    'Households within 200m of a rail/light-rail transit station (#)',
                                                'Households within 800m of a rail/light-rail transit station (#)')

        output_1_final = output_1_long.sort_values(by=['ALT_GEO_CODE_EN']).replace(
            f'200m{future}Transit_Access', 'Total').replace(f'800m{future}Transit_Access', 'Total').replace(
            f'200m{future}Transit_PerHHAccess', 'Percentage of all HHs').replace(f'800m{future}Transit_PerHHAccess', 
                                                                                 'Percentage of all HHs')
        
        # export to csv
        output_1_final.to_csv(os.path.join(throughputs_path, f"Output1{future}.csv"))
        print("Output 1 Successfully created...")

        return output_1_final

        

    def prepare_output_2(self):
        print("Preparing Output 2...")
        
        output_2_columns = required_cols + [col for col in self.master_data.columns if col.startswith('Avg_Rent_')]
        assert len(output_2_columns) != len(required_cols), "The required columns are not fetched"

        
        try:
            output_2 = self.master_data[output_2_columns]
            # output_2 = output_2[output_2['Geography'].isin(test_geo)]

        except KeyError:
            print('Some columns from output 2 were not found')

        output_2_long = output_2.melt(id_vars=required_cols, var_name="Year", value_name="Avg Monthly Rent")

        output_2_long["Year"] = output_2_long["Year"].str.extract(r"(\d{4})")
        output_2_long["Avg Monthly Rent"] = pd.to_numeric(output_2_long["Avg Monthly Rent"], errors="coerce")

        # Sort by Geography and Year
        output_2_long = output_2_long.sort_values(by=required_cols+["Year"])

        # Calculate change in Avg Rent
        output_2_long["Change in Avg Rent"] = output_2_long.groupby(required_cols)["Avg Monthly Rent"].diff()
        output_2_long["% Change in Avg Rent"] = output_2_long["Change in Avg Rent"] / output_2_long.groupby(required_cols)["Avg Monthly Rent"].shift(1) * 100

        # Pivot the table into the desired format
        output_2_final = output_2_long.melt(id_vars=required_cols+["Year"], var_name="Metric", value_name="Value")

        # Pivot for final structure
        output_2_final = output_2_final.pivot_table(index=required_cols+["Metric"], columns="Year", values="Value", aggfunc="first")

        output_2_final.reset_index(inplace=True)
        output_2_final = output_2_final.sort_values(by=required_cols+["Metric"])

        # export to csv
        output_2_final.to_csv(os.path.join(throughputs_path, "Output2.csv"))
        print("Output 2 Successfully created...")

        return output_2_final

    def prepare_output_3(self):

        print("Preparing Output 3...")
        output_3_columns = required_cols + [col for col in self.master_data.columns if col.startswith('Vacancy_')]
        assert len(output_3_columns) != len(required_cols), "The required columns are not fetched"

        
        try:
            output_3 = self.master_data[output_3_columns]
            # output_3 = output_3[output_3['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 3 were not found')

        output_3_long = output_3.melt(id_vars=required_cols, var_name="Year", value_name="Vacancy Rate")

        output_3_long["Year"] = output_3_long["Year"].str.extract(r"(\d{4})")
        output_3_long["Vacancy Rate"] = pd.to_numeric(output_3_long["Vacancy Rate"], errors="coerce")

        # Sort by Geography and Year
        output_3_long = output_3_long.sort_values(by=required_cols+["Year"])

        # Calculate change in Vacancy Rate
        output_3_long["Change in Vacancy Rate"] = output_3_long.groupby(required_cols)["Vacancy Rate"].diff()

        # Pivot the table into the desired format
        output_3_final = output_3_long.melt(id_vars=required_cols+["Year"], var_name="Metric", value_name="Value")

        # Pivot for final structure
        output_3_final = output_3_final.pivot_table(index=required_cols+["Metric"], columns="Year", values="Value", aggfunc="first")

        output_3_final.reset_index(inplace=True)
        output_3_final = output_3_final.sort_values(by=required_cols+["Metric"])

        # export to csv
        output_3_final.to_csv(os.path.join(throughputs_path, "Output3.csv"))
        print("Output 3 Successfully created...")

        return output_3_final
    
    def prepare_output_4a(self):
        print("Preparing Output 4a...")
        output_4a_columns = required_cols + [col for col in self.master_data.columns if col.startswith('Starts_Structure_')]
        assert len(output_4a_columns) != len(required_cols), "The required columns are not fetched"
        
        try:
            output_4a = self.master_data[output_4a_columns]
            # output_4a = output_4a[output_4a['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 4a were not found')

        output_4a_long = output_4a.melt(id_vars=required_cols, var_name="Variable", value_name="Value")

        # Extract Year and Metric Type
        output_4a_long["Year"] = output_4a_long["Variable"].str.extract(r'(\d{4})').astype(int)
        output_4a_long["Metric"] = output_4a_long["Variable"].str.replace(r'Starts_Structure_|_\d{4}', '', regex=True)

        output_4a_long = output_4a_long.drop(columns=["Variable"])

        # Pivot to the required format
        output_4a_final = output_4a_long.pivot_table(index=required_cols+["Metric"], columns="Year", values="Value", aggfunc="first")

        output_4a_final.reset_index(inplace=True)
        output_4a_final = output_4a_final.sort_values(by=required_cols+["Metric"]).replace('Semis', 'Semi-detached').replace('Singles', 'Single-detached')

        
        # Check if the sums are zero...
        years = [col for col in output_4a_final.columns if isinstance(col, int) or col.isdigit()]  

        # Iterate over each (id, Geography) group
        for (id_val, geo), group in output_4a_final.groupby(["ALT_GEO_CODE_EN", "Geography"]):
            total_row = group[group["Metric"] == "Total"]
            other_rows = group[group["Metric"] != "Total"]
            
            for year in years:
                year = int(year)
                # Sum all components (Singles, Semis, Row, Apartment)
                other_rows[year] = pd.to_numeric(other_rows[year], errors='coerce')
                calculated_total = other_rows[year].sum()
                
                total_row[year] = pd.to_numeric(total_row[year], errors='coerce')
                expected_total = total_row[year].values[0] if not pd.isna(total_row[year].values[0]) else 0

                # Assertion to check the condition
                assert expected_total == calculated_total, f"Mismatch in Total for id={id_val}, Geography={geo}, Year={year}"

        # export to csv
        output_4a_final.to_csv(os.path.join(throughputs_path, "Output4a.csv"))
        print("Output 4a Successfully created...")

        return output_4a_final


    def prepare_output_4b(self):
        print("Preparing Output 4b...")
        output_4b_columns = required_cols + [col for col in self.master_data.columns if col.startswith('Starts_Market_')]
        assert len(output_4b_columns) != len(required_cols), "The required columns are not fetched"

        
        try:
            output_4b = self.master_data[output_4b_columns]
            # output_4b = output_4b[output_4b['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 4b were not found')
    
        output_4b_long = output_4b.melt(id_vars=required_cols, var_name="Variable", value_name="Value")

        # Extract Year and Metric Type
        output_4b_long["Year"] = output_4b_long["Variable"].str.extract(r'(\d{4})').astype(int)
        output_4b_long["Metric"] = output_4b_long["Variable"].str.replace(r'Starts_Market_|_\d{4}', '', regex=True)

        output_4b_long = output_4b_long.drop(columns=["Variable"])

        # Pivot to the required format
        output_4b_final = output_4b_long.pivot_table(index=required_cols+["Metric"], columns="Year", values="Value", aggfunc="first")

        output_4b_final.reset_index(inplace=True)
        output_4b_final = output_4b_final.sort_values(by=required_cols+["Metric"]).replace('Coop', 'Co-op').replace('NA', 'N/A')

        
        # Check if the sums are zero...
        years = [col for col in output_4b_final.columns if isinstance(col, int) or col.isdigit()]  

        # Iterate over each (id, Geography) group
        for (id_val, geo), group in output_4b_final.groupby(["ALT_GEO_CODE_EN", "Geography"]):
            total_row = group[group["Metric"] == "Total"]
            other_rows = group[group["Metric"] != "Total"]
            
            for year in years:
                year = int(year)
                # Sum all components (Condo, Rental, Owner, NA, Coop)
                other_rows[year] = pd.to_numeric(other_rows[year], errors='coerce')
                calculated_total = other_rows[year].sum()
                
                total_row[year] = pd.to_numeric(total_row[year], errors='coerce')
                expected_total = total_row[year].values[0] if not pd.isna(total_row[year].values[0]) else 0

                # Assertion to check the condition
                assert expected_total == calculated_total, f"Mismatch in Total for id={id_val}, Geography={geo}, Year={year}"

        
        # export to csv
        output_4b_final.to_csv(os.path.join(throughputs_path, "Output4b.csv"))
        print("Output 4b Successfully created...")

        return output_4b_final


    def prepare_output_5a(self):

        print("Preparing Output 5a...")
        output_5a_columns = required_cols + [col for col in self.master_data.columns if col.startswith('CHN_Owner_') or (col.startswith('CHN_Renter_'))]
        assert len(output_5a_columns) != len(required_cols), "The required columns are not fetched"

        
        try:
            output_5a = self.master_data[output_5a_columns]
            # output_5a = output_5a[output_5a['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 5a were not found')

        output_5a_long = output_5a.melt(id_vars=required_cols, var_name="Variable", value_name="Value")

        # Extract Year and Metric Type
        output_5a_long["Year"] = output_5a_long["Variable"].str.extract(r'(\d{4})').astype(int)
        output_5a_long["Metric"] = output_5a_long["Variable"].str.replace(r'CHN_|_\d{4}', '', regex=True)

        output_5a_long = output_5a_long.drop(columns=["Variable"])
   
        output_5a_final = output_5a_long.pivot_table(index=required_cols+["Metric"], columns="Year", values="Value", aggfunc="first")
        output_5a_final.reset_index(inplace=True)

        output_5a_final[2021] = pd.to_numeric(output_5a_final[2021], errors='coerce')
        output_5a_final[2016] = pd.to_numeric(output_5a_final[2016], errors='coerce')

        output_5a_final['2021 - 2016'] = output_5a_final[2021] - output_5a_final[2016]
        output_5a_final['% change in # of HH in CHN by tenure'] = (output_5a_final[2021] - output_5a_final[2016]) / output_5a_final[2016]

        output_5a_final = output_5a_final.sort_values(by=required_cols+["Metric"])

        # export to csv
        output_5a_final.to_csv(os.path.join(throughputs_path, "Output5a.csv"))
        print("Output 5a Successfully created...")

        return output_5a_final
    
    def prepare_output_5b(self, output_5a):

        print("Preparing Output 5b...")
        output_5b_columns = required_cols + [col for col in self.master_data.columns if col.startswith('ExaminedForCHN_')]
        assert len(output_5b_columns) != len(required_cols), "The required columns are not fetched"

        
        try:
            output_5b = self.master_data[output_5b_columns]
            # output_5b = output_5b[output_5b['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 5b were not found')

        output_5b_long = output_5b.melt(id_vars=required_cols, var_name="Variable", value_name="Value")

        # Extract Year and Metric Type
        output_5b_long["Year"] = output_5b_long["Variable"].str.extract(r'(\d{4})').astype(int)
        output_5b_long["Metric"] = output_5b_long["Variable"].str.replace(r'ExaminedForCHN_|_\d{4}', '', regex=True)

        output_5b_long = output_5b_long.drop(columns=["Variable"])
   
        output_5b_final = output_5b_long.pivot_table(index=required_cols+["Metric"], columns="Year", values="Value", aggfunc="first")

        # Fetch Output 5a for calculation
        output_5a.set_index(required_cols+["Metric"], inplace=True)

        original_length = len(output_5b_final)
        output_5b_final = output_5b_final.join(output_5a[[2016, 2021]], how='left', rsuffix='_5a')
        assert original_length == len(output_5b_final)

        output_5b_final['2021'] = pd.to_numeric(output_5b_final['2021'], errors='coerce')
        output_5b_final['2016'] = pd.to_numeric(output_5b_final['2016'], errors='coerce')

        output_5b_final['2016_5b'] = output_5b_final['2016_5a'] / output_5b_final['2016']
        output_5b_final['2021_5b'] = output_5b_final['2021_5a'] / output_5b_final['2021']

        output_5b_final = output_5b_final.drop(['2016', '2016_5a', '2021', '2021_5a'], axis=1).rename(
            columns={'2016_5b': 2016, '2021_5b': 2021})


        output_5b_final.reset_index(inplace=True)

        output_5b_final['2021 - 2016'] = output_5b_final[2021] - output_5b_final[2016]

        output_5b_final = output_5b_final.sort_values(by=required_cols+["Metric"])

        # export to csv
        output_5b_final.to_csv(os.path.join(throughputs_path, "Output5b.csv"))
        print("Output 5b Successfully created...")

        return output_5b_final
    
    def prepare_output_6(self):

        print("Preparing Output 6...")
        output_6_columns = required_cols + ['2021_All_Renters',	'2021_Primary_Renters']
        assert len(output_6_columns) != len(required_cols), "The required columns are not fetched"
        
        try:
            output_6 = self.master_data[output_6_columns]
            # output_6 = output_6[output_6['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 6 were not found')

        output_6['2021_All_Renters'] = pd.to_numeric(output_6['2021_All_Renters'], errors='coerce')
        output_6['2021_Primary_Renters'] = pd.to_numeric(output_6['2021_Primary_Renters'], errors='coerce')
        
        output_6['2021_Secondary_Renters'] = output_6['2021_All_Renters'] - output_6['2021_Primary_Renters']

        output_6_long = output_6.melt(id_vars=required_cols, var_name="Variable", value_name="Value")

        # Extract Year and Metric Type
        output_6_long["Year"] = output_6_long["Variable"].str.extract(r'(\d{4})').astype(int)
        output_6_long["Metric"] = output_6_long["Variable"].str.replace(r'\d{4}_', '', regex=True)

        output_6_long = output_6_long.drop(columns=["Variable"])
   
        output_6_final = output_6_long.pivot_table(index=required_cols+["Metric"], columns="Year", values="Value", aggfunc="first")
        output_6_final.reset_index(inplace=True)

        output_6_final = output_6_final.sort_values(by=required_cols+["Metric"]).replace('All_Renters', 'All Rental HHs').replace(
            'Primary_Renters', 'Primary Rental Units').replace('Secondary_Renters', 'Secondary Rental Units')
    
        # export to csv
        output_6_final.to_csv(os.path.join(throughputs_path, "Output6.csv"))
        print("Output 6 Successfully created...")

        return output_6_final
    
    def prepare_output_7(self):

        print("Preparing Output 7...")
        output_7_columns = required_cols + ['2021_All_Renters',	'2021_Subsidized_HHs']
        assert len(output_7_columns) != len(required_cols), "The required columns are not fetched"
        
        try:
            output_7 = self.master_data[output_7_columns]
            # output_7 = output_7[output_7['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 7 were not found')

        output_7['2021_All_Renters'] = pd.to_numeric(output_7['2021_All_Renters'], errors='coerce')
        output_7['2021_Subsidized_HHs'] = pd.to_numeric(output_7['2021_Subsidized_HHs'], errors='coerce')
        
        output_7['2021_Private_Rental'] = output_7['2021_All_Renters'] - output_7['2021_Subsidized_HHs']
        output_7.drop(['2021_All_Renters'], axis=1, inplace=True)

        output_7_long = output_7.melt(id_vars=required_cols, var_name="Variable", value_name="Value")

        # Extract Year and Metric Type
        output_7_long["Year"] = output_7_long["Variable"].str.extract(r'(\d{4})').astype(int)
        output_7_long["Metric"] = output_7_long["Variable"].str.replace(r'\d{4}_', '', regex=True)

        output_7_long = output_7_long.drop(columns=["Variable"])
   
        output_7_final = output_7_long.pivot_table(index=required_cols+["Metric"], columns="Year", values="Value", aggfunc="first")
        output_7_final.reset_index(inplace=True)

        output_7_final = output_7_final.sort_values(by=required_cols+["Metric"]).replace(
            'Subsidized_HHs', 'Subsidized rental housing units').replace(
            'Private_Rental', 'Private rental market housing units')
        # pdb.set_trace()
    
        # export to csv
        output_7_final.to_csv(os.path.join(throughputs_path, "Output7.csv"))
        print("Output 7 Successfully created...")

        return output_7_final
    
    def prepare_output_8(self):
        # Number of unsubsidized rental housing units that are below market rent in the private market (2021)  shelter cost
        print("Preparing Output 8...")
        output_8_columns = required_cols + [col for col in self.master_data.columns if col.endswith('_Unsubsidized')]
        assert len(output_8_columns) != len(required_cols), "The required columns are not fetched"
        
        try:
            output_8 = self.master_data[output_8_columns]
            # output_8 = output_8[output_8['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 8 were not found')

        output_8['Total (sum)'] = output_8.loc[:, output_8.columns.str.endswith('_Unsubsidized')].sum(axis=1)
        support_output_8 = self.master_data[required_cols + ['2021_AMHI']]

        output_8_long = output_8.melt(id_vars=required_cols, var_name="Variable", value_name="Value")

        output_8_long["Renters (unsubsidized)"] = 'Renters (unsubsidized)'
        output_8_long["Metric"] = output_8_long["Variable"].str.replace(r'2021_Shelter_|_Unsubsidized', '', regex=True)

        output_8_long = output_8_long.drop(columns=["Variable"])
   
        output_8_final = output_8_long.pivot_table(index=required_cols+["Metric"], columns="Renters (unsubsidized)", values="Value", aggfunc="first")
        output_8_final.reset_index(inplace=True)

        output_8_final = output_8_final.sort_values(by=required_cols+["Metric"])

        output_8_final["Total_Renters"] = output_8_final.groupby(required_cols)[
            "Renters (unsubsidized)"].transform(lambda x: x.loc[output_8_final["Metric"] == "Total (sum)"].values[0])

        output_8_final['Renters (unsubsidized)'] = pd.to_numeric(output_8_final['Renters (unsubsidized)'], errors='coerce')
        output_8_final['Total_Renters'] = pd.to_numeric(output_8_final['Total_Renters'], errors='coerce')

        # Calculate percentage of total renters (avoid division by zero)
        output_8_final["% of Total (Unsubsidized)"] = (
            output_8_final["Renters (unsubsidized)"]
            .div(output_8_final["Total_Renters"].replace(0, float('nan')))  
        )

        # Drop the total renters column if not needed
        output_8_final.drop(columns=["Total_Renters"], inplace=True)

        filtered_output_8 = output_8_final[
            output_8_final['Metric'].isin(['VeryLow', 'Low', 'Moderate'])].groupby(
                required_cols)[['Renters (unsubsidized)', '% of Total (Unsubsidized)']].sum().reset_index()

        # export to csv
        filtered_output_8.to_csv(os.path.join(throughputs_path, "Output8.csv"))
        print("Output 8 Successfully created...")

        return filtered_output_8

    def prepare_output_9_and_10(self):
        #changes to headship rates by age 2016 vs 2021
        print("Preparing Output 9...")
        output_9_columns = required_cols + [col for col in self.master_data.columns if col.endswith('_Unsubsidized')]
        assert len(output_9_columns) != len(required_cols), "The required columns are not fetched"

        try:
            output_9 = self.master_data[output_9_columns]
            # output_9 = output_9[output_9['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 9 were not found')

        output_9_columns = required_cols + [col for col in self.master_data.columns if 'Pop' in col] + [col for col in
                                                                                                     self.master_data.columns
                                                                                                     if 'PHM' in col]
        output_9 = self.master_data[output_9_columns]
        output_9_long = output_9.melt(id_vars=required_cols, var_name="Variable", value_name="Value")
        output_9_long = output_9_long[output_9_long['Variable'] != 'Population, 2021'] #filter out total pop
        #clean data
        output_9_long['Value'].replace('x', np.nan, inplace=True)
        output_9_long.replace('F', np.nan, inplace=True)
        #expand Variable into 3 columns
        expanded_cols = output_9_long['Variable'].str.split(pat='_', expand=True)
        expanded_cols.rename(columns={0: 'Year', 1: "Age", 2: "pop_or_PHM"}, inplace=True)
        #join 3 expanded columns back to larger dataframe
        output_9_long_expanded = pd.concat([output_9_long, expanded_cols], axis=1)
        #set data types to correct ones
        dtype_dict = {"Variable": str, "Year": np.int64, "Age": str, "pop_or_PHM": str}
        output_9_long_expanded = output_9_long_expanded.astype(dtype_dict)
        pivot_df = output_9_long_expanded.pivot_table(index=required_cols + ["Age"], columns=["Year", "pop_or_PHM"],
                                                      values="Value", aggfunc="first")
        # keep all years for now to calculate headship rates
        pivot_df[(2006, 'Headship')] = pivot_df[(2006, 'PHM')] / pivot_df[(2006, 'Pop')]
        pivot_df[(2016, 'Headship')] = pivot_df[(2016, 'PHM')] / pivot_df[(2016, 'Pop')]
        pivot_df[(2021, 'Headship')] = pivot_df[(2021, 'PHM')] / pivot_df[(2021, 'Pop')]
        pivot_df[("Overall", 'Change in Headship Rate')] = pivot_df[(2021, 'Headship')] - pivot_df[(2016, 'Headship')]

        # rename cols to match the doc
        rename_dict = {(2006, 'Pop'): '2006 Population', (2006, 'PHM'): '2006 Number of Primary Household Maintainers',
                       (2006, 'Headship'): '2006 Headship Rate',
                       (2016, 'Pop'): '2016 Population', (2016, 'PHM'): '2016 Number of Primary Household Maintainers',
                       (2016, 'Headship'): '2016 Headship Rate',
                       (2021, 'Pop'): '2021 Population', (2021, 'PHM'): '2021 Number of Primary Household Maintainers',
                       (2021, 'Headship'): '2021 Headship Rate',
                       ('Overall', 'Change in Headship Rate'): 'Change in Headship Rate between 2016 and 2021'}
        pivot_df.columns = pivot_df.columns.to_flat_index()
        pivot_df.rename(columns=rename_dict, inplace=True)
        output_9 = pivot_df.drop(
            columns=['2006 Number of Primary Household Maintainers', '2006 Population', '2006 Headship Rate'])
        #reorder columns
        output_9 = pivot_df[['2016 Population', '2016 Number of Primary Household Maintainers', '2016 Headship Rate',
                             '2021 Population', '2021 Number of Primary Household Maintainers',
                             '2021 Headship Rate',
                             'Change in Headship Rate between 2016 and 2021']]
        #remove 75+ age bin
        filtered_output_9 = output_9.loc[~output_9.index.get_level_values('Age').str.contains('75plus', case=False)]

        # export to csv
        filtered_output_9.to_csv(os.path.join(throughputs_path, "Output9.csv"))
        print("Output 9 Successfully created...")

        #OUTPUT 10 uses similar data to 9
        print("Preparing Output 10...")
        # Potential Households in 2021  = Headship Rate in 2006 multiplied by the Population in 2021.
        pivot_df["2021 Potential Households (2006 Headship Rate x 2021 Population)"] = pivot_df['2006 Headship Rate'] * \
                                                                                       pivot_df['2021 Population']
        # Potential Households in 2021 minus Actual Households in 2021. If the result for any age group is less than zero, set the result to zero.
        pivot_df["2021_Suppressed_Households"] = pivot_df[
                                                     "2021 Potential Households (2006 Headship Rate x 2021 Population)"] - \
                                                 pivot_df["2021 Number of Primary Household Maintainers"]
        pivot_df.loc[pivot_df["2021_Suppressed_Households"] < 0, '2021_Suppressed_Households'] = 0
        pivot_df.rename(columns={'2006 Number of Primary Household Maintainers': '2006 Households',
                                 '2021 Number of Primary Household Maintainers': '2021 Households',
                                 "2021_Suppressed_Households": "2021 Suppressed Households (only if Potential Households > Actual Households)"},
                        inplace=True)
        filtered_ouput_10 = pivot_df.loc[
            ~pivot_df.index.get_level_values('Age').str.contains('|'.join(['75to84', '85plus']))]

        output_10a = filtered_ouput_10[['2006 Population', '2006 Households', '2006 Headship Rate',
                               '2021 Population', '2021 Households', '2021 Headship Rate']]
        output_10b = filtered_ouput_10[['2021 Potential Households (2006 Headship Rate x 2021 Population)',
                               "2021 Households",
                               "2021 Suppressed Households (only if Potential Households > Actual Households)"]]
        #add summary statistic of 2021 suppressed households
        # Calculate the sum of the 'Total' column
        grouped = output_10b.groupby(required_cols)
        # pdb.set_trace()

        # Initialize an empty list to hold the sum rows
        sum_rows = []

        # Loop through each group to calculate the sum and create the sum row
        for group_id, group in grouped:
            # print("group_id", group_id) #, "group", group.shape)
            total_sum = group["2021 Suppressed Households (only if Potential Households > Actual Households)"].sum()

            # Create a new sum row with the calculated sum and the municipality
            sum_row = pd.DataFrame([{
                'Geography': group_id[0],
                'GEO_TYPE_ABBR_EN': group_id[1],
                'ALT_GEO_CODE_EN': group_id[2],
                'PR_CODE_EN': group_id[3],
                'Age': 'Total',
                "2021 Suppressed Households (only if Potential Households > Actual Households)": total_sum
            }])

            # Append the sum row to the list
            sum_rows.append(sum_row)
        
        # pdb.set_trace()

        # Concatenate the sum rows with the original DataFrame
        sum_rows_df = pd.concat(sum_rows, ignore_index=True)
        sum_rows_df.set_index(['Geography', 'GEO_TYPE_ABBR_EN', 'ALT_GEO_CODE_EN', 'PR_CODE_EN', 'Age'], inplace=True)
        output_10b_with_summary = pd.concat([output_10b, sum_rows_df])
        # assert original len + len of unique muni == concatenated df
        assert(sum_rows_df.shape[0] +  output_10b.shape[0] == output_10b_with_summary.shape[0])
        output_10b_with_summary.sort_index(inplace=True)
        # export to csv
        output_10a.to_csv(os.path.join(throughputs_path, "Output10a.csv"))
        output_10b_with_summary.to_csv(os.path.join(throughputs_path, "Output10b.csv"))

        print("Output 10 a and b Successfully created...")

        return output_9, output_10a, output_10b_with_summary

    def prepare_output_11(self):
        #priority groups by core housing need

        #todo waiting on more data- filled with -1 for now
        print("Preparing Output 11...")
        CHN_cols = [col for col in self.master_data.columns if 'ExaminedForCHN' in col] + [col
                                            for col in self.master_data.columns if '2021_CHN' in col]
        # do we want CHN_Renter_2021 or ExaminedForCHNRenter as the divisor?
        CHN_renter_owner_cols = [col for col in self.master_data.columns if 'Renter' in col or 'Owner' in col]
        clean_CHN_cols = list(set(CHN_cols) - set(CHN_renter_owner_cols)) #['2021_CHN_Youth', '2021_CHN_TransgenderNonBinary', '2021_CHN_Veteran', '2021_ExaminedForCHN_MentalHealth', '2021_ExaminedForCHN_Veteran', '2021_ExaminedForCHN_SameGender', '2021_CHN_MentalHealth', '2021_CHN_SameGender', '2021_ExaminedForCHN_Youth', '2021_ExaminedForCHN_TransgenderNonBinary']  # #

        output_11_columns = required_cols + clean_CHN_cols

        assert len(output_11_columns) != len(required_cols), "The required columns are not fetched"
        try:
            output_11 = self.master_data[output_11_columns]
            # output_11 = output_11[output_11['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 11 were not found')
        output_11 = self.master_data[output_11_columns]

        output_11.iloc[:,3:] = output_11.iloc[:,3:].apply(pd.to_numeric,  errors='coerce')
        priority_groups = ['Youth', 'SameGender', 'TransgenderNonBinary', 'MentalHealth', 'Veteran']
        for group in priority_groups:
            subset = output_11[[col for col in output_11.columns if group in col]]
            # Calculate Rate of Core Housing Need (CHN) for each of the five following priority groups as the Number of Households
            # in CHN divided by the Number of Households Examined for CHN  ie. 2021_CHN_Youth / '2021_ExaminedForCHN_Youth'
            output_11[f'{group}_Rate of CHN'] = subset[f'2021_CHN_{group}'].div(subset[f'2021_ExaminedForCHN_{group}'])
            #REMOVE WHEN WE GET THE REAL DATA TODO
            if group == 'SameGender' or group == 'TransgenderNonBinary':
                output_11[subset.columns] = subset.replace(-1, np.nan).replace(1, np.nan)


        # export to csv
        output_11.to_csv(os.path.join(throughputs_path, "Output11.csv"))
        print("Output 11 Successfully created...")

        return output_11

    def prepare_output_12(self):
        # number of co-ops who registered with the co-op housing federation
        print("Preparing Output 12...")
        output_12_columns = required_cols + ['2024_Coops']

        assert len(output_12_columns) != len(required_cols), "The required columns are not fetched"
        try:
            output_12 = self.master_data[output_12_columns]
            #output_12 = output_12[output_12['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 12 were not found')
        output_12 = self.master_data[output_12_columns]
        # export to csv
        output_12.to_csv(os.path.join(throughputs_path, "Output12.csv"))
        print("Output 12 Successfully created...")

        return output_12


    def prepare_output_13(self):
        # affordable units and # lost
        print("Preparing Output 13...")
        output_13_columns = required_cols + ["2016to2021_AffordableUnits_Built", "2016to2021_AffordableUnits_Lost"]

        assert len(output_13_columns) != len(required_cols), "The required columns are not fetched"
        try:
            output_13 = self.master_data[output_13_columns]
            # output_13 = output_13[output_13['Geography'].isin(test_geo)]
        except KeyError:
            print('Some columns from output 13 were not found')
        output_13 = self.master_data[output_13_columns]
        output_13['Net Change in Affordable Units'] = output_13["2016to2021_AffordableUnits_Built"] - output_13['2016to2021_AffordableUnits_Lost']
        # export to csv
        output_13.to_csv(os.path.join(throughputs_path, "Output13.csv"))
        print("Output 13 Successfully created...")

        return output_13

    @staticmethod
    def clean_input_data(input_data):
        input_data.columns = input_data.columns.str.replace(
            '20162', '2016', regex=False).str.replace('Unsibsidized', 'Unsubsidized', regex=False)
        #make new column for 2021 75+ bin
        input_data['2021_75plus_Pop'] = input_data['2021_75to84_Pop'] + input_data['2021_85plus_Pop']
        input_data['2021_75plus_PHM'] = input_data['2021_75to84_PHM'] + input_data['2021_85plus_PHM']
        return input_data
