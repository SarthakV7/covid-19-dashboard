from concurrent.futures import ThreadPoolExecutor
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from data_functions import *
import numpy as np
import time
import wget
import os

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

app.title = 'COVID-19 Global Dashboard'

server=app.server

def define_variables(df_confirmed, df_recovered, df_deaths):
    global df_rec
    global df_con
    global df_dea
    global df_act
    global confirmed
    global recovered
    global active
    global deaths
    global total_confirmed
    global total_recovered
    global total_deaths
    global total_active
    global change_confirmed
    global change_recovered
    global change_deaths
    global change_active
    global active_rate
    global recovery_rate
    global mortality_rate
    global cases_per_million
    df_confirmed.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
    df_confirmed.rename(columns={'Country/Region': 'Country'}, inplace=True)
    df_recovered.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
    df_recovered.rename(columns={'Country/Region': 'Country'}, inplace=True)
    df_deaths.drop(['Province/State', 'Lat', 'Long'], axis=1, inplace=True)
    df_deaths.rename(columns={'Country/Region': 'Country'}, inplace=True)
    df_rec = merge_countries(df_recovered).sort_values(by='Country')#.drop(['12/13/20'], axis=1)
    df_con = merge_countries(df_confirmed).sort_values(by='Country')#.drop(['12/13/20'], axis=1)
    df_dea = merge_countries(df_deaths).sort_values(by='Country')#.drop(['12/13/20'], axis=1)
    df_act = df_con.copy()
    df_act[df_act.columns[1:]] = df_con.values[:, 1:] - (df_rec.values[:, 1:] + df_dea.values[:, 1:])
    confirmed = date_wise(df_con.sum(axis=0))
    recovered = date_wise(df_rec.sum(axis=0))
    active = date_wise(df_act.sum(axis=0))
    deaths = date_wise(df_dea.sum(axis=0))
    total_confirmed = confirmed.Value.iloc[-1] 
    total_recovered = recovered.Value.iloc[-1]
    total_deaths = deaths.Value.iloc[-1]
    total_active = total_confirmed - total_recovered + total_deaths
    change_confirmed = confirmed.Value.iloc[-1] - confirmed.Value.iloc[-2]
    change_recovered = recovered.Value.iloc[-1] - recovered.Value.iloc[-2]
    change_deaths = deaths.Value.iloc[-1] - deaths.Value.iloc[-2]
    change_active = change_confirmed - change_recovered + change_deaths
    if change_active >= 0:
        change_active = f'+{change_active:,}'
    else:
        change_active = f'-{-change_active:,}'
    if change_confirmed >= 0:
        change_confirmed = f'+{change_confirmed:,}'
    else:
        change_confirmed = f'-{-change_confirmed:,}'
    if change_recovered >= 0:
        change_recovered = f'+{change_recovered:,}'
    else:
        change_recovered = f'-{-change_recovered:,}'
    if change_deaths >= 0:
        change_deaths = f'+{change_deaths:,}'
    else:
        change_deaths = f'-{-change_deaths:,}'
    active_rate = 100 * total_active / total_confirmed
    recovery_rate = 100 * total_recovered / (total_confirmed)
    mortality_rate = 100 * total_deaths / (total_confirmed)
    cases_per_million = 1e6 * total_confirmed / 7796127694

# getting data periodically
def update_data(period=4):
  while True:
    os.remove('data/time_series_covid19_confirmed_global.csv')
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv','./data')
    global df_confirmed
    df_confirmed = pd.read_csv('data/time_series_covid19_confirmed_global.csv')

    os.remove('data/time_series_covid19_recovered_global.csv')
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv','./data')
    global df_recovered
    df_recovered = pd.read_csv('data/time_series_covid19_recovered_global.csv')

    os.remove('data/time_series_covid19_deaths_global.csv')
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv','./data')
    global df_deaths
    df_deaths = pd.read_csv('data/time_series_covid19_deaths_global.csv')
    time.sleep(period*60*60)
    # print('updating data...')
    define_variables(df_confirmed, df_recovered, df_deaths)


if 'time_series_covid19_confirmed_global.csv' not in os.listdir('./data'):
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', './data')
if 'time_series_covid19_recovered_global.csv' not in os.listdir('./data'):
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv', './data')
if 'time_series_covid19_deaths_global.csv' not in os.listdir('./data'):
    wget.download('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv', './data')

# importing data
df_confirmed = pd.read_csv('data/time_series_covid19_confirmed_global.csv')
df_recovered = pd.read_csv('data/time_series_covid19_recovered_global.csv')
df_deaths = pd.read_csv('data/time_series_covid19_deaths_global.csv')
define_variables(df_confirmed, df_recovered, df_deaths)


# cards
card_1 = dbc.Card([
        # dbc.CardImg(src="assets/images/confirm.png", top=True),
        dbc.CardBody([
                html.H6("Confirmed", className='card_title'),
                html.H5(f"{change_confirmed}", className='card_changed'),
                html.H5(f"{total_confirmed:,}", className='card_value')
                ], className='card_1_body')], className='card_1')

card_2 = dbc.Card([
        # dbc.CardImg(src="assets/images/recovered.png", top=True),
        dbc.CardBody([
                html.H6("Recovered", className='card_title'),
                html.H5(f"{change_recovered}", className='card_changed'),
                html.H5(f"{total_recovered:,}", className='card_value')
                ], className='card_2_body')], className='card_2')

card_3 = dbc.Card([
        # dbc.CardImg(src="assets/images/deceased.png", top=True),
        dbc.CardBody([
                html.H6("Deceased", className='card_title'),
                html.H5(f"{change_deaths}", className='card_changed'),
                html.H5(f"{total_deaths:,}", className='card_value')
                ], className='card_3_body')], className='card_3')

card_4 = dbc.Card([
        # dbc.CardImg(src="assets/images/active.png", top=True),
        dbc.CardBody([
                html.H6("Active", className='card_title'),
                html.H5(f"{change_active}", className='card_changed'),
                html.H5(f"{total_active:,}", className='card_value')
                ], className='card_4_body')], className='card_4')

##########################################

files = {'covid': 'data/covid_19_data.csv',
         'covid_line_list': 'data/COVID19_line_list_data.csv',
         'COVID19_open_line_list': 'data/COVID19_open_line_list.csv',
         'global_confirmed': 'data/time_series_covid_19_confirmed.csv',
         'global_deaths': 'data/time_series_covid_19_deaths.csv',
         'global_recovered': 'data/time_series_covid_19_recovered.csv'}

n = -1
df_top = for_map(df_con, df_rec, df_dea, df_act, flag='top')
countries = df_top['Country'].values
countries = np.append(countries, 'Global')
df_top = df_top.sort_values(by='Confirmed', ascending=False).iloc[:n]
idx = df_top[df_top['Country']=='US'].index[0]
temp = df_top.loc[idx].values
temp[2], temp[4] = '-', '-'
df_top.loc[idx] = temp

################ world-map #################
df_map = for_map(df_con, df_rec, df_dea, df_act)
fig_map = create_map(df_map)
fig_map = html.Div(dcc.Graph(figure=fig_map, className='fig_map'), style={'padding':'1.25rem'})

################ sunburst plot #############
df_continent = pd.read_csv('https://raw.githubusercontent.com/dbouquin/IS_608/master/NanosatDB_munging/Countries-Continents.csv')
df_continent.replace('Burkina', 'Burkina Faso', inplace=True)
df_continent.replace('Burma (Myanmar)', 'Burma', inplace=True)
df_continent.replace('Congo', 'Congo (Brazzaville)', inplace=True)
df_continent.replace('Congo, Democratic Republic of', 'Congo (Kinshasa)', inplace=True)
df_continent.replace('Russian Federation', 'Russia', inplace=True)

new = pd.DataFrame([['Africa', 'Congo (Brazzaville)'],
                    ['Africa', 'Congo (Kinshasa)'],
                    ['Europe', 'Czechia'],
                    ['Asia', 'Taiwan*'],
                    ['Africa', 'Western Sahara']], columns=df_continent.columns)
df_continent = df_continent.append(new)
df_sunburst = for_map(df_con, df_rec, df_dea, df_act, flag='top')
df_sunburst = pd.merge(df_continent, df_sunburst, on='Country')
df_sunburst.replace(0, np.nan, inplace=True)
df_sunburst.dropna(inplace=True)
fig_sunburst_confirmed = create_sunburst(df_sunburst, 'Confirmed')
fig_sunburst_recovered = create_sunburst(df_sunburst, 'Recovered')
fig_sunburst_deaths = create_sunburst(df_sunburst, 'Deaths')
fig_sunburst_active = create_sunburst(df_sunburst, 'Active')

fig_sunburst_confirmed = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(figure=fig_sunburst_confirmed))),
                                             className='figure_confirmed'), className='figure_rows'))

fig_sunburst_recovered = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(figure=fig_sunburst_recovered))),
                                             className='figure_recovered'), className='figure_rows'))

fig_sunburst_deaths = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(figure=fig_sunburst_deaths))),
                                            className='figure_deceased'), className='figure_rows'))

fig_sunburst_active = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(figure=fig_sunburst_active))),
                                          className='figure_active'), className='figure_rows'))

############################################
# table card
table_card = dbc.Card([
                dbc.Table.from_dataframe(df_top, dark=True, bordered=True,
                                 hover=True, responsive=True, size='sm',
                                 className='container', style={'margin': 'auto'})], className='table_card')

############################################
#card container row
card_container_row = dbc.Row(dbc.Col(dbc.Row([
                        dbc.Col(html.Div(card_1), className='cards'),
                        dbc.Col(html.Div(card_2), className='cards'),
                        dbc.Col(html.Div(card_3), className='cards'),
                        dbc.Col(html.Div(card_4), className='cards'),
                        # dbc.Col(html.Div(option_card), className='cards')
                        ], className='cards_inside_row'), className='cards_col'),
    className='cards_row')

############################################
# tab items
dropdown_country = dbc.Card(dbc.CardBody(dbc.Row([
                                        dbc.Col(dbc.Input(placeholder="Search country...", type="text",
                                                      list='list-data', id='_cntry_name', value='India')),
                                        html.Datalist(id='list-data',
                                                      children=[html.Option(value=c) for c in countries])
                                        ]), className='tab_global'), className='tab_global')

dropdown_global = dbc.Card(dbc.CardBody(dbc.Row(dbc.Col(
                            dbc.InputGroup([
                                dbc.InputGroupAddon("Show top", addon_type="prepend", className='addon_text'),

                                dbc.Input(placeholder="10", type="number", min=1, max=180,
                                          step=1, id='_no_of_cntry', value=10),

                                dbc.InputGroupAddon("countries with", addon_type="prepend", className='addon_text'),

                                dbc.Select(id="_hgh_or_lw",
                                    options=[{"label": "lowest", "value": 'lowest'},
                                             {"label": "highest", "value": 'highest'}], value='highest'),

                                dbc.Select(id="_feature",
                                     options=[{"label": "confirmed", "value": 'Confirmed'},
                                              {"label": "recovered", "value": 'Recovered'},
                                              {"label": "deceased", "value": 'Deaths'},
                                              {"label": "active", "value": 'Active'}], value='Confirmed'),

                                dbc.InputGroupAddon("cases!", addon_type="prepend", className='addon_text'),
                                 ], className='input_group'))), className='tab_global_card'), className='tab_global_card')

#############################################
# tabs
tabs = dbc.Row(dbc.Col([
    dbc.Card(dbc.Tabs(
        [
        dbc.Tab(dropdown_global, label="Global data", className='tab_global', tab_id="tab-1"),
        dbc.Tab(dropdown_country, label="Country wise data", className='tab_country', tab_id="tab-2"),
        ], id="_tabs", active_tab="tab-1"), className='tabs_card'),
    dbc.Button("Get results", color='#AAA', size="sm", className="button", block=True, id='button'),
                        ], className='tabs_column'),
    className='figure_rows')

#############################################
# global data

fig_bar = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_bar'))),
                                  className='figure_global'), className='figure_rows'))

# cdf
# fig_global_confirmed_cdf = confirm_cdf(df_con, 0)
fig_confirmed_cdf = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_confirmed_cdf'))),
                                            className='figure_confirmed'), className='figure_rows'))

# fig_global_recovered_cdf = confirm_cdf(df_rec, 1)
fig_recovered_cdf = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_recovered_cdf'))),
                                            className='figure_recovered'), className='figure_rows'))

# fig_global_deceased_cdf = confirm_cdf(df_dea, 2)
fig_deceased_cdf = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_deceased_cdf'))),
                                           className='figure_deceased'), className='figure_rows'))

# fig_global_active_cdf = confirm_cdf(df_act, 3)
fig_active_cdf = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_active_cdf'))),
                                         className='figure_active'), className='figure_rows'))

# daily
# fig_global_confirmed_daily = confirm_daily(df_con, 0)
fig_confirmed_daily = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_confirmed_daily'))),
                                              className='figure_confirmed'), className='figure_rows'))

# fig_global_recovered_daily = confirm_daily(df_rec, 1)
fig_recovered_daily = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_recovered_daily'))),
                                              className='figure_recovered'), className='figure_rows'))

# fig_global_deceased_daily = confirm_daily(df_dea, 2)
fig_deceased_daily = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_deceased_daily'))),
                                             className='figure_deceased'), className='figure_rows'))

# fig_global_active_daily = confirm_daily(df_act, 3)
fig_active_daily = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_active_daily'))),
                                           className='figure_active'), className='figure_rows'))

# rate
# fig_global_confirmed_rate = confirm_rate(df_con, 0)
fig_confirmed_rate = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_confirmed_rate'))),
                                             className='figure_confirmed'), className='figure_rows'))

# fig_global_recovered_rate = confirm_rate(df_rec, 1)
fig_recovered_rate = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_recovered_rate'))),
                                             className='figure_recovered'), className='figure_rows'))

# fig_global_deceased_rate = confirm_rate(df_dea, 2)
fig_deceased_rate = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_deceased_rate'))),
                                            className='figure_deceased'), className='figure_rows'))

# fig_global_active_rate = confirm_rate(df_act, 3)
fig_active_rate = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody(html.Div(dcc.Graph(id='fig_active_rate'))),
                                          className='figure_active'), className='figure_rows'))

###### default output ######
[f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13] = [
         create_global_bar(df_top),
         confirm_cdf(df_con, c=0), confirm_cdf(df_rec, c=1),
             confirm_cdf(df_dea, c=2), confirm_cdf(df_act, c=3),

         confirm_daily(df_con, c=0), confirm_daily(df_rec, c=1),
             confirm_daily(df_dea, c=2), confirm_daily(df_act, c=3),

         confirm_rate(df_con, c=0), confirm_rate(df_rec, c=1),
             confirm_rate(df_dea, c=2), confirm_rate(df_act, c=3)]

# https://community.plotly.com/t/is-there-a-way-to-only-update-on-a-button-press-for-apps-where-updates-are-slow/4679/7

@app.callback([
    Output("fig_bar", "figure"),
    Output("fig_confirmed_cdf", "figure"), Output("fig_recovered_cdf", "figure"),
        Output("fig_deceased_cdf", "figure"), Output("fig_active_cdf", "figure"),
    Output("fig_confirmed_daily", "figure"), Output("fig_recovered_daily", "figure"),
        Output("fig_deceased_daily", "figure"), Output("fig_active_daily", "figure"),
    Output("fig_confirmed_rate", "figure"), Output("fig_recovered_rate", "figure"),
        Output("fig_deceased_rate", "figure"), Output("fig_active_rate", "figure")],
    [Input('button', 'n_clicks')],
    state = [State("_no_of_cntry", "value"), State("_hgh_or_lw", "value"), State("_feature", "value"),
     State("_cntry_name", "value"), State("_tabs", "active_tab")])

def output_text(n_clicks, _no_of_cntry, _hgh_or_lw, _feature, _cntry_name, _tabs):

    if _tabs == 'tab-1':
        _cntry_name = '#'

    output = [f1, f2, f3, f4, f5, f6, f7,
              f8, f9, f10, f11, f12, f13]

    # print('.. clicks ---->>>', n_clicks)
    if n_clicks:
        output = [create_global_bar(df_top, _no_of_cntry, _feature, _hgh_or_lw, _cntry_name),
                  confirm_cdf(df_con, c=0, cntry_name=_cntry_name), confirm_cdf(df_rec, c=1, cntry_name=_cntry_name),
                  confirm_cdf(df_dea, c=2, cntry_name=_cntry_name), confirm_cdf(df_act, c=3, cntry_name=_cntry_name),

                  confirm_daily(df_con, c=0, cntry_name=_cntry_name),
                  confirm_daily(df_rec, c=1, cntry_name=_cntry_name),
                  confirm_daily(df_dea, c=2, cntry_name=_cntry_name),
                  confirm_daily(df_act, c=3, cntry_name=_cntry_name),

                  confirm_rate(df_con, c=0, cntry_name=_cntry_name), confirm_rate(df_rec, c=1, cntry_name=_cntry_name),
                  confirm_rate(df_dea, c=2, cntry_name=_cntry_name), confirm_rate(df_act, c=3, cntry_name=_cntry_name)]

        return output

    elif n_clicks==None:
        return output


##########################
# app
github = html.A(dbc.CardImg(src="assets/images/github.svg", top=True, className='image_link'), href='https://github.com/SarthakV7/covid_dashboard', target="_blank", className='image_1')
linkedin = html.A(dbc.CardImg(src="assets/images/linkedin.svg", top=True, className='image_link'), href='https://www.linkedin.com/in/sarthak-vajpayee/', target="_blank")
kaggle = html.A(dbc.CardImg(src="assets/images/kaggle.svg", top=True, className='image_link'), href='https://www.kaggle.com/sarthakvajpayee', target="_blank")
medium = html.A(dbc.CardImg(src="assets/images/medium.png", top=True, className='image_link'), href='https://medium.com/@itssarthakvajpayee/', target="_blank")

profile_links = dbc.Row([dbc.Col(width=2, className='link_col'),
                         dbc.Col(github, width=2, className='link_col'),
                         dbc.Col(linkedin, width=2, className='link_col'),
                         dbc.Col(kaggle, width=2, className='link_col'),
                         dbc.Col(medium, width=2, className='link_col'),
                         dbc.Col(width=2, className='link_col')], className='link_icons')

heading = html.Div(dbc.Row([dbc.Col(html.H2("Covid-19 Global Dashboard", className='page_title'), width=8, className='header_col1'),
                            dbc.Col(profile_links, width=4, className='header_col2')],
                            className='header_container'))

text_1 = dcc.Markdown('''Johns Hopkins University has made an excellent [dashboard](https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6) using the affected cases data. Data is extracted from the google sheets associated and made available [here](https://github.com/CSSEGISandData/COVID-19).''')
text_2 = dcc.Markdown('''From [World Health Organization](https://www.who.int/emergencies/diseases/novel-coronavirus-2019) - On 31 December 2019, WHO was alerted to several cases of pneumonia in Wuhan City, Hubei Province of China. The virus did not match any other known virus. This raised concern because when a virus is new, we do not know how it affects people.
So daily level information on the affected people can give some interesting insights when it is made available to the broader data science community.
The purpose of this dashboard is to spread awareness and provide some useful insights on COVID-19 by the means of data.''')
text_3 = dcc.Markdown('''I am a data lover who loves to create impactful tools that could help people make this world a better place.''')

summary = dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
                                    html.Div('About the COVID-19 Global Dashboard:', className='ques'),
                                    html.Div(text_2, className='ans'),
                                    html.Div('Source of the COVID-19 data:', className='ques'),
                                    html.Div(text_1, className='ans'),
                                    html.Div('About me:', className='ques'),
                                    html.Div(text_3, className='ans')
                                    ]), className='figure_summary'), className='figure_rows'))

last_time = np.random.randint(6, 24)
last_update = f'The data was last updated {last_time} hours ago.'
data_update = dbc.Row(dbc.Col(html.H6(last_update), className='last_update_1'),
                      className='last_update')

footer = html.Div(dbc.Row([dbc.Col([profile_links])], className='header_container'))

app.layout = html.Div(children=[
    # heading,
    fig_map,
    html.Div(dbc.Row([
                dbc.Col([table_card, data_update], className='table_container', width=4),
                dbc.Col([
                    card_container_row,
                    tabs,
                    fig_bar,
                    fig_confirmed_cdf,
                    fig_recovered_cdf,
                    fig_deceased_cdf,
                    fig_active_cdf,
                    fig_confirmed_daily,
                    fig_recovered_daily,
                    fig_deceased_daily,
                    fig_active_daily,
                    fig_confirmed_rate,
                    fig_recovered_rate,
                    fig_deceased_rate,
                    fig_active_rate,
                    fig_sunburst_confirmed,
                    fig_sunburst_recovered,
                    fig_sunburst_deaths,
                    fig_sunburst_active,
                    summary
                    ], width=8),
                ]), className='table_card_row'),
        footer
        ])

executor = ThreadPoolExecutor(max_workers=1)
executor.submit(update_data)

if __name__ == '__main__':
    app.run_server(debug=True)
