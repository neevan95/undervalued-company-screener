import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("Undervalued Companies Screener")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload cleaned Capital IQ Excel file", type=["xls", "xlsx"])
if uploaded_file is None:
    st.warning("Please upload a cleaned Excel file to begin.")
    st.stop()



#load the clenaed file and rename columns:
file_name = uploaded_file

data = pd.read_excel(file_name,sheet_name='Screening')
#print(data.columns)
data = data.rename(columns= {'Company Name':'company', 
                             'Exchange:Ticker':'ticker',
       'Market Capitalization [My Setting] [Latest] ($USDmm, Historical rate)':'market_cap_mn',
       'TEV/Forward EBITDA [My Setting] - Capital IQ [NTM] (x)':'tev_ebitda_ntm',
       'Forward P/E - Capital IQ [NTM] (x)':'forward_pe_ntm',
       'Forward P/BV - Capital IQ [NTM]':'forward_pbv_ntm', 
       'Net Debt/EBITDA [LTM]':'debt_ebitda_ltm',
       'EBITDA / Interest Exp. [LTM]':'ebitda_interest_ltm', 
       'Total Revenues, 5 Yr CAGR % [LTM] (%)':'rev_cagr',
       'Gross Profit, 5 Yr CAGR % [LTM] (%)':'gross_profit_cagr', 
       'EBITDA, 5 Yr CAGR % [LTM] (%)':'ebitda_cagr',
       'Diluted EPS before Extra, 5 Yr CAGR % [LTM] (%)':'eps_cagr',
       'Capital Expenditures, 5 Yr CAGR % [LTM] (%)':'capex_cagr',
       'Total Debt/Equity % [Latest Quarter]':'debt_equity',
       'Capex as % of Revenues [Latest Annual] (%)':'capex_pct',
       'Avg. Cash Conversion Cycle [Latest Quarter] (Days)':'cash_conversion_cycle',
       'Total Asset Turnover [Latest Quarter]':'asset_turnover_qtr',
       'Inventory Turnover [Latest Quarter]':'inventory_turnover_qtr', 
       'Return on Assets % [LTM]':'roa_ltm',
       'Return on Capital % [LTM]':'roc_ltm', 
       'Return on Equity % [LTM]':'roe_ltm',
       '5 Year Beta [Latest]':'5yr_beta', 
       '5 Year Beta R-Squared [Latest]':'5yr_beta_r_squared',
       'Primary Industry':'industry', 
       'Primary Sector':'sector',
       'Exchange Country/Region [Primary Listing]':'country', 
       'Updated Ke':'Ke',
       'Intangibles%':'intangibles_pct',
       'EPS (GAAP) - Std Dev - Capital IQ [FY] ($USD, Historical rate)':'eps_std_dev',
       'Net Income Margin % [LTM]':'net_margin_ltm', 
       'Cash and ST Inv %':'cash_pct',
       'As-Reported Total Revenue [LTM] ($USD, Historical rate)':'revenue_mn',
       'Asset Turnover [LTM]':'asset_turnover_ltm',
       'Total Cash & ST Investments / Total Assets - Copy':'cash_pct_copy',
       'Institutions - % Owned [Latest] (%)':'institutional_ownership_pct',
       'Individuals/Insiders - % Owned [Latest] (%)':'insider_ownership_pct',
       'Total Cash & ST Investments [Latest Annual] ($USDmm, Historical rate)':'cash_mn',
       'Cash from Ops. [LTM] ($USDmm, Historical rate)':'cash_from_ops_ltm',
       'Cash from Investing [LTM] ($USDmm, Historical rate)':'cash_from_investing_ltm',
       'Cash from Financing [LTM] ($USDmm, Historical rate)':'cash_from_financing_ltm'})

#bins = [-9999999999999999999,10000,999999999999999999999999999]
#labels = ['less than 10B','More than 10B']
#data['market_cap_label'] = pd.cut(data['market_cap_mn'],bins=bins,labels=labels,right=True)
# --- USER INPUTS ---
st.sidebar.header("Filtering Parameters")
min_market_cap = st.sidebar.number_input("Minimum Market Cap ($mn)", value=10000)
min_companies_needed = st.sidebar.number_input("Minimum Companies in Industry", value=5)
min_weighted_score = st.sidebar.slider("Minimum Total Weighted Score", min_value=0, max_value=150, value=75)
min_score_in_each_category = st.sidebar.slider("Minimum Score in Each Category (%)", min_value=0, max_value=100, value=10)

st.sidebar.header("Industry/Sector Filters")
unique_sectors = sorted(data['sector'].dropna().unique())
unique_industries = sorted(data['industry'].dropna().unique())
sectors_to_avoid = st.sidebar.multiselect("Sectors to Avoid", unique_sectors)
industries_to_avoid = st.sidebar.multiselect("Industries to Avoid", unique_industries)


st.sidebar.header("Metric Weights")
tev_ebitda_ntm_weight = st.sidebar.slider("TEV/EBITDA Weight", 0, 20, 10)
forward_pe_ntm_weight = st.sidebar.slider("Forward P/E Weight", 0, 20, 10)
forward_pbv_ntm_weight = st.sidebar.slider("Forward P/BV Weight", 0, 20, 0)
debt_ebitda_ltm_weight = st.sidebar.slider("Net Debt/EBITDA Weight", 0, 20, 8)
ebitda_interest_ltm_weight = st.sidebar.slider("EBITDA/Interest Weight", 0, 20, 8)
debt_equity_weight = st.sidebar.slider("Debt/Equity Weight", 0, 20, 8)
eps_std_dev_weight = st.sidebar.slider("EPS Std Dev Weight", 0, 20, 5)
capex_pct_weight = st.sidebar.slider("Capex % Weight", 0, 20, 5)
rev_cagr_weight = st.sidebar.slider("Revenue CAGR Weight", 0, 20, 10)
eps_cagr_weight = st.sidebar.slider("EPS CAGR Weight", 0, 20, 8)
net_margin_ltm_weight = st.sidebar.slider("Net Margin Weight", 0, 20, 7)
roc_ltm_weight = st.sidebar.slider("ROC Weight", 0, 20, 0)
roa_ltm_weight = st.sidebar.slider("ROA Weight", 0, 20, 7)
roe_ltm_weight = st.sidebar.slider("ROE Weight", 0, 20, 8)
asset_turnover_ltm_weight = st.sidebar.slider("Asset Turnover Weight", 0, 20, 5)
cash_from_ops_ltm_weight = st.sidebar.slider("Cash from Ops Weight", 0, 20, 5)
cash_conversion_cycle_weight = st.sidebar.slider("Cash Conversion Cycle Weight", 0, 20, 2)



#checking for companies that have more cash balances than their market cap: (usually financial companies but anything other than those is an anomaly to be looked into)
data['cash_market_cap_difference'] = data['cash_mn'] - data['market_cap_mn']
data['cash_vs_market_cap'] = data['cash_mn'] > data['market_cap_mn']
companies_with_more_cash_than_mktcap = data[(data['cash_vs_market_cap']==True)&(data['sector']!='Financials')][['company','ticker','industry','sector','market_cap_mn','cash_mn','cash_market_cap_difference']].sort_values(by=['cash_market_cap_difference'],ascending=False)

#filtering out companies with market cap < 10B
# min_market_cap = 10000
data = data[data['market_cap_mn'] > min_market_cap]

#creating industry level median for various metrics
data['median_tev_ebitda_ntm'] = data.groupby(['sector','industry'])['tev_ebitda_ntm'].transform('median')
data['median_forward_pe_ntm'] = data.groupby(['sector','industry'])['forward_pe_ntm'].transform('median')
data['median_forward_pbv_ntm'] = data.groupby(['sector','industry'])['forward_pbv_ntm'].transform('median')
data['median_debt_ebitda_ltm'] = data.groupby(['sector','industry'])['debt_ebitda_ltm'].transform('median')
data['median_ebitda_interest_ltm'] = data.groupby(['sector','industry'])['ebitda_interest_ltm'].transform('median')
data['median_debt_equity'] = data.groupby(['sector','industry'])['debt_equity'].transform('median')
data['median_eps_std_dev'] = data.groupby(['sector','industry'])['eps_std_dev'].transform('median')
data['median_capex_pct'] = data.groupby(['sector','industry'])['capex_pct'].transform('median')
data['median_rev_cagr'] = data.groupby(['sector','industry'])['rev_cagr'].transform('median')
data['median_eps_cagr'] = data.groupby(['sector','industry'])['eps_cagr'].transform('median')
data['median_net_margin_ltm'] = data.groupby(['sector','industry'])['net_margin_ltm'].transform('median')
data['median_roc_ltm'] = data.groupby(['sector','industry'])['roc_ltm'].transform('median')
data['median_roa_ltm'] = data.groupby(['sector','industry'])['roa_ltm'].transform('median')
data['median_roe_ltm'] = data.groupby(['sector','industry'])['roe_ltm'].transform('median')
data['median_asset_turnover_ltm'] = data.groupby(['sector','industry'])['asset_turnover_ltm'].transform('median')
data['median_cash_from_ops_ltm'] = data.groupby(['sector','industry'])['cash_from_ops_ltm'].transform('median')
data['median_cash_conversion_cycle'] = data.groupby(['sector','industry'])['cash_conversion_cycle'].transform('median')


#comparing if a company metric is less/more than its industry median
data['tev_ebitda_ntm_median_check'] = np.where(data['tev_ebitda_ntm'] < data['median_tev_ebitda_ntm'],1,0)
data['forward_pe_ntm_median_check'] = np.where(data['forward_pe_ntm'] < data['median_forward_pe_ntm'],1,0)
data['forward_pbv_ntm_median_check'] = np.where(data['forward_pbv_ntm'] < data['median_forward_pbv_ntm'],1,0)
data['debt_ebitda_ltm_median_check'] = np.where(data['debt_ebitda_ltm'] < data['median_debt_ebitda_ltm'],1,0)
data['ebitda_interest_ltm_median_check'] = np.where(data['ebitda_interest_ltm'] > data['median_ebitda_interest_ltm'],1,0)
data['debt_equity_median_check'] = np.where(data['debt_equity'] < data['median_debt_equity'],1,0)
data['eps_std_dev_median_check'] = np.where(data['eps_std_dev'] < data['median_eps_std_dev'],1,0)
data['capex_pct_median_check'] = np.where(data['capex_pct'] < data['median_capex_pct'],1,0)
data['rev_cagr_median_check'] = np.where(data['rev_cagr'] > data['median_rev_cagr'],1,0)
data['eps_cagr_median_check'] = np.where(data['eps_cagr'] > data['median_eps_cagr'],1,0)
data['net_margin_ltm_median_check'] = np.where(data['net_margin_ltm'] > data['median_net_margin_ltm'],1,0)
data['roc_ltm_median_check'] = np.where(data['roc_ltm'] > data['median_roc_ltm'],1,0)
data['roa_ltm_median_check'] = np.where(data['roa_ltm'] > data['median_roa_ltm'],1,0)
data['roe_ltm_median_check'] = np.where(data['roe_ltm'] > data['median_roe_ltm'],1,0)
data['asset_turnover_ltm_median_check'] = np.where(data['asset_turnover_ltm'] > data['median_asset_turnover_ltm'],1,0)
data['cash_from_ops_ltm_median_check'] = np.where(data['cash_from_ops_ltm'] > data['median_cash_from_ops_ltm'],1,0)
data['cash_conversion_cycle_median_check'] = np.where(data['cash_conversion_cycle'] > data['median_cash_conversion_cycle'],1,0)

#setting weights for metrics
# tev_ebitda_ntm_weight = 10
# forward_pe_ntm_weight = 10
# forward_pbv_ntm_weight = 0
# debt_ebitda_ltm_weight = 8
# ebitda_interest_ltm_weight = 8
# debt_equity_weight = 8
# eps_std_dev_weight = 5
# capex_pct_weight = 5
# rev_cagr_weight = 10
# eps_cagr_weight = 8
# net_margin_ltm_weight = 7
# roc_ltm_weight = 0
# roa_ltm_weight = 7
# roe_ltm_weight = 8
# asset_turnover_ltm_weight = 5
# cash_from_ops_ltm_weight = 5
# cash_conversion_cycle_weight = 2

#calculating weighted score for each metric
data['tev_ebitda_ntm_score'] = data['tev_ebitda_ntm_median_check'] * tev_ebitda_ntm_weight
data['forward_pe_ntm_score'] = data['forward_pe_ntm_median_check'] * forward_pe_ntm_weight
data['forward_pbv_ntm_score'] = data['forward_pbv_ntm_median_check'] * forward_pbv_ntm_weight
data['debt_ebitda_ltm_score'] = data['debt_ebitda_ltm_median_check'] * debt_ebitda_ltm_weight
data['ebitda_interest_ltm_score'] = data['ebitda_interest_ltm_median_check'] * ebitda_interest_ltm_weight
data['debt_equity_score'] = data['debt_equity_median_check'] * debt_equity_weight
data['eps_std_dev_score'] = data['eps_std_dev_median_check'] * eps_std_dev_weight
data['capex_pct_score'] = data['capex_pct_median_check'] * capex_pct_weight
data['rev_cagr_score'] = data['rev_cagr_median_check'] * rev_cagr_weight
data['eps_cagr_score'] = data['eps_cagr_median_check'] * eps_cagr_weight
data['net_margin_ltm_score'] = data['net_margin_ltm_median_check'] * net_margin_ltm_weight
data['roc_ltm_score'] = data['roc_ltm_median_check'] * roc_ltm_weight
data['roa_ltm_score'] = data['roa_ltm_median_check'] * roa_ltm_weight
data['roe_ltm_score'] = data['roe_ltm_median_check'] * roe_ltm_weight
data['asset_turnover_ltm_score'] = data['asset_turnover_ltm_median_check'] * asset_turnover_ltm_weight
data['cash_from_ops_ltm_score'] = data['cash_from_ops_ltm_median_check'] * cash_from_ops_ltm_weight
data['cash_conversion_cycle_score'] = data['cash_conversion_cycle_median_check'] * cash_conversion_cycle_weight

#specifying columns for calculating scores
score_columns = ['tev_ebitda_ntm_median_check', 'forward_pe_ntm_median_check', 'forward_pbv_ntm_median_check', 'debt_ebitda_ltm_median_check', 'ebitda_interest_ltm_median_check', 'debt_equity_median_check', 'eps_std_dev_median_check', 'capex_pct_median_check', 'rev_cagr_median_check', 'eps_cagr_median_check', 'net_margin_ltm_median_check', 'roc_ltm_median_check', 'roa_ltm_median_check', 'roe_ltm_median_check', 'asset_turnover_ltm_median_check', 'cash_from_ops_ltm_median_check', 'cash_conversion_cycle_median_check']
weighted_score_columns = ['tev_ebitda_ntm_score', 'forward_pe_ntm_score', 'forward_pbv_ntm_score', 'debt_ebitda_ltm_score', 'ebitda_interest_ltm_score', 'debt_equity_score', 'eps_std_dev_score', 'capex_pct_score', 'rev_cagr_score', 'eps_cagr_score', 'net_margin_ltm_score', 'roc_ltm_score', 'roa_ltm_score', 'roe_ltm_score', 'asset_turnover_ltm_score', 'cash_from_ops_ltm_score', 'cash_conversion_cycle_score']

price_weighted_score_columns = ['tev_ebitda_ntm_score', 'forward_pe_ntm_score', 'forward_pbv_ntm_score']
risk_weighted_score_columns = ['debt_ebitda_ltm_score', 'ebitda_interest_ltm_score', 'debt_equity_score', 'eps_std_dev_score', 'capex_pct_score']
growth_weighted_score_columns = ['rev_cagr_score', 'eps_cagr_score']
quality_of_growth_weighted_score_columns = ['net_margin_ltm_score', 'roc_ltm_score', 'roa_ltm_score', 'roe_ltm_score', 'asset_turnover_ltm_score', 'cash_from_ops_ltm_score', 'cash_conversion_cycle_score']

#calculating scores
data['total_unweighted_score'] = data[score_columns].sum(axis=1)
data['total_weighted_score'] = data[weighted_score_columns].sum(axis=1)
data['total_weighted_score_from_price'] = data[price_weighted_score_columns].sum(axis=1)
data['total_weighted_score_from_risk'] = data[risk_weighted_score_columns].sum(axis=1)
data['total_weighted_score_from_growth'] = data[growth_weighted_score_columns].sum(axis=1)
data['total_weighted_score_from_quality_of_growth'] = data[quality_of_growth_weighted_score_columns].sum(axis=1)

#calculating weighted score mix from various factors
data['price_score_mix'] = round(data['total_weighted_score_from_price']*100/data['total_weighted_score'],1)
data['risk_score_mix'] = round(data['total_weighted_score_from_risk']*100/data['total_weighted_score'],1)
data['growth_score_mix'] = round(data['total_weighted_score_from_growth']*100/data['total_weighted_score'],1)
data['quality_of_growth_score_mix'] = round(data['total_weighted_score_from_quality_of_growth']*100/data['total_weighted_score'],1)

#no. of companies in each industry for this analysis
data['n_companies'] = data.groupby(['sector','industry'])['company'].transform('nunique').astype('int')

#cleaning up all unwanted columns for output data sheet
final_data_sheet_columns = ['sector','industry','n_companies','company','ticker','market_cap_mn','revenue_mn', 'total_unweighted_score', 
                            'total_weighted_score','price_score_mix', 'risk_score_mix', 'growth_score_mix', 'quality_of_growth_score_mix',
                            'tev_ebitda_ntm', 'forward_pe_ntm', 'forward_pbv_ntm', 'debt_ebitda_ltm', 'ebitda_interest_ltm', 'debt_equity','eps_std_dev','capex_pct',
                            'rev_cagr', 'eps_cagr', 'net_margin_ltm','roc_ltm',  'roa_ltm', 'roe_ltm','asset_turnover_ltm', 'cash_from_ops_ltm','cash_conversion_cycle']

final_data_sheet = data[final_data_sheet_columns].sort_values(by=['sector','industry'])

#creating a summary data sheet
summary_data_sheet_columns = ['sector','industry','n_companies','company','ticker','market_cap_mn','revenue_mn', 'total_unweighted_score', 
                            'total_weighted_score','price_score_mix', 'risk_score_mix', 'growth_score_mix', 'quality_of_growth_score_mix']

summary_data_sheet = data[summary_data_sheet_columns].sort_values(by=['sector','industry'])

#creating a summary list of shortlisted companies
# min_companies_needed = int(5)
# min_weighted_score = int(75)
# min_score_in_each_category = int(10)
# sectors_to_avoid = []
# industries_to_avoid = []

shortlist = summary_data_sheet[(summary_data_sheet['n_companies']>= min_companies_needed) & (summary_data_sheet['total_weighted_score']>min_weighted_score) & 
            (summary_data_sheet['price_score_mix']>min_score_in_each_category) & (summary_data_sheet['risk_score_mix']>min_score_in_each_category) & 
            (summary_data_sheet['growth_score_mix']>min_score_in_each_category)
            & (summary_data_sheet['quality_of_growth_score_mix']>min_score_in_each_category)]

shortlist = shortlist[~shortlist.sector.isin(sectors_to_avoid)]
shortlist = shortlist[~shortlist.industry.isin(industries_to_avoid)].sort_values(by =['total_weighted_score'],ascending=False).reset_index(drop=True)

print(shortlist)


st.subheader("Shortlisted Companies")
st.dataframe(shortlist)

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(shortlist)
st.download_button(
    "Download Shortlist as CSV",
    data=csv,
    file_name='undervalued_company_shortlist.csv',
    mime='text/csv'
)

st.subheader("Detailed Data Sheet")
st.dataframe(final_data_sheet)

st.subheader("Summary Data Sheet")
st.dataframe(summary_data_sheet)

st.subheader("Companies with More Cash than Market Cap")
st.dataframe(companies_with_more_cash_than_mktcap)
