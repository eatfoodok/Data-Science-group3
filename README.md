For the data preprocessing, the directory "data cleaning" has the code for how we cleaned the data and the directory "data merge" has the code for how we merged data for many years together.

For our random forest model, the code is in the random_forest.py. We want to identify the key drivers of migration. This will be achieved by conducting a feature importance analysis to rank the top factors influencing migration decisions.

For the logistic regression, we look at how the people are migrating, separating the types into Migration_1 (Inter-provincial), 
Migration_2 (Intra-provincial/Inter-city), Migration_3 (Intra-city/Inter-county). Our determinates are drawn from the ratio of the variable after migration over the variable before migration or (xxx_a / xxx_b). We looked at the variables: personal gdp, average temp, lowest temp, highest temp, managable income, population, precipitation, road length, gdp per capita.

The dataset itself is in the directory "panel_data_1021".
