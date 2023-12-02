
from googleapiclient.discovery import build
import pymongo
import mysql.connector
import pandas as pd
import streamlit as st
import base64


# API Key connection 

def api_connection():
    Api_id ="AIzaSyCarxRRhN0PzJGDbSrhDpOgt2KucH0VePk"
    Api_service_name = "Youtube"
    Api_version = "v3"
    youtube =build(Api_service_name, Api_version,developerKey=Api_id) 
    return youtube
youtube = api_connection()


# get channel infomation
def get_channel(channel_id):
  request = youtube.channels().list(
          part="snippet,contentDetails,statistics",
          id=channel_id
      )
  response = request.execute()

  for i in response['items']:
    data = dict(Channel_Name=i['snippet']['title'],
                Subscriber= i['statistics']['subscriberCount'],
                Total_Videos = i['statistics']['videoCount'],
                Playlist_Id=i['contentDetails']['relatedPlaylists']['uploads'],
                Channel_Id = i['id'],
                Views= i['statistics']['viewCount'],
                Channel_Description=i['snippet']['description']
                )
  return data

#get video ids
def get_videos_ids(channel_id):
    video_ids = []
    response = youtube.channels().list(id=channel_id,
        part = "contentDetails").execute()
    
    playlist_Id =response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    next_page_token = None
    

    # playlist video ids

    while True:
        response1 = youtube.playlistItems().list(
            part = 'snippet',
            playlistId =playlist_Id,
            maxResults=50,
            pageToken=next_page_token).execute()  


        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = response1.get('nextPageToken')
        if next_page_token is None:
            break
    return video_ids
 
 # Get Video information 
def get_videos_info(Video_Ids):
    video_data=[]
    for video_id in Video_Ids:
        request = youtube.videos().list(
            id=video_id,
            part = "snippet,contentDetails,statistics" )
        response=request.execute()
        
        for item in response['items'] :
            data = dict(Channel_Name = item['snippet']['channelTitle'],
                        Channel_Id =item['snippet']['channelId'],
                        Video_Id= item['id'],
                        Title=item['snippet']['title'],
                        Tags = item['snippet'].get('tags'),
                        Thumbnail=item['snippet']['thumbnails']['default']['url'],
                        Description=item['snippet'].get('description'),
                        publish_data=item['snippet']['publishedAt'],
                        Duration =item['contentDetails']['duration'],
                        Views =item['statistics'].get('viewCount'),
                        Likes=item['statistics'].get('likeCount'),
                        Comments=item['statistics'].get('commentCount'),
                        Favoritecount=item['statistics']['favoriteCount'],
                        Definition=item['contentDetails']['definition']
                        )
            video_data.append(data)
    return video_data

# Get comment information
def get_comment_info(video_data):
    Comment_data = []
    try:
        for video_id in video_data:
            request = youtube.commentThreads().list(
                part = "snippet",
                videoId = video_id,
                maxResults=50
            )
            response=request.execute()

            for items in response['items']:
                data = dict(Comment_id = items['snippet']['topLevelComment']['id'],
                            Video_id = items['snippet']['topLevelComment']['snippet']['videoId'],
                            Comment_Text =items['snippet']['topLevelComment']['snippet']['textDisplay'],
                            Comment_Author=items['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            Comment_published_dt = items['snippet']['topLevelComment']['snippet']['publishedAt']
                            )
                Comment_data.append(data)
    except:
        pass      

    return  Comment_data

#Get playlist information
def get_playlist_info(Channel_Id):
    Next_page_Token= None
    Playlist_data = []
    while True:
        request = youtube.playlists().list(
            part = "snippet,contentDetails",
            channelId=Channel_Id,
            maxResults=50,
            pageToken =Next_page_Token
        )
        response=request.execute()
        for item in response['items']:
            data = dict(Playlist_Id = item['id'],
                        Title= item['snippet']['title'],
                        Channel_Id = item['snippet']['channelId'],
                        Channel_Name =item['snippet']['channelTitle'],
                        Published_dt = item['snippet']['publishedAt'],
                        Video_Count=item['contentDetails']['itemCount'])
            Playlist_data.append(data)
        Next_page_Token = response.get('nextPageToken')
        if Next_page_Token  is None:
            break
    return Playlist_data

# Pymongo database
# Uploading to mongo DB
client =pymongo.MongoClient("mongodb+srv://dharani8890:sai1108@cluster0.o7fjb6h.mongodb.net/?retryWrites=true&w=majority")
db=client["Youtube_Data"]

# Sort the data in mongo DB
def Channel_details(channel_id):
    Ch_details=get_channel(channel_id)
    Vi_ids =get_videos_ids(channel_id)
    Vi_info=get_videos_info(Vi_ids)
    Com_info=get_comment_info(Vi_ids)
    Pi_details= get_playlist_info(channel_id)

    db1=db["channel_detail"]
    db1.insert_one({"Channel_informaion":Ch_details,"Playlist_information":Pi_details,
                     "Video_information": Vi_info,"Comment_information": Com_info })
    return "Upload completed scuccessfully"

# SQL database connection

def Channel_Table():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    )

    mycursor = mydb.cursor(buffered=True)

    ## Create Database in mysql

    # mycursor.execute("create database Youtube")



    drop_query= '''drop table if exists Youtube.channels1'''
    mycursor.execute(drop_query)
    mydb.commit()

    # Table creation for channels,playlist,vidoes,comments
    try:
        create_query='''CREATE TABLE if not exists Youtube.Channels1(Channel_Name varchar(100),
                                                            Subscriber bigint,
                                                            Total_Videos int,
                                                            Playlist_Id varchar(80),
                                                            Channnel_Id varchar(80) primary key,
                                                            Views bigint,
                                                            Channel_Description text)'''
        mycursor.execute(create_query)
        mydb.commit()
    except:
        print('Channels1 table already created')


    # Mongo data convert into table format
    Ch_list = []
    db =client["Youtube_Data"]
    Coll1 = db["channel_detail"]
    for ch_data in Coll1.find({},{"_id":0,"Channel_informaion":1}):
        Ch_list.append(ch_data["Channel_informaion"])
    df = pd.DataFrame(Ch_list)


    # insert data into SQL
    for index,row in df.iterrows():
        insert_query='''insert into Youtube.Channels1(Channel_Name,
                                            Subscriber,
                                            Total_Videos,
                                            Playlist_Id,
                                            Channnel_Id,
                                            Views,
                                            Channel_Description)
                                            values(%s,%s,%s,%s,%s,%s,%s)'''
        values=(row['Channel_Name'],
                row['Subscriber'],
                row['Total_Videos'],
                row['Playlist_Id'],
                row['Channel_Id'],
                row['Views'],
                row['Channel_Description'])
        try:
            mycursor.execute(insert_query,values)
            mydb.commit()
        except:
            print("Channels details already exist")

def Playlist_Table():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    )

    mycursor = mydb.cursor(buffered=True)

    ## Create Database in mysql

    # mycursor.execute("create database Youtube")



    drop_query= '''drop table if exists Youtube.Playlists1'''
    mycursor.execute(drop_query)
    mydb.commit()

    # Table creation for channels,playlist,vidoes,comments
    create_query='''CREATE TABLE if not exists Youtube.Playlists1(Playlist_Id varchar(100) primary key,
                                                        Title varchar(100),
                                                        Channel_Id varchar(100),
                                                        Channel_Name varchar(100),
                                                        Published_dt timestamp ,
                                                        Video_Count int)'''
    mycursor.execute(create_query)
    mydb.commit()

    # Mongo data convert into table format
    Pl_list = []
    db=client['Youtube_Data']
    Coll1 = db["channel_detail"]
    for Pl_data in Coll1.find({},{'_id':0,'Playlist_information':1}):
        for i in range(len(Pl_data['Playlist_information'])):
            Pl_list.append(Pl_data["Playlist_information"][i])
    df1=pd.DataFrame(Pl_list)

    # insert data into SQL
    for index,row in df1.iterrows():
        insert_query='''insert into Youtube.Playlists1(Playlist_Id,
                                            Title,
                                            Channel_Id,
                                            Channel_Name,
                                            Published_dt,
                                            Video_Count)
                                            values(%s,%s,%s,%s,%s,%s)'''
        values=(row['Playlist_Id'],
                row['Title'],
                row['Channel_Id'],
                row['Channel_Name'],
                row['Published_dt'],
                row['Video_Count'])

        mycursor.execute(insert_query,values)
        mydb.commit()

