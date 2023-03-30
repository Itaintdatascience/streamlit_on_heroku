# from vega_datasets import data
# import streamlit as st
# import altair as alt

# def main():
#     df = load_data()
#     page = st.sidebar.selectbox("Choose a page", ["Homepage", "Exploration"])

#     if page == "Homepage":
#         st.header("This is your data explorer.")
#         st.write("Please select a page on the left.")
#         st.write(df)
#     elif page == "Exploration":
#         st.title("Data Exploration")
#         x_axis = st.selectbox("Choose a variable for the x-axis", df.columns, index=3)
#         y_axis = st.selectbox("Choose a variable for the y-axis", df.columns, index=4)
#         visualize_data(df, x_axis, y_axis)

# @st.cache
# def load_data():
#     df = data.cars()
#     return df

# def visualize_data(df, x_axis, y_axis):
#     graph = alt.Chart(df).mark_circle(size=60).encode(
#         x=x_axis,
#         y=y_axis,
#         color='Origin',
#         tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
#     ).interactive()

#     st.write(graph)

# if __name__ == "__main__":
#     main()

### REQUIREMENTS ###
import os
import streamlit as st
import pandas as pd
import numpy as np
# from gsheetsdb import connect
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from annotated_text import annotated_text
import altair as alt

cwd = os.getcwd()

def main():
    st.set_page_config(
        page_title="Client App Demo | Streamlit",
        page_icon="⭐️⭐️⭐️",
        # page_icon="chart_with_upwards_trend",
        layout="wide",
        initial_sidebar_state="expanded"
        # primaryColor="purple"
        )


    # Build Streamlit UI


    # Connect to Data Source (Can be elasticSearch or any other api)
    st.header("XYZ Client Portal")

    df = load_data()
    file_type_filter = st.sidebar.multiselect("Filter by document type(s):", 
                                 sorted(list(df['file_type'].unique())))
    st.sidebar.write("##")
    slider_ePHI = st.sidebar.slider('ePHI Score Range: ', 0, 100)

    
    st.sidebar.write("##")


    


    if file_type_filter:

        df = df[(df.file_type.isin(file_type_filter))]
        st.write("Data Snapshot:")
        st.write(df)
        st.write("##")

        col1, col2, col3 = st.columns(3)
        col1.metric('Breach % Change', df['breach_value'].max())
        col2.metric('Breach % Change', df['breach_value'].max())
        col3.metric('Breach % Change', df['breach_value'].max())
        st.write("##")
        # st.download_button('Download Data', df)
        thresh = df[df['ePHI_Score'] > 90]
        st.write("##")
        st.write("##")

        ##### 3-dimension SCATTER PLOT #####
        scatter = alt.Chart(df).mark_circle().encode(x='days_ago', y='breach_value', size='severity_score',  
                                                   color='severity_score')
        st.altair_chart(scatter)


        fig1 = px.bar(df.sort_values('breach_value', ascending=False), 
            x="file_type", 
            y="breach_value", 
            color="directory", 
            title="File Distribution by Breach Value", 
            template = 'ggplot2',
            height=500)

        fig2 = px.bar(df, 
            category_orders={"severity_band": ["Critical", "Warning", "Informational"]},
            x="breach_value", 
            y="severity_band", 
            color='file_type', 
            hover_data = ['file_type'],
            orientation='h',         
            height=500,
            title='Severity Bands',
            template = 'ggplot2')

        fig2.update_layout(barmode='stack')

        # PLOT:
        col1, col2 = st.columns(2)

        col1.plotly_chart(fig1)
        col2.plotly_chart(fig2)


        annotated_text(
            ("Insight:", "", "#afa")
            )


        if df[df['ePHI_Score'] > 90]['ePHI_Score'].min() <= 90:
            st.markdown('Detected {} documents at risk (90%+ ePHI Score) with a total Breach Value of ${}'.format(len(df), 
                                                                                                                round(sum(df['breach_value']), 2)))
            st.markdown('Documents last scanned {} days ago'.format(df['days_ago'].min()))

        else:
            st.markdown('Detected {} documents at risk (90%+ ePHI Score) with a total Breach Value of ${}'.format(len(thresh), 
                                                                                                                round(sum(thresh['breach_value']), 2)))
            st.markdown('Documents last scanned {} days ago'.format(df['days_ago'].min()))

        st.write("##")

        annotated_text(
            ("Action:", "", "#faa"),
            )
        st.text("'It is not a matter of if you are attacked, it is a matter of when'")
        st.markdown('- We found {} Critical item(s) that need your attention with a total Breach Value of ${}'.format(len(df[df['severity_band'] == 'Critical']), round(df[df['severity_band'] == 'Critical']['breach_value'].sum(), 2)))
        st.markdown('- Here are the paths to the directories:')
        st.code("{}".format(df[df['severity_band'] == 'Critical']['file_extension'].to_list()))
        st.write("##")

        csv = convert_df(df)
        st.sidebar.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='output.csv',
            mime='text/csv',
        )

    else:
        st.write("Data Snapshot:")
        st.write(df)
        st.write("##")

        ### CALL OUT METRICS ###
        col1, col2, col3 = st.columns(3)
        col1.metric('Breach % Change', df['breach_value'].max())
        col2.metric('Breach % Change', df['breach_value'].max())
        col3.metric('Breach % Change', df['breach_value'].max())
        st.write("##")
        ##### 3-dimension SCATTER PLOT #####
        scatter = alt.Chart(df).mark_circle().encode(x='days_ago', y='breach_value', size='severity_score',  
                                                   color='severity_score')
        st.altair_chart(scatter)

        # create ePHI thres score for urgent records
        thresh = df[df['ePHI_Score'] > 90]
        sev_order = ["Critical","Warning","Informational"]
        fig1 = px.bar(df.sort_values('breach_value', ascending=False), 
            x="file_type", 
            y="breach_value", 
            color="directory", 
            title="File Distribution BY breach value", 
            height=500,
            template = 'ggplot2')

        fig2 = px.bar(df, 
            category_orders={"severity_band": ["Critical", "Warning", "Informational"]},
            x="breach_value", 
            y="severity_band", 
            color='file_type', 
            orientation='h',
            hover_data = ['file_type'],
            height=500,
            title='Severity Bands',
            template = 'ggplot2')

        fig2.update_layout(barmode='stack')

        # PLOT:
        col1, col2 = st.columns(2)

        col1.plotly_chart(fig1)
        col2.plotly_chart(fig2)

        annotated_text(
            ("Insight:", "", "#afa")
            )

        st.markdown('- Detected {} documents at risk (90%+ ePHI Score) with a total Breach Value of ${}'.format(len(thresh), round(sum(thresh['breach_value']), 2)))
        st.markdown('- Documents last scanned {} days ago'.format(thresh['days_ago'].min()))


        annotated_text(
            ("Action:", "", "#faa")
            )

        st.markdown('- We found {} Critical item(s) that need your attention with a total Breach Value of ${}'.format(len(df[df['severity_band'] == 'Critical']), round(df[df['severity_band'] == 'Critical']['breach_value'].sum(), 2)))
        st.markdown('- Here are the paths to the directories:')
        st.code("{}".format(df[df['severity_band'] == 'Critical']['file_extension'].to_list()))
        # annotated_text(
        #   ("We found "),
        #     ("{}".format(len(df[df['severity_band'] == 'Critical'])), "", "#faa"),
        #     ("Critical item(s) that need your attention with a total Breach Value of "),
        #     ("${}".format(round(df[df['severity_band'] == 'Critical']['breach_value'].sum(), 2)), "", "#faa")
        #     )
        csv = convert_df(df)
        st.sidebar.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='output.csv',
            mime='text/csv',
        )




    st.write("##")
    st.write("##")
    st.write("##")


    # embed iframe example:
    st.markdown("##### Embedded iFrame Example:")
    st.write("##")

    placeholder = st.empty()


    # Here's to demonstrate that you can take native / pre-built dashboards, and embed them directly into the Streamlit Web App for further drill downs and analysis
    components.iframe("http://localhost:5601/app/dashboards#/view/7adfa750-4c81-11e8-b3d7-01146121b73d?embed=true&_g=()&_a=(viewMode:view)&hide-filter-bar=true",
                    width=1285, 
                    height=3000, 
                    scrolling=True)



