import base64

import altair as alt
import streamlit as st

import strava
from pandas.api.types import is_numeric_dtype
import pandas as pd


st.set_page_config(
    page_title="Streamlit Activity Viewer for Strava",
    page_icon=":mountain_bicyclist:",
)

st.image("https://analytics.gssns.io/pixel.png")

strava_header = strava.header()

st.markdown(
    """
    # :mountain_bicyclist: PwCs Alpe predictor
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
st.text(f'{strava_auth["athlete"]["firstname"]} great you participate in the alpe du zwift event')

st.text(str(strava_auth["athlete"]["weight"]) +' kg is not going to help you but still you might make it to the top..')
st.text("Your prior zwift activities show a great upwards trend")
st.dataframe(strava.all_strava_activity(auth=strava_auth).style.format(subset=['distance','average_watts','weighted_average_watts','suffer_score'], formatter="{:.1f}"))

st.header('Your predicted time to the top of the alpe is 52 minutes and 13 seconds')
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