def Video_Table():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    )

    mycursor = mydb.cursor(buffered=True)

    ## Create Database in mysql

    # mycursor.execute("create database Youtube")



    drop_query= '''drop table if exists Youtube.Video'''
    mycursor.execute(drop_query)
    mydb.commit()

    # Table creation for channels,playlist,vidoes,comments
    create_query='''CREATE TABLE if not exists Youtube.Video(Channel_Name varchar(100),
                                                                Channel_Id varchar(100),
                                                                Video_Id varchar(30) primary key,
                                                                Title varchar(200),
                                                                Tags text,
                                                                Thumbnail varchar(200),
                                                                Description text,
                                                                publish_date timestamp,
                                                                Duration int,
                                                                Views bigint,
                                                                Likes bigint,
                                                                Comments int,
                                                                Favorite_count int,
                                                                Definition varchar(10))'''
    mycursor.execute(create_query)
    mydb.commit()

    # Mongo data convert into table format
    Vl_list = []
    db=client['Youtube_Data']
    Coll1 = db["channel_detail"]
    for Vl_data in Coll1.find({},{'_id':0,'Video_information':1}):
        for i in range(len(Vl_data['Video_information'])):
            Vl_list.append(Vl_data["Video_information"][i])
    df2=pd.DataFrame(Vl_list)


    mycursor = mydb.cursor(buffered=True)

    for index,row in df2.iterrows():
        insert_query='''insert into Youtube.Video(Channel_Name,
                                            Channel_Id,
                                            Video_Id,
                                            Title,
                                            Tags,
                                            Thumbnail,
                                            Description,
                                            publish_date,
                                            Duration,
                                            Views,
                                            Likes,
                                            Comments,
                                            Favorite_count,
                                            Definition)
                                            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        values=(row['Channel_Name'],
                row['Channel_Id'],
                row['Video_Id'],
                row['Title'],
                row['Tags'],
                row['Thumbnail'],
                row['Description'],
                row['publish_data'],
                row['Duration'],
                row['Views'],
                row['Likes'],
                row['Comments'],
                row['Favoritecount'],
                row['Definition'])

        mycursor.execute(insert_query,values)
        mydb.commit()


# SQL data connection
def Comments_Table():
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    )

    mycursor = mydb.cursor(buffered=True)

    ## Create Database in mysql

    # mycursor.execute("create database Youtube")



    drop_query= '''drop table if exists youtube.Comments'''
    mycursor.execute(drop_query)
    mydb.commit()

    # Table creation for channels,playlist,vidoes,comments
    create_query='''CREATE TABLE if not exists youtube.Comments(Comment_id varchar(100) primary key,
                                                        Video_id varchar(100),
                                                        Comment_Text text,
                                                        Comment_Author varchar(150),
                                                        Comment_published_dt timestamp
                                                        )'''

    mycursor.execute(create_query)
    mydb.commit()

    # Mongo data convert into table format
    Cl_list = []
    db=client['Youtube_Data']
    Coll1 = db["channel_detail"]
    for Cl_data in Coll1.find({},{'_id':0,'Comment_information':1}):
        for i in range(len(Cl_data['Comment_information'])):
            Cl_list.append(Cl_data["Comment_information"][i])
    df4=pd.DataFrame(Cl_list)

    # insert data into SQL
    for index,row in df4.iterrows():
        insert_query='''insert into Youtube.comments(Comment_id,
                                            Video_id,
                                            Comment_Text,
                                            Comment_Author,
                                            Comment_published_dt)
                                            values(%s,%s,%s,%s,%s)'''
        values=(row['Comment_id'],
                row['Video_id'],
                row['Comment_Text'],
                row['Comment_Author'],
                row['Comment_published_dt'])

        mycursor.execute(insert_query,values)
        mydb.commit()

def Tables():
    Channel_Table()
    Playlist_Table()
    Video_Table()
    Comments_Table()

    return "Tables created successfully"

def show_channels_table():
    Ch_list = []
    db =client["Youtube_Data"]
    Coll1 = db["channel_detail"]
    for ch_data in Coll1.find({},{"_id":0,"Channel_informaion":1}):
        Ch_list.append(ch_data["Channel_informaion"])
    df = st.dataframe(Ch_list)

    return df

def show_playlist_table():
    Pl_list = []
    db=client['Youtube_Data']
    Coll1 = db["channel_detail"]
    for Pl_data in Coll1.find({},{'_id':0,'Playlist_information':1}):
        for i in range(len(Pl_data['Playlist_information'])):
            Pl_list.append(Pl_data["Playlist_information"][i])
    df1=st.dataframe(Pl_list)

    return df1

def show_video_table():
    Vl_list = []
    db=client['Youtube_Data']
    Coll1 = db["channel_detail"]
    for Vl_data in Coll1.find({},{'_id':0,'Video_information':1}):
        for i in range(len(Vl_data['Video_information'])):
            Vl_list.append(Vl_data["Video_information"][i])
    df2=st.dataframe(Vl_list)

    return df2

def show_comments_table(): 
    Cl_list = []
    db=client['Youtube_Data']
    Coll1 = db["channel_detail"]
    for Cl_data in Coll1.find({},{'_id':0,'Comment_information':1}):
        for i in range(len(Cl_data['Comment_information'])):
            Cl_list.append(Cl_data["Comment_information"][i])
    df4=st.dataframe(Cl_list)

    return df4

# Streamlit part 


st.markdown("<h1 style='text-align: center; color: black;'>HARVESTING AND WAREHOUSING YOUTUBE INFORMATION </h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: grey;'>Analyze and inspect about specific channels </h2>", unsafe_allow_html=True)
st.markdown("------")
page_bg_img = '''
<style>
body {
background-image: url("https://images.app.goo.gl/GcjTR8khtyzo5BQ8A");
background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)
st.image("youtube.jpg",width=300)