# Function to Load & Cache Data (essentially will be the elasticSearch Query via python wrapper)
@st.cache
def load_data():
    # gsheet_url = "https://docs.google.com/spreadsheets/d/1o1cKCZ-uHCs0BKRRtzQlZy2roCywCpMBqo4P-etjBKQ/edit?usp=sharing"
    # conn = connect()
    # rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
    # df = pd.DataFrame(rows)
    df = pd.read_csv("~/ts_data_prod - Sheet1.csv")
    df['days_ago'] = df['days_ago'].astype(int)
    df['ePHI_Score'] = df['ePHI_Score'].astype(float)
    df['user_ID'] = df['user_ID'].astype(int).astype(str)
    df['breach_value'] = df['breach_value'].astype(int)
    df['file_size_mb'] = df['file_size_mb'].astype(int)

    # user ePHI_Score as a weight multiplier for breach value
    df['severity_score'] = df['ePHI_Score'] * df['breach_value']

    def severity_bucket(x):
        """
        Create Severity score bands. Users can take action on the given statistical ranges.
        """
        if x > df['severity_score'].describe()['75%']:

            return "Critical"

        elif x >= df['severity_score'].describe()['25%'] <= df['severity_score'].describe()['75%']:

            return "Warning"

        else:
            return "Informational"

    df['severity_band'] = df['severity_score'].apply(severity_bucket)

    return df


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


if __name__ == "__main__":
    main()