
import requests
import pandas as pd
import numpy as np
import json
import mysql.connector
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu

mydb = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
)

mycursor = mydb.cursor(buffered=True)




st.set_page_config(layout="wide")

selected = option_menu(None,
                       options = ["Home","Analysis","Insights","About",],
                       icons = ["bar-chart","house","toggles","at"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"container": {"width": "100%"},
                               "icon": {"color": "white", "font-size": "24px"},
                               "nav-link": {"font-size": "24px", "text-align": "center", "margin": "-4px" ,"--hover-color": "#800080"},
                               "nav-link-selected": {"background-color": "#800080"},
                               "nav": {"background-color": "#E6E6FA"}})

# ABOUT PAGE
if selected == "About":
    col1, col2, = st.columns(2)
    col1.image("https://sarkaripariksha.com/daily-news-images/1676025622-news.jpeg", width=550)
    with col1:
        st.subheader(
            "PhonePe  is an Indian digital payments and financial technology company headquartered in Bengaluru, Karnataka, India. PhonePe was founded in December 2015, by Sameer Nigam, Rahul Chari and Burzin Engineer. The PhonePe app, based on the Unified Payments Interface (UPI), went live in August 2016. It is owned by Flipkart, a subsidiary of Walmart.")
        st.markdown("[DOWNLOAD APP](https://www.phonepe.com/app-download/)")

    with col2:
        st.image("https://dutchuncles.in/wp-content/uploads/2021/05/PhonePe-Copy.jpg",width=700)


# HOME PAGE
if selected == "Home":
    col1,col2 = st.columns(2)
    with col1:
        st.video("https://youtu.be/c_1H6vivsiA")
    with col2:
        st.title(':violet[PHONEPE PULSE DATA VISUALISATION]')
        st.subheader(':violet[Phonepe Pulse]:')
        st.write('PhonePe Pulse is a feature offered by the Indian digital payments platform called PhonePe.PhonePe Pulse provides users with insights and trends related to their digital transactions and usage patterns on the PhonePe app.')
        st.subheader(':violet[Phonepe Pulse Data Visualisation]:')
        st.write('Data visualization refers to the graphical representation of data using charts, graphs, and other visual elements to facilitate understanding and analysis in a visually appealing manner.'
                 'The goal is to extract this data and process it to obtain insights and information that can be visualized in a user-friendly manner.')

    st.write("---")

    # ANALYSIS PAGE
if selected == "Analysis":
    st.title(':violet[ANALYSIS]')
    st.subheader('Analysis done on the basis of All India ,States, Districts and Top categories between 2018 and 2023')
    select = option_menu(None,
                         options=["INDIA", "STATES", "TOP CATEGORIES" ],
                         default_index=0,
                         orientation="horizontal",
                         styles={"container": {"width": "100%"},
                                   "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px"},
                                   "nav-link-selected": {"background-color": "#6F36AD"}})

    if select == "INDIA":
        tab1, tab2 = st.tabs(["TRANSACTION","USER"])

        # TRANSACTION TAB
        with tab1:
            col1, col2, col3 = st.columns(3)
            with col1:
                year = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='year')
            with col2:
                qtr = st.selectbox('**Select Quarter**', ('1','2','3','4'), key='qtr')
            with col3:
                 Trans_type = st.selectbox('**Select Transaction type**',
                                            ('Recharge & bill payments', 'Peer-to-peer payments',
                                             'Merchant payments', 'Financial Services', 'Others'), key='Trans_type')
                 
            try:
    # Transaction Analysis bar chart query
                mycursor.execute(f"SELECT State, Transacion_amount FROM phonepe.agg_transaction WHERE Year = '{year}' AND Quater = '{qtr}' AND Transacion_type = '{Trans_type}';")
                Trans_query1 = mycursor.fetchall()
                df_Trans= pd.DataFrame(Trans_query1, columns=['State', 'Transaction_amount'])
                df_Trans_res = df_Trans.set_index(pd.Index(range(1, len(df_Trans) + 1)))

    # Transaction Analysis table query 
                mycursor.execute(f"SELECT State,Transacion_count, Transacion_amount FROM phonepe.agg_transaction WHERE Year = '{year}' AND Quater = '{qtr}' AND Transacion_type = '{Trans_type}';")
                Trans_query2 = mycursor.fetchall()
                df_Trans2= pd.DataFrame(Trans_query2, columns=['State','Transacion_count', 'Transaction_amount'])
                df_Trans_res2 = df_Trans2.set_index(pd.Index(range(1, len(df_Trans2) + 1)))

    # Total Transaction Amount table query
                mycursor.execute(f"SELECT SUM(Transacion_amount), AVG(Transacion_amount) FROM phonepe.agg_transaction WHERE Year = '{year}' AND Quater = '{qtr}' AND Transacion_type = '{Trans_type}';")
                Trans_query3 = mycursor.fetchall()
                df_Trans3= pd.DataFrame(Trans_query3, columns=['Total', 'Average'])
                df_Trans_res3 = df_Trans3.set_index(['Average'])

     # Total Transaction Count table query
                mycursor.execute(f"SELECT SUM(Transacion_count), AVG(Transacion_count) FROM phonepe.agg_transaction WHERE Year = '{year}' AND Quater = '{qtr}' AND Transacion_type = '{Trans_type}';")
                Trans_query4 = mycursor.fetchall()
                df_Trans4= pd.DataFrame(Trans_query4, columns=['Total', 'Average'])
                df_Trans_res4 = df_Trans4.set_index(['Average'])
                col,cols=st.columns([2,2])

                with col:
                    # GEO VISUALISATION
                    # Drop a State column from df_Trans
                    
                    df_Trans.drop(columns=['State'], inplace=True)
                    # Clone the gio data
                    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
                    response = requests.get(url)
                    data1 = json.loads(response.content)
                    state_list1 = [feature['properties']['ST_NM'] for feature in data1['features']]
                    state_list1.sort()
                # Create a DataFrame with the state names column
                    df_state_names_tra = pd.DataFrame({'State': state_list1})
                # Combine the Gio State name with df_Trans
                    df_state_names_tra['Transaction_amount'] = df_Trans
                 # convert dataframe to csv file
                    df_state_names_tra.to_csv('State_trans.csv', index=False)
                # Read csv
                    df_tra = pd.read_csv('State_trans.csv')
                # Geo plot 
                    fig_tra = px.choropleth(
                        df_tra,
                        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                        featureidkey='properties.ST_NM', locations='State', color='Transaction_amount',
                        color_continuous_scale='thermal', title='Transaction Analysis')
                    fig_tra.update_geos(fitbounds="locations", visible=False)
                    fig_tra.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)
                    st.plotly_chart(fig_tra, use_container_width=True)
                # ---------   /   All India Transaction Analysis Bar chart  /  ----- #
                    df_Trans_res['State'] = df_Trans_res['State'].astype(str)
                    df_Trans_res['Transaction_amount'] = df_Trans_res['Transaction_amount'].astype(float)
                    df_in_tr_tab_qry_rslt1_fig = px.bar(df_Trans_res, x='State', y='Transaction_amount',
                                                        color='Transaction_amount', color_continuous_scale='thermal',
                                                        title='Transaction Analysis Chart', height=700, )
                    df_in_tr_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
                    st.plotly_chart(df_in_tr_tab_qry_rslt1_fig, use_container_width=True) 

            

                 # -------  /  All India Total Transaction calculation Table   /   ----  #
                with cols:
                    col4,= st.columns(1)
                    with col4:
                        st.subheader(':violet[Transaction Analysis]')
                        st.dataframe(df_Trans_res2)
                    # with col5:
                    st.subheader(':violet[Transaction Amount]')
                    st.dataframe(df_Trans_res3)
                    st.subheader(':violet[Transaction Count]')
                    st.dataframe(df_Trans_res4) 
            except:
                pass
# USER TAB
        with tab2:
            col1,col2=st.columns(2)
            with col1:
                User_year =st.selectbox('**Select Year**',('2018', '2019', '2020', '2021', '2022','2023'),key='User_year')
            with col2:
                User_Qtr = st.selectbox('**Select Quarter**',('1','2','3','4'),key='User_Qtr')
        # SQL Query
                try:
        # User Analysis Bar chart query
                    mycursor.execute(f"SELECT State,SUM(User_count) FROM phonepe.agg_user WHERE Year = '{User_year}' AND Quater ='{User_Qtr}' GROUP BY State;")
                    User_Query =mycursor.fetchall()
                    df_User=pd.DataFrame(User_Query,columns=['State','User_count'])
                    df_User_res = df_User.set_index(pd.Index(range(1,len(df_User)+1)))
                    # Total User Count table query
                    mycursor.execute(f"SELECT SUM(User_count), AVG(User_count) FROM phonepe.agg_user WHERE Year = '{User_year}' AND Quater ='{User_Qtr}';")
                    User_Query1 =mycursor.fetchall()
                    df_User1=pd.DataFrame(User_Query1,columns=['Total','Average'])
                    df_User_res1 = df_User1.set_index(['Average'])
        # ---------   /   All India Transaction Analysis Bar chart  /  ----- #
                    # col8,cols9=st.columns(2)
                    # with col8:
                 
                    # -------  /  All India Total Transaction calculation Table   /   ----  #
                    # with cols9:   
                    col6 = st.columns(2)
                    st.header(':violet[User Count]')
                   
                    st.subheader(':violet[User Analysis]')
                    st.dataframe(df_User_res)
                    st.subheader(':violet[User Count]')
                    st.dataframe(df_User_res1)

        
                    df_User_res['State'] = df_User_res['State'].astype(str)
                    df_User_res['User_count'] = df_User_res['User_count'].astype(int)
                    df_in_us_tab_qry_rslt1_fig=px.sunburst(df_User_res, path=['State', 'User_count'], values='User_count')
                    st.subheader(':violet[User Count sunburst chart]')
                    st.plotly_chart(df_in_us_tab_qry_rslt1_fig, use_container_width=True)  
                    df_User_res['State'] = df_User_res['State'].astype(str)
                    df_User_res['User_count'] = df_User_res['User_count'].astype(int)
                    df_in_us_tab_qry_rslt1_fig = px.bar(df_User_res, x='State', y='User_count',
                                                    color='User_count', color_continuous_scale='thermal',
                                                    title='User Analysis Chart', height=700, )
                    df_in_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
                    st.plotly_chart(df_in_us_tab_qry_rslt1_fig, use_container_width=True) 

                     

                except:
                    pass

# STATE TAB
    if select == "STATES":
        tab3 ,tab4 = st.tabs(["TRANSACTION","USER"])
                #TRANSACTION TAB FOR STATE
        with tab3:
            col1, col2, col3 = st.columns(3)
            with col1:
                state_trans = st.selectbox('**Select State**', ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh', 'assam', 'bihar',
                                    'chandigarh', 'chhattisgarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat','haryana', 'himachal-pradesh',
                                    'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh','maharashtra', 'manipur',
                                    'meghalaya', 'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim','tamil-nadu', 'telangana',
                                    'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal	'), key='state_trans')
            with col2:
                state_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='state_yr')
            with col3:
                state_qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='state_qtr')
        # SQL QUERY
                try:
                    
            #Transaction Analysis bar chart query
                    mycursor.execute(f"SELECT Transaction_Distict ,Transaction_Amt FROM phonepe.map_transaction WHERE Year = '{state_yr}' AND Quater = '{state_qtr}' AND State ='{state_trans}';")
                    State_Query = mycursor.fetchall()
                    State_trans = pd.DataFrame(np.array(State_Query),columns=['Trans_Distict','Transa_Amt'])
                    State_Trans_res = State_trans.set_index(pd.Index(range(1, len(State_trans) + 1)))    
                    # Transaction Analysis table query
                    mycursor.execute(f"SELECT Transaction_Distict, Transaction_count, Transaction_Amt  FROM phonepe.map_transaction WHERE State = '{state_trans}' AND Year = '{state_yr}' AND Quater = '{state_qtr}';")
                    State_Query2 = mycursor.fetchall()
                    State_trans2 = pd.DataFrame(np.array(State_Query2),columns=['Districts', 'Transaction_count','Transaction_amount'])
                    State_Trans_res2 = State_trans2.set_index(pd.Index(range(1, len(State_trans2) + 1)))
                    # Total Transaction Amount table query
                    mycursor.execute(f"SELECT Transaction_Distict,SUM(Transaction_count), AVG(Transaction_Amt) FROM phonepe.map_transaction WHERE State = '{state_trans}' AND Year = '{state_yr}' AND Quater = '{state_qtr}'group by Transaction_Distict;")
                    State_Query3 = mycursor.fetchall()
                    State_trans3 = pd.DataFrame(np.array(State_Query3), columns=['Districts', 'Total', 'Average'])
                    State_Trans_res3 = State_trans3.set_index(['Average'])

                    # Total Transaction Count table query
                    mycursor.execute(f"SELECT Transaction_Distict,SUM(Transaction_count), AVG(Transaction_count) FROM phonepe.map_transaction WHERE State = '{state_trans}' AND Year = '{state_yr}' AND Quater = '{state_qtr}' group by Transaction_Distict")
                    State_Query4 = mycursor.fetchall()
                    State_trans4 = pd.DataFrame(State_Query4, columns=['Districts','Total', 'Average'])
                    State_Trans_res4= State_trans4.set_index(['Average'])
                # -----    /   State wise Transaction Analysis bar chart   /   ------ #

                    State_Trans_res['Districts'] = State_Trans_res['Districts'].astype(str)
                    State_Trans_res['Transaction_amount'] = State_Trans_res['Transaction_amount'].astype(float)
                    df_st_tr_tab_bar_qry_rslt1_fig = px.bar(State_Trans_res, x='Districts',
                                                        y='Transaction_amount', color='Transaction_amount',
                                                        color_continuous_scale='thermal',
                                                        title='Transaction Analysis Chart', height=500, )
                    df_st_tr_tab_bar_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
                    st.plotly_chart(df_st_tr_tab_bar_qry_rslt1_fig, use_container_width=True)

                    # ------  /  State wise Total Transaction calculation Table  /  ---- #
                    st.header(':violet[Total calculation]')
                    col4, col5 = st.columns(2)
                    with col4:
                        st.subheader(':violet[Transaction Analysis]')
                        st.dataframe(State_Trans_res2)
                    with col5:
                        st.subheader(':violet[Transaction Amount]')
                        st.dataframe(State_Trans_res3)
                        st.subheader(':violet[Transaction Count]')
                        st.dataframe(State_Trans_res4)   

                except:
                    pass  

            with tab4:
                col5, col6,col7 = st.columns(3)
                try:
                    with col5:
                        state_trans = st.selectbox('**Select State**', (
                        'Andaman & Nicobar', 'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar',
                        'chandigarh', 'chhattisgarh', 'Dadra and Nagar Haveli and Daman and Diu', 'delhi', 'goa', 'gujarat',
                        'haryana', 'himachal pradesh',
                        'jammu & kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya pradesh',
                        'maharashtra', 'manipur',
                        'meghalaya', 'mizoram', 'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim',
                        'tamil nadu', 'telangana',
                        'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal'), key='state_trans')
                    with col6:
                        state_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='state_yr')
                    with col7:
                        state_qtr = st.selectbox('**Select Quarter**', ('1', '2', '3', '4'), key='state_qtr')
                
                    column1,column2 = st.columns(2)
                    # SQL QUERY
                    try:
                        # User Analysis Bar chart query
                        
                        mycursor.execute(f"SELECT Transaction_Distict, SUM(Reg_Count) FROM phonepe.map_user WHERE State = '{state_trans}' AND Year = '{state_yr}' AND Quater = '{state_qtr}' GROUP BY Transaction_Distict;")
                        User_Qu1 = mycursor.fetchall()
                        User_t1 = pd.DataFrame(np.array(User_Qu1), columns=['District', 'User Count'])
                        User_t1_res1 = User_t1.set_index(pd.Index(range(1, len(User_t1) + 1)))

                        # Total User Count table query
                        mycursor.execute(f"SELECT Transaction_Distict,SUM(Reg_Count), AVG(Reg_Count) FROM phonepe.map_user WHERE State = '{state_trans}' AND Year = '{state_yr}' AND Quater = '{state_qtr}'' GROUP BY Transaction_Distict;")
                        User_Qu2 = mycursor.fetchall()
                        User_t2 = pd.DataFrame(np.array(User_Qu2), columns=['District','Total', 'Average'])
                        User_t2_res2 = User_t2.set_index(['District'])
                    except:
                        pass

                    with column1:

                        # -----   /   All India User Analysis Bar chart   /   ----- #
                        #df_st_us_tab_qry_rslt1['District'] = df_st_us_tab_qry_rslt1['District'].astype(int)
                        User_t1_res1['User Count'] = User_t1_res1['User Count'].astype(int)
                        df_st_us_tab_qry_rslt1_fig = px.bar(User_t1_res1, x='District', y='User Count', color='User Count',
                                                            color_continuous_scale='thermal', title='User Analysis Chart',
                                                            height=500, )
                        df_st_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
                        st.plotly_chart(df_st_us_tab_qry_rslt1_fig, use_container_width=True)



                    # ------    /   district wise User Total User calculation Table   /   -----#
                    with column2:
                        st.header(':violet[Total calculation]')

                        col3, col4 = st.columns(2)
                        with col3:
                            st.subheader(':violet[User Analysis]')
                            st.dataframe(User_t1_res1)
                        with col4:
                            st.subheader(':violet[User Count]')
                            st.dataframe(User_t2_res2)
                except:
                    pass 
           





 # TOP CATEGORIES
    if select == "TOP CATEGORIES":
        tab5, tab6 = st.tabs(["TRANSACTION", "USER"])

        # Overall top transaction
        #TRANSACTION TAB
        with tab5:
            top_tr_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='top_tr_yr')

            #SQL QUERY

            #Top Transaction Analysis bar chart query
            mycursor.execute(f"SELECT State, SUM(Top_Amount) As Top_Amount FROM phonepe.top_transaction WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Top_Amount DESC LIMIT 10;")
            top_query = mycursor.fetchall()
            df_top_trans = pd.DataFrame(top_query,columns=['State', 'Top Transaction amount'])
            df_top_trans_rslt = df_top_trans.set_index(pd.Index(range(1, len(df_top_trans) + 1)))

            # Top Transaction Analysis table query
            mycursor.execute(f"SELECT State, SUM(Top_Amount) as Transaction_amount, SUM(Top_Count) as Transaction_count FROM phonepe.top_transaction WHERE Year = '{top_tr_yr}'GROUP BY State ORDER BY Top_Amount DESC LIMIT 10;")
            top_query1 = mycursor.fetchall()
            df_top_trans1 = pd.DataFrame(top_query1,columns=['State', 'Top Transaction amount','Total Transaction count'])
            df_top_trans_rslt1 = df_top_trans1.set_index(pd.Index(range(1, len(df_top_trans1) + 1)))

            # All India Transaction Analysis Bar chart
            df_top_trans_rslt['State'] = df_top_trans_rslt['State'].astype(str)
            df_top_trans_rslt['Top Transaction amount'] = df_top_trans_rslt['Top Transaction amount'].astype(float)
            df_top_trans_fig = px.bar(df_top_trans_rslt, x='State', y='Top Transaction amount',
                                                    color='Top Transaction amount', color_continuous_scale='thermal',
                                                    title='Top Transaction Analysis Chart', height=600, )
            df_top_trans_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_top_trans_fig, use_container_width=True)


            #All India Total Transaction calculation Table
            st.header(':violet[Total calculation]')
            st.subheader('Top Transaction Analysis')
            st.dataframe(df_top_trans_rslt1)

        with tab6:
            top_us_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'), key='top_us_yr')

            #SQL QUERY

            #Top User Analysis bar chart query
            mycursor.execute(f"SELECT State, SUM(Reg_Count) AS Top_user FROM phonepe.top_user WHERE Year='{top_us_yr}' GROUP BY State ORDER BY Reg_Count DESC LIMIT 10;")
            top_us_query = mycursor.fetchall()
            df_us_trans = pd.DataFrame(top_us_query, columns=['State', 'Total User count'])
            df_us_trans_rslt = df_us_trans.set_index(pd.Index(range(1, len(df_us_trans) + 1)))



            #All India User Analysis Bar chart
            df_us_trans_rslt['State'] = df_us_trans_rslt['State'].astype(str)
            df_us_trans_rslt['Total User count'] = df_us_trans_rslt['Total User count'].astype(float)
            df_top_us_tab_qry_rslt1_fig = px.bar(df_us_trans_rslt, x='State', y='Total User count',
                                                 color='Total User count', color_continuous_scale='thermal',
                                                 title='Top User Analysis Chart', height=600, )
            df_top_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
            st.plotly_chart(df_top_us_tab_qry_rslt1_fig, use_container_width=True)

            #All India Total Transaction calculation Table
            st.header(':violet[Total calculation]')
            st.subheader(':violet[Total User Analysis]')
            st.dataframe(df_us_trans_rslt)


#INSIGHTS TAB
if selected == "Insights":
    st.title(':violet[BASIC INSIGHTS]')
    st.subheader("The basic insights are derived from the Analysis of the Phonepe Pulse data. It provides a clear idea about the analysed data.")
    options = ["--select--",
               "Top 10 states based on year and amount of transaction",
               "Top 10 Districts based on the Transaction Amount",
               "Least 10 Districts based on the Transaction Amount",
               "Top 10 Districts based on the Transaction count",
               "Least 10 Districts based on the Transaction count",
               "Top Transaction types based on the Transaction Amount",
               "Top 10 Mobile Brands based on the User count of transaction"]
    select = st.selectbox(":violet[Select the option]",options)


 #1
    if select == "Top 10 states based on year and amount of transaction":
        mycursor.execute(
            "SELECT DISTINCT State, SUM(Top_Amount) AS Total_Transaction_Amount FROM phonepe.top_transaction GROUP BY State ORDER BY Total_Transaction_Amount DESC LIMIT 10")

        data = mycursor.fetchall()
        df = pd.DataFrame(data, columns=['States', 'Transaction_amount'],index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 states based on amount of transaction")
            fig_px=px.pie(df, values= "Transaction_amount", names= "States", color_discrete_sequence=px.colors.sequential.dense_r,
                        title= "Top Mobile Brands of Transaction_count")
            st.plotly_chart(fig_px)

#2
    elif select == "Top 10 Districts based on the Transaction Amount":
        mycursor.execute(
            "SELECT DISTINCT State ,Transaction_Distict,SUM(Transaction_Amt) FROM phonepe.map_transaction GROUP BY State ,Transaction_Distict ORDER BY Transaction_Amt DESC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Transaction_Amount']
        df1 = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))
        col1, col2 = st.columns(2)
        with col1:
            st.write(df1)
    
 #3
    elif select == "Least 10 Districts based on the Transaction Amount":
        mycursor.execute(
            "SELECT DISTINCT State,Transaction_Distict,SUM(Transaction_Amt)FROM phonepe.map_transaction GROUP BY State, Transaction_Distict  ORDER BY Transaction_Amt ASC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)   

#4
    elif select == "Top 10 Districts based on the Transaction count":
        mycursor.execute("SELECT DISTINCT State,Transaction_Distict,SUM(Transaction_count)FROM phonepe.map_transaction GROUP BY State, Transaction_Distict  ORDER BY Transaction_count DESC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Transaction_Count']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)       

#5
    elif select == "Least 10 Districts based on the Transaction count":
        mycursor.execute("SELECT DISTINCT State,Transaction_Distict,SUM(Transaction_count)FROM phonepe.map_transaction GROUP BY State, Transaction_Distict  ORDER BY Transaction_count ASC LIMIT 10")
        data = mycursor.fetchall()
        columns = ['States', 'District', 'Transaction_Count']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