st.sidebar.write('User Feedback')
#radio button 
rating = st.sidebar.radio('Are You satisfied with the outcome',('Yes','No'))
if rating == 'Yes':
    st.sidebar.success('Thank You for your response')
elif rating =='No':
    st.sidebar.info('Thank You for your response')

#selectbox
rating = st.sidebar.radio("Rate Your Experience ",
                     ['Very Satisfied', 'Satisfied', 'Somewhat Satisfied','Unsatisfied','Very Unsatisfied'])
st.sidebar.success(rating)
st.sidebar.write('Recently viewed')
#slider

mydb = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
)

mycursor = mydb.cursor(buffered=True)
query1 = '''Select Channel_Name as channelname from youtube.channels1'''
mycursor.execute(query1)
mydb.commit()
t1=mycursor.fetchall()
df = pd.DataFrame(t1,columns=['Channel Name'])
st.sidebar.write(df)




channel_id=st.text_input("ENTER CHANNEL ID :",placeholder="Paste the Channel ID") 

Click= st.button("Click to get ID info ", type="primary")

if Click:
    ch_id=[]
    db=client["Youtube_Data"]
    Coll1=db['channel_detail']
    for ch_data in Coll1.find({},{'_id':0,'Channel_informaion':1}):
        ch_id.append(ch_data['Channel_informaion']['Channel_Id'])
        
    if channel_id in ch_id:
        st.success("Given Channel ID Already Exist") 
    else:
        insert=Channel_details(channel_id)
        st.success(insert)
if st.button("Migrate to SQL", type="primary"):
    Table =Tables()
    st.success(Table)

show_table=st.selectbox("Choose the Information",["Channels","Playlist","videos","Comments"])

if show_table=="Channels":
    st.write('You selected Channel Information.')
    show_channels_table()
    

elif show_table=="Playlist":
    st.write('You selected Playlist Information.')
    show_playlist_table()
    

elif show_table=="videos":
    st.write('You selected Video Information.')
    show_video_table()
    

elif show_table=="Comments":
    st.write('You selected Comments Information.')
    show_comments_table()
    


# SQL Connection
mydb = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
)




mycursor = mydb.cursor(buffered=True)

Question =st.selectbox("Select Your Question",("1. All the videos and their corresponding channels",
                                               "2. Channels have the most number of videos",
                                               "3. Top 10 most viewed videos",
                                               "4. Comments were made on each video",
                                               "5. Videos have the highest number of likes",
                                               "6. Total number of likes and dislikes for each video",
                                               "7. Total number of views for each channel",
                                               "8. Published videos in the year 2022",
                                               "9. Average duration of all videos in each channel",
                                               "10.Videos have the highest number of comments"))


