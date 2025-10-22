PROC IMPORT OUT= WORK.Migration2008B 
            DATAFILE= "C:\Users\Justin Wang\OneDrive - Duke University\Documents\xwechat_files\wxid_w7u07b7g5r6m22_b44b\msg\file\2025-10\panel_data_1021\panel_data_1021\2008Before_1021.csv" 
/*Change filepath for local environment*/
			DBMS=CSV REPLACE; 
RUN;

data migration2008B_mig_1 (keep = Migrate_1 gdp_move_std average_temp_std lowest_temp_std manageable_income_std population_std precipitation_std highest_temp_std road_length_std gdp_per_capita_std);
    set Migration2008B;
	gdp_move_std = gdp_after_move / gdp_before_move;
	average_temp_std = average_temp_a / average_temp_b;
	lowest_temp_std = lowest_temp_Jan__a / lowest_temp_Jan__b;
	manageable_income_std = manageable_income_per_capita_a / manageable_income_per_capita_b;
	population_std = population_10k__a / population_10k__b;
	precipitation_std = precipitation_mm__a / precipitation_mm__b;
	highest_temp_std = highest_temp_July__a / highest_temp_July__b;
	road_length_std = road_length_per_10K__km__a / road_length_per_10K__km__b;
	gdp_per_capita_std = gdp_per_capita_k__a / gdp_per_capita_k__b;
run;

proc logistic data=migration2008B_mig_1  descending outmodel = work.migration2008B_mig_1_model;
    model Migrate_1 = gdp_move_std average_temp_std lowest_temp_std manageable_income_std population_std precipitation_std highest_temp_std road_length_std gdp_per_capita_std / rsquare;
run;

data migration2008B_mig_2 (keep = Migrate_2 gdp_move_std average_temp_std lowest_temp_std manageable_income_std population_std precipitation_std highest_temp_std road_length_std gdp_per_capita_std);
    set Migration2008B;
	gdp_move_std = gdp_after_move / gdp_before_move;
	average_temp_std = average_temp_a / average_temp_b;
	lowest_temp_std = lowest_temp_Jan__a / lowest_temp_Jan__b;
	manageable_income_std = manageable_income_per_capita_a / manageable_income_per_capita_b;
	population_std = population_10k__a / population_10k__b;
	precipitation_std = precipitation_mm__a / precipitation_mm__b;
	highest_temp_std = highest_temp_July__a / highest_temp_July__b;
	road_length_std = road_length_per_10K__km__a / road_length_per_10K__km__b;
	gdp_per_capita_std = gdp_per_capita_k__a / gdp_per_capita_k__b;
run;

proc logistic data=migration2008B_mig_2  descending outmodel = work.migration2008B_mig_2_model;
    model Migrate_2 = gdp_move_std average_temp_std lowest_temp_std manageable_income_std population_std precipitation_std highest_temp_std road_length_std gdp_per_capita_std / rsquare;
run;

data migration2008B_mig_3 (keep = Migrate_3 gdp_move_std average_temp_std lowest_temp_std manageable_income_std population_std precipitation_std highest_temp_std road_length_std gdp_per_capita_std);
    set Migration2008B;
	gdp_move_std = gdp_after_move / gdp_before_move;
	average_temp_std = average_temp_a / average_temp_b;
	lowest_temp_std = lowest_temp_Jan__a / lowest_temp_Jan__b;
	manageable_income_std = manageable_income_per_capita_a / manageable_income_per_capita_b;
	population_std = population_10k__a / population_10k__b;
	precipitation_std = precipitation_mm__a / precipitation_mm__b;
	highest_temp_std = highest_temp_July__a / highest_temp_July__b;
	road_length_std = road_length_per_10K__km__a / road_length_per_10K__km__b;
	gdp_per_capita_std = gdp_per_capita_k__a / gdp_per_capita_k__b;
run;

proc logistic data=migration2008B_mig_3  descending outmodel = work.migration2008B_mig_3_model;
    model Migrate_3 = gdp_move_std average_temp_std lowest_temp_std manageable_income_std population_std precipitation_std highest_temp_std road_length_std gdp_per_capita_std / rsquare;
run;
