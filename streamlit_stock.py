# pip install streamlit fbprophet yfinance plotly
import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import matplotlib.pyplot as plt

try: 
	image="https://p7.hiclipart.com/preview/382/800/847/warren-buffett-berkshire-hathaway-investment-investor-finance-warren-buffet.jpg"

	st.set_page_config(
    page_title="FinancioApp",
    page_icon=image,
	layout='wide')


	START = "2015-01-01"
	TODAY = date.today().strftime("%Y-%m-%d")
	st.title('Stock Forecast Application')
	#stocks = ('GOOGL', 'AAPL', 'PLTR', 'NVO', 'KO', 'BAC', 'DUK', ')
	text_isin = st.text_input(label='Put your stock ticker ex: (KO) - CoCa-Cola')
	#selected_stock = st.selectbox('Select dataset for prediction', stocks)
	n_years = st.slider('Years of prediction:', 1, 4)
	period = n_years * 365


	@st.cache_data
	def load_data(ticker):
		data = yf.download(ticker, START, TODAY)
		data.reset_index(inplace=True)
		return data

		
	data_load_state = st.text('Loading data...')
	data = load_data(text_isin)
	data_load_state.text('Loading data... done!')


	st.subheader('Raw data')
	st.write(data.tail())

	# Plot raw data
	def plot_raw_data():
		fig = go.Figure()
		fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open", line_color='white'))
		fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
		fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
		st.plotly_chart(fig, use_container_width=True)
		
	plot_raw_data()

	# Predict forecast with Prophet.
	df_train = data[['Date','Close']]
	df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

	m = Prophet()
	m.fit(df_train)
	future = m.make_future_dataframe(periods=period)
	forecast = m.predict(future)

		# Show and plot forecast
	st.subheader('Forecast data')
	st.write(forecast.tail())
		
	st.write(f'Forecast plot for {n_years} years')
	fig1 = plot_plotly(m, forecast) # change 'red' to any valid CSS color
	st.plotly_chart(fig1, use_container_width=True, height=50)

	fig2 = m.plot_components(forecast)
	with st.expander('Forecast components'):
		st.write(fig2)

	st.subheader('Financials data')



	col1, col2 = st.columns(2)

	 #Tableau pour voir les revenues totaux Brut et Net de l'entreprrise sur 4 années. 
	data_finance = yf.Ticker(text_isin)
	income_stmt = data_finance.income_stmt

		# Récupérer Net Income
	net_income = income_stmt.loc['Net Income']
	brut_income = income_stmt.loc['Total Revenue']

		# Convertir les valeurs en milliards
	net_income_in_billion = net_income / 1e9
	brut_income_in_billion = brut_income /1e9

	bar_width = 0.15
		# Créer un tableau avec matplotlib
	plt.style.use('dark_background')
	fig, ax = plt.subplots(figsize=(10, 5))
	net_bars = ax.bar(net_income.index.year - bar_width/2, net_income_in_billion.values, color='white', width=0.15)  # Ajuster la largeur des barres
	gross_bars = ax.bar(brut_income.index.year + bar_width/2, brut_income_in_billion.values, color='red', width=0.15)
	ax.set_title('Net and Gross Income Over Years')
	ax.set_xlabel('Year')
	ax.set_ylabel('Net Income (in billions)')
	ax.set_facecolor('black')
	for bar in net_bars:
    		ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(bar.get_height(), 2), ha='center', va='bottom', color='white')

	for bar in gross_bars:
		ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(bar.get_height(), 2), ha='center', va='bottom', color='white')
	with col2:
		with st.expander('Balance sheet '):
			data_finance = yf.Ticker(text_isin)
			st.write(data_finance.balance_sheet)

		with st.expander('Cashflow'):
			data_finance = yf.Ticker(text_isin)
			st.write(data_finance.cashflow)

		st.subheader('Net and Gross Income Statement')
		st.pyplot(fig, transparent=True)

	#Talbleau pour afficher la dette totale de l'entprise
	# Utiliser le style 'dark_background'
	plt.style.use('dark_background')

	data_debt = yf.Ticker(text_isin)
	inco = data_debt.balance_sheet
	total_debt = inco.loc['Total Debt']
	total_debt_in_billion = total_debt / 1e9

	fig_2, ax_2 = plt.subplots(figsize=(10, 5))
	debt_bar = ax_2.bar(total_debt_in_billion.index.year, total_debt_in_billion.values,  color='orange', width=0.15)
	ax_2.set_title('Total Debt Over Years')
	ax_2.set_xlabel('Year')
	ax_2.set_ylabel('Total Debt(in billions)')
	ax_2.set_facecolor('black')

	for bar in debt_bar:
		ax_2.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(bar.get_height(), 2), ha='center', va='bottom', color='white')

	with col1:
		with st.expander('Dividends'):
			data_finance = yf.Ticker(text_isin)
			st.write(data_finance.dividends)
		with st.expander('Income statement'):
			data_finance = yf.Ticker(text_isin)
			st.write(data_finance.income_stmt)
		st.subheader('Total Debt Graphic')
		st.pyplot(fig_2, transparent=True)
	pass
except Exception as e:
	st.error(f'Please put the ticker of your stock !')
	st.write(e)