if Question == "1. All the videos and their corresponding channels":

    query1 = '''SELECT Title as videos,Channel_Name as channelname from youtube.video'''
    mycursor.execute(query1)
    mydb.commit()
    t1=mycursor.fetchall()
    df = pd.DataFrame(t1,columns=['Video Title','Channel Name'])
    st.write(df)


elif Question == "2. Channels have the most number of videos":
    
    query2= '''SELECT Channel_Name as channelname, Total_Videos as no_videos from youtube.channels1
            order by Total_Videos desc'''
    mycursor.execute(query2)
    mydb.commit()
    t2=mycursor.fetchall()
    df2 = pd.DataFrame(t2,columns=['channelname','No of Videos'])
    st.write(df2)

elif Question == "3. Top 10 most viewed videos":
    query3= '''SELECT Views as views, Channel_Name as channelname, Title as videostitle from youtube.video
            where Views is not null order by Views desc limit 10'''
    mycursor.execute(query3)
    mydb.commit()
    t3=mycursor.fetchall()
    df3 = pd.DataFrame(t3,columns=['Views','Channel Name','Video Title'])
    st.write(df3)

elif Question == "4. Comments were made on each video":
    query4= '''SELECT Comments as no_comments,Title as videotile from youtube.video where Comments is not null'''
    mycursor.execute(query4)
    mydb.commit()
    t4=mycursor.fetchall()
    df4 = pd.DataFrame(t4,columns=['No of comments','Video Title'])
    st.write(df4)

elif Question == "5. Videos have the highest number of likes":
    query5= '''SELECT Title as videotile, Channel_Name as channelname, Likes as likescount from youtube.video
            where Likes is not null order by Likes desc '''
    mycursor.execute(query5)
    mydb.commit()
    t5=mycursor.fetchall()
    df5 = pd.DataFrame(t5,columns=['Video Title','ChannelName','LikesCount'])
    st.write(df5)

elif Question == "6. Total number of likes and dislikes for each video":
    query6= '''SELECT Likes as likecount,Title as videotitle from youtube.video '''
    mycursor.execute(query6)
    mydb.commit()
    t6=mycursor.fetchall()
    df6 = pd.DataFrame(t6,columns=['LikesCount','Video Title'])
    st.write(df6)

elif Question == "7. Total number of views for each channel":
    query7= '''SELECT Views as viwes, Channel_Name as channelname from youtube.channels1  '''
    mycursor.execute(query7)
    mydb.commit()
    t7=mycursor.fetchall()
    df7 = pd.DataFrame(t7,columns=['Totalviews','ChannelName'])
    st.write(df7)

elif Question == "8. Published videos in the year 2022":
    query8= '''SELECT Title as video_title,publish_date as videorelease,Channel_Name as channelname from youtube.video
        where extract(year from publish_date) = 2022 '''
    mycursor.execute(query8)
    mydb.commit()
    t8=mycursor.fetchall()
    df8 = pd.DataFrame(t8,columns=['videotitle','publish_date','Channel_Name'])
    st.write(df8)
   
elif Question == "9. Average duration of all videos in each channel":
    query9= '''SELECT Channel_Name as Channelnam ,AVG(Duration) as avarageduration from youtube.video
        group by Channel_Name'''
    mycursor.execute(query9)
    mydb.commit()
    t9=mycursor.fetchall()
    df9 = pd.DataFrame(t9,columns=['Channel_Name','Avg_Duration'])
    st.write(df9)

    T9 = []
    for index,row in df9.iterrows():
        channel_Name = row['Channel_Name']
        average_duration=row['Avg_Duration']
        average_duration_str=str(average_duration)
        T9.append(dict(channeltitle = channel_Name,avgduration=average_duration_str))
    df1 = pd.DataFrame(T9)
    st.write(df1)
    
elif Question == "10.Videos have the highest number of comments":
    query10= '''SELECT Title as videotitle ,Channel_Name as Channelname,Comments as videocomments from youtube.video
        where comments is not null order by Comments desc'''
    mycursor.execute(query10)
    mydb.commit()
    t10=mycursor.fetchall()
    df10 = pd.DataFrame(t10,columns=['Video_Title','channel_name','Comments_Count'])
    st.write(df10)
    
