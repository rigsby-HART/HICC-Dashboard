#  Housing, Infrastructure and Communities Canada (HICC) Dashboard

## Introduction

This HNA Template, developed in collaboration with Housing, Infrastructure and Communities Canada (HICC), is meant to support communities across Canada to satisfy the requirements of federal funding programs, like the Housing Accelerator Fund (HAF), the Canada Community Building Fund (CCBF), and the Permanent Transit Fund.

The tool is powered by census data custom built by Statistics Canada in collaboration with HART researchers.

The HICC tool and dashboard includes data for Canada; the Provinces and Territories; Census divisions (CD), a general term for regional planning areas; and Census subdivisions (CSD), a general term for municipalities.  

The dashboard was created in collaboration with [Licker Geospatial](https://www.lgeo.co), who can be reached for further questions regarding dashboard functionality and design.

Link: https://hart.ubc.ca/federal-hna-template

## Features

The HICC dashboard provides the following features:

- Map picker for selecting regions
- Plots and tables for Average rents and Vacancy Rates
- Plots and tables for Household Projections
- Plots and tables by Housing Structural Types and Tenures
- Plots and tables for Core Housing Needs and Headship Rates
- Plots and tables by Household Suppression by Age
- Plots and tables for Co-operative Housing Units and Number of Affordable Units
- Plots and tables for Priority Groups
- Tables for Households within 200m and 800m of rail/light-rail transit station
- Download functions for all plots and tables

## Getting Started In Your Local Environment

### System requirements

Please make sure you have the following installed(Requirements.txt is provided in the repository):

- Python 3
- Pandas
- Numpy
- Plotly
- Dash
- SQL Alchemy

### Start Local Server and Run the Dashboard

1. Git Clone or Download the code package from the repository
2. Type `python app.py` on your Shell inside of the folder of the code package.
3. Type `000.000.0.00:8050/page1` and `000.000.0.00:8050/page2` on your browser. 000.000.0.00 is your IP address. Each page indicates:
    - page1: Map Picker
    - page2: HICC HNA page
    - note: Try http://localhost:8050/page1 if network designation is not recognized
    
## Technical Support
Please contact [LGeo](https://www.lgeo.co)