import pandas as pd
import streamlit as st
import easyocr
import mysql.connector
from mysql.connector import (connection)
from streamlit_option_menu import option_menu
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re

# SETTING PAGE CONFIGURATIONS
st.set_page_config(
    page_title="Extracting Business Card Data with OCR",
    layout="wide",
    initial_sidebar_state="expanded"
)
selected = option_menu(None, 
                           options =["Home","Upload Bizcard","Modify"],
                           icons = ["house","credit_card","pencil"],
                          default_index=0,
                          orientation="horizontal",
                          styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "0px", 
                                                "--hover-color": "#19A1B5"},
                                   "icon": {"font-size": "40px"},
                                   "container" : {"max-width": "2000px"},
                                   "nav-link-selected": {"background-color": "#D3D3D3"},
                                   "nav": {"background-color": "#D3D3D3"}})

# Create a container for the icon and title
icon_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTSv11x2suJu2zqPU8yxBof44oe-gfiE9wxDw&usqp=CAU"
title = "Extracting Business Card Data with OCR"
st.markdown(
    f'<div><img src ="{icon_url}" alt="Icon" style ="height:50px; margin-right :10px;">,{title}</div>',
    unsafe_allow_html=True)
st.title("Extracting Business Card Data with OCR")

# SETTING-UP BACKGROUND IMAGE
def back_grd():
    st.markdown(f"""<style>.stApp{{
        background:url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT84jxS3JUAxw4zAOe3_uZ6Zd2VAk8HzF0ZTg&usqp=CAU");
                        background-size: cover;
    }}</style>""", unsafe_allow_html=True)
back_grd()

# HOME MENU

if selected == 'Home':
# Title image
     
    st.markdown(":black_large_square: **Project Title**: BizCardX: Extracting Business Card Data with OCR")
    technologies = "streamlit GUI, SQL, Data Extraction"
    st.markdown(f':black_large_square: **Techonologies** : {technologies}')
    overview = "Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR."
    st.markdown(f":black_large_square: **Overview** : {overview}")
    icon_url = "https://png.pngitem.com/pimgs/s/30-304321_business-cards-png-business-card-mockup-png-transparent.png"
    st.image(icon_url,use_column_width=True)

# UPLOAD AND EXTRACT MENU
if selected == 'Upload Bizcard':
  tab1,tab2,tab3=st.tabs(['UPLOAD','EXTRACT','STORE'])
  with tab1:
        st.markdown("### Upload a Business Card")
        uploaded_card=st.file_uploader("Upload Here",label_visibility="collapsed",type=["png", "jpeg", "jpg"])

        if uploaded_card is not None:
             # Save the uploaded file to a temporary directory
            temp_dir = os.path.join("uploaded_card")
            os.makedirs(temp_dir,exist_ok=True)
            temp_file_path = os.path.join(temp_dir, "temp_card.jpg")
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_card.getbuffer())


            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)   
with tab2:
         
    if uploaded_card is not None:
        if hasattr(uploaded_card, 'name') and uploaded_card.name is not None:
            with open(os.path.join("uploaded_cards", uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())
            # Rest of the code that depends on uploaded_card
            image = cv2.imread(temp_file_path)
            res = reader.readtext(temp_file_path)
            st.markdown("### Image Processed and Data Extracted")
        def image_preview(image, res):
                    for (bbox, text, prob) in res:
                       # unpack the bounding box
                        (tl, tr, br, bl) = bbox
                        tl = (int(tl[0]), int(tl[1]))
                        tr = (int(tr[0]), int(tr[1]))
                        br = (int(br[0]), int(br[1]))
                        bl = (int(bl[0]), int(bl[1]))
                        cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                        cv2.putText(image, text, (tl[0], tl[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    plt.rcParams['figure.figsize'] = (15, 15)
                    plt.axis('off')
                    plt.imshow(image)    

                    # DISPLAYING THE CARD WITH HIGHLIGHTS
            
                    with st.spinner("Please wait, processing image..."):
                            st.set_option('deprecation.showPyplotGlobalUse', False)
                            saved_img = os.path.join(os.getcwd(), "uploaded_cards", uploaded_card.name)
                            image = cv2.imread(saved_img)
                            res = reader.readtext(saved_img)
                            st.pyplot(image_preview(image, res))

                    # easyOCR
                    saved_img = os.path.join(os.getcwd(), "uploaded_cards", uploaded_card.name)
                    result = reader.readtext(saved_img, detail=0, paragraph=False)

                    # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
                    def img_to_binary(file):
                        # Convert image data to binary format
                        with open(file, 'rb') as file:
                            binaryData = file.read()
                        return binaryData
                     # DISPLAYING THE CARD WITH HIGHLIGHTS
        
                    with st.spinner("Please wait, processing image..."):
                        st.set_option('deprecation.showPyplotGlobalUse', False)
                        saved_img = os.path.join(os.getcwd(), "uploaded_cards", uploaded_card.name)
                        image = cv2.imread(saved_img)
                        res = reader.readtext(saved_img)
                        st.pyplot(image_preview(image, res))

               # easyOCR
                    saved_img = os.path.join(os.getcwd(), "uploaded_cards", uploaded_card.name)
                    result = reader.readtext(saved_img, detail=0, paragraph=False)

        # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData

        data = {"company_name": [],
                "card_holder": [],
                "designation": [],
                "mobile_number": [],
                "email": [],
                "website": [],
                "area": [],
                "city": [],
                "state": [],
                "pin_code": [],
                "image": img_to_binary(saved_img)
                }

        def get_data(res):
                for ind, i in enumerate(res):
                # To get WEBSITE_URL
                    if "www " in i.lower() or "www." in i.lower():
                            data["website"].append(i)
                    elif "WWW" in i:
                            data["website"] = res[4] + "." + res[5]
                    # To get EMAIL ID
                    elif "@" in i:
                            data["email"].append(i)
                    # To get MOBILE NUMBER
                    elif "-" in i:
                            data["mobile_number"].append(i)
                    if len(data["mobile_number"]) == 2:
                            data["mobile_number"] = " & ".join(data["mobile_number"])
                    # To get COMPANY NAME
                    elif ind == len(res) - 1:
                        data["company_name"].append(i)
                    # To get CARD HOLDER NAME
                    elif ind == 0:
                        data["card_holder"].append(i)
                    # To get DESIGNATION
                    elif ind == 1:
                        data["designation"].append(i)
                    # To get AREA
                    if re.findall('^[0-9].+, [a-zA-Z]+', i):
                        data["area"].append(i.split(',')[0])
                    elif re.findall('[0-9] [a-zA-Z]+', i):
                        data["area"].append(i)
                    # To get CITY NAME
                    match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                    match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                    match3 = re.findall('^[E].*', i)
                    if match1:
                        data["city"].append(match1[0])
                    elif match2:
                        data["city"].append(match2[0])
                    elif match3:
                        data["city"].append(match3[0])
                    # To get STATE
                    state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                    if state_match:
                        data["state"].append(i[:9])
                    elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                        data["state"].append(i.split()[-1])
                    if len(data["state"]) == 2:
                        data["state"].pop(0)
                    # To get PINCODE
                    if len(i) >= 6 and i.isdigit():
                        data["pin_code"].append(i)
                    elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                        data["pin_code"].append(i[10:])
        get_data(result)

# FUNCTION TO CREATE DATAFRAME
def create_df(data):
    df = pd.DataFrame(data)
    return df
df = create_df(data)
st.success("### Data Extracted!")
st.write(df)
pass
# STORING datas in mysql
with tab3:
    
    if df is not None and not df.empty:
        try:
            # CONNECTING WITH MYSQL DATABASE
            conn = connection.MySQLConnection(host="localhost", user="root", port='3306', database="om", password="April123$")
            cur = conn.cursor()
            for i, row in df.iterrows():
                sql = """INSERT INTO Business_Cards(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cur.execute(sql, tuple(row))
                # Commit the changes and close the cursor and connection
                conn.commit()
                cur.close()
                conn.close()
                st.success("Data uploaded to the database successfully!")
        except mysql.connector.Error as error:
            st.error(f"Failed to store data in the database: {error}")
    else:
        st.warning("No data to store. Please upload and extract business card data first.")
        st.warning("No data to store. Please upload and extract business card data first.") 
        pass

# MODIFY MENU
if selected == "Modify":
     # Title Image
    image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-mnIkBDCJ8COUP5ihU51dyVCoDTC8YuTbug&usqp=CAU"
    # Display the icon image at the top
    st.sidebar.image(image, use_column_width=True)

    
    icon_url = "https://png.pngitem.com/pimgs/s/30-304321_business-cards-png-business-card-mockup-png-transparent.png"
    st.image(icon_url,use_column_width=True)

    col1, col2, col3 = st.columns([3, 3, 2])
    col2.markdown("## Alteration and Deletion of Datas")
    column1, column2 = st.columns(2, gap="large")
    
    try:
        with column1:
            cur.execute("SELECT card_holder FROM Business_Cards")
            result = cur.fetchall()
            business_cards = {row[0]: row[0] for row in result}
            
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Modify the Datas")
            
            cur.execute("SELECT company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code FROM Business_Cards WHERE card_holder=%s", (selected_card,))
            result = cur.fetchone()
            
            # DISPLAYING ALL THE INFORMATION
            company_name = st.text_input("Company Name", result[0])
            card_holder = st.text_input("Card Holder", result[1])
            designation = st.text_input("Designation", result[2])
            mobile_number = st.text_input("Mobile Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            area = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pin Code", result[9])

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                cur.execute("""
                    UPDATE Business_Cards
                    SET company_name=%s, card_holder=%s, designation=%s, mobile_number=%s, email=%s, website=%s, area=%s, city=%s, state=%s, pin_code=%s
                    WHERE card_holder=%s
                """, (company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code, selected_card))
                conn.commit()
                st.success("New Information updated in the database successfully.")

        with column2:
            cur.execute("SELECT card_holder FROM Business_Cards")
            result =cur.fetchall()
            business_cards = {row[0]: row[0] for row in result}
            
            selected_card = st.selectbox("Select a card holder name to delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Are You Sure")
            
            if st.button("Yes,sure"):
                cur.execute(f"DELETE FROM Business_Cards WHERE card_holder='{selected_card}'")
                conn.commit()
                st.success("Business card infos deleted from the database.")
    except:
        st.warning(" No data available in the database")

    if st.button("View updated data"):
        cur.execute("SELECT company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code FROM Business_Cards")
        updated_data = pd.DataFrame(cur.fetchall(), columns=["Company Name", "Card Holder", "Designation", "Mobile Number", "Email", "Website", "Area", "City", "State", "Pin Code"])
        st.write(updated_data)

 



