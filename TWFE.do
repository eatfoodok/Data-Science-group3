* 2014 年人均 GDP 差（迁入省份2014 - 迁出城市2014）
gen dgdp2014 = gdppercapitak_a - gdppercapitak_b

* 气候差：1月最低温差、降水差等（如果你真要用）
gen dtempjan2014 = lowest_tempjan_a - lowest_tempjan_b
gen dprecip2014  = precipitationmm_a - precipitationmm_b

* 也可以只选少数代表变量，不要全家桶
gen mig_period = .
replace mig_period = 1 if migration_year <= 1990
replace mig_period = 2 if inrange(migration_year, 1991, 2000)
replace mig_period = 3 if inrange(migration_year, 2001, 2010)
replace mig_period = 4 if migration_year >= 2011
label define migp 1 "≤1990" 2 "1991–2000" 3 "2001–2010" 4 "≥2011"
label values mig_period migp

reg is_beijing ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      i.hs_residence i.migration_year, r

set maxiter 20
logit is_beijing ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      i.hs_residence i.migration_year, r
  	  
reg is_shanghai ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      i.hs_residence i.migration_year, r

set maxiter 20
logit is_shanghai ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      i.hs_residence i.migration_year, r
 

		  
		  
		  
		  
		  
/////////////////////////////////////////////////////////////////////////	  
set maxiter 15
logit is_beijing ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      gdppercapitak_b population10k_b unemployment_b ///
      medicaltechniciansper10k_b ///
      i.mig_period, r

	  
lasso logit is_beijing ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      gdppercapitak_b population10k_b unemployment_b ///
      medicaltechniciansper10k_b ///
      , selection(plugin, postselection(none)) rseed(12345)

lasso logit is_beijing ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      gdppercapitak_b population10k_b unemployment_b ///
      medicaltechniciansper10k_b ///
      , lambda(0.0030714) selection(none) rseed(12345)
	  
	  
	  
	  lassocoef, display(nonzero)

	  
	  
	  
	  ///Iteration 1: lambda = .0030714   no. of nonzero coef. = 10
	  
	  
	  
	  
	  


lasso logit is_beijing ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      gdppercapitak_b population10k_b unemployment_b ///
      medicaltechniciansper10k_b ///
	  i.mig_period, ///
      lambda(0.0123) rseed(12345)
	  

* 看哪些变量被选进来了（系数非零）
lassocoef, display(nonzero)
	  
firthlogit is_beijing ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      gdppercapitak_b population10k_b unemployment_b ///
      medicaltechniciansper10k_b ///
      i.mig_period	  
	  
set maxiter 15
logit is_shanghai ///
      male age is_han bachelor rural marriage employed ///
      income_total_m_win rent_m_win hours_per_week_filled ///
      length_marriage kids_number birth_here happiness ///
      dgdp2014 dtempjan2014 dprecip2014 migration_distance_km ///
      gdppercapitak_b population10k_b unemployment_b ///
      medicaltechniciansper10k_b ///
      i.mig_period, r



set maxiter 10

logit is_beijing male age is_han bachelor rural marriage employed income_total_m exp_total_m income_total_m_win exp_total_m_win food_exp_m_win income_to_home_win rent_m_win hours_per_week_filled length_marriage kids_number birth_here happiness lowest_tempjan_a average_temp_a highest_tempjuly_a precipitationmm_a gdppercapitak_a unemployment_a education_budget10k_a marriage10k_a population10k_a medicaltechniciansper10k_a road_length_per_10kkm_a manageable_income_per_capita_a gdp_before_move gdp_after_move migration_distance_km i.hs_residence i.migration_year, r

set maxiter 20

logit is_shanghai male age is_han bachelor rural marriage employed income_total_m exp_total_m income_total_m_win exp_total_m_win food_exp_m_win income_to_home_win rent_m_win hours_per_week_filled length_marriage kids_number birth_here happiness lowest_tempjan_a average_temp_a highest_tempjuly_a precipitationmm_a gdppercapitak_a unemployment_a education_budget10k_a marriage10k_a population10k_a medicaltechniciansper10k_a road_length_per_10kkm_a manageable_income_per_capita_a gdp_before_move gdp_after_move migration_distance_km i.hs_residence i.migration_year, r