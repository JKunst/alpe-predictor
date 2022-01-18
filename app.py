import base64

import altair as alt
import streamlit as st
import pandas as pd
import strava
from pandas.api.types import is_numeric_dtype
import datetime

# streamlit_app.py
import gspread as gs
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet_data(worksheet):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('cred.json', scope)
    # authorize the clientsheet
    client = gs.authorize(creds)
    # get the instance of the Spreadsheet
    sheet = client.open('strava_file')
    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(worksheet)
    # get all the records of the data
    records_data = sheet_instance.get_all_records()
    # view the data
    # convert the json to dataframe
    records_df = pd.DataFrame.from_dict(records_data)
    return records_df

import gspread_dataframe as gd
import gspread as gs

def export_to_sheets(worksheet_name,df,mode='r'):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('cred.json', scope)
    # authorize the clientsheet
    client = gs.authorize(creds)
    ws = client.open("strava_file").worksheet(worksheet_name)
    if(mode=='w'):
        ws.clear()
        gd.set_with_dataframe(worksheet=ws,dataframe=df,include_index=False,include_column_header=True,resize=True)
        return True
    elif(mode=='a'):
        ws.add_rows(df.shape[0])
        gd.set_with_dataframe(worksheet=ws,dataframe=df,include_index=False,include_column_header=False,row=ws.row_count+1,resize=False)
        return True
    else:
        return gd.get_as_dataframe(worksheet=ws)

def prediction(weight, ftp):
    wpkg = ftp/weight
    time = (180*60)/wpkg+300
    hours=int(time/3600)
    if hours >0:
        minutes =int((time-3600)/60)
        seconds = int(time - hours*3600 - minutes * 60)
    else:
        minutes = int((time)/60)
        seconds = int(time - hours - minutes*60)
    result = {'hours':hours,
              'minutes':minutes,
              'seconds':seconds}
    return result


st.set_page_config(
    page_title="Streamlit Activity Viewer for Strava",
    page_icon=":mountain_bicyclist:",
)

st.image("https://analytics.gssns.io/pixel.png")

strava_header = strava.header()

st.markdown(
    """
    # :mountain_bicyclist: DA Alpe predictor
    Authenticate your strava and see your prediction for the Alpe!
    """
)

strava_auth = strava.authenticate(header=strava_header, stop_if_unauthenticated=False)

if strava_auth is None:
    st.markdown("Click the \"Connect with Strava\" button at the top to login with your Strava account and get started.")
    # st.image(
    #     "https://files.gssns.io/public/streamlit-activity-viewer-demo.gif",
    #     caption="Streamlit Activity Viewer demo",
    #     use_column_width="always",
    # )
    st.stop()

athlete = strava.get_athlete(strava_auth)
try:
    weight = int(athlete["weight"])
except:
    weight = int(77)
try:
    ftp=int(athlete['ftp'])
except:
    ftp = int(200)



st.text(f'{strava_auth["athlete"]["firstname"]} great you participate in the alpe du zwift event')

st.text(str(weight) +' kg is not going to help you but still you might make it to the top..')
weight = st.number_input('Adjust your weight if necessary:',45,150, value=weight)
st.text(f'Your ftp from strava is:{ftp}')
ftp = st.number_input('If necessary adjust it for the Alpe time prediction',100,500, value=ftp)
st.text("Your prior zwift activities show a great upwards trend")

predicted = prediction(weight=weight,ftp=ftp)

if predicted['hours']>1:
    st.header(f"Your predicted time to the top of the alpe is {predicted['hours']} uur, {predicted['minutes']} minutes and {predicted['seconds']} seconds")
else:
    st.header(f"Your predicted time to the top of the alpe is {predicted['minutes']} minutes and {predicted['seconds']} seconds")

try:
    st.dataframe(strava.zwift_strava_activity(auth=strava_auth).style.format(subset=['distance','average_watts','weighted_average_watts','suffer_score'], formatter="{:.1f}"))
except:
    pass

st.markdown('Just like the Alpe dHuez from the Tour de France, this route is 12.24 km (7.6 miles) long, with a total elevation gain of over 1000 meters (3400′)! It’s a brutal 8.5% gradient, which is never constant - you have to deal with frequent ramps of 13-14%. The Road to Sky route is 17 km and is the shortest route to include the Alpe. '
            ' route includes the run down into the Jungle - wave to the sloth and pass the ruins, then turn off the gravel and hit the first 10% ramp. Don’t be fooled; even this meagre 17 km route will take in excess of 1 hour at a strong pace! '
            ' you ride the entire way up at 3 w/kg I would expect you to summit in around 1 hour; the fastest times on the official Strava segment by Zwift Insider are 31:35 for men, by Brent House and 35:18 for women, by Vegan Soldier. ')

activities = strava.all_strava_activity(auth=strava_auth)
old = get_sheet_data(0)
activities = activities.append(old)
activities = activities.drop_duplicates()

export_to_sheets('activities', activities,'w')

stats = strava.strava_user(auth=strava_auth)
old_user = get_sheet_data(1)
stats = stats.append(old_user)
stats = stats.drop_duplicates()

export_to_sheets('users', stats,'w')

# activity = strava.select_strava_activity(strava_auth)
# data = strava.download_activity(activity, strava_auth)
# csv = data.to_csv()
# csv_as_base64 = base64.b64encode(csv.encode()).decode()
# st.markdown(
#     (
#         f"<a "
#         f"href=\"data:application/octet-stream;base64,{csv_as_base64}\" "
#         f"download=\"{activity['id']}.csv\" "
#         f"style=\"color:{strava.STRAVA_ORANGE};\""
#         f">Download activity as csv file</a>"
#     ),
#     unsafe_allow_html=True
# )
#
#
# columns = []
# for column in data.columns:
#     if is_numeric_dtype(data[column]):
#         columns.append(column)
#
# selected_columns = st.multiselect(
#     label="Select columns to plot",
#     options=columns
# )
#
# data["index"] = data.index
#
# if selected_columns:
#     for column in selected_columns:
#         altair_chart = alt.Chart(data).mark_line(color=strava.STRAVA_ORANGE).encode(
#             x="index:T",
#             y=f"{column}:Q",
#         )
#         st.altair_chart(altair_chart, use_container_width=True)
# else:
#     st.write("No column(s) selected")
