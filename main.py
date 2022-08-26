# ライブラリーのインストール
from cProfile import label
from email.policy import default
from re import L
import thinker
import turtle
from turtle import distance, width
import streamlit as st 
import pytz
import folium
from streamlit_folium import folium_static

# webデザインを作成する
text = st.subheader('ツイートマッピングアプリケーション(Tweet Mapping Application)')

# webアプリケーションの説明部分
text  = ''' 

　こちらのサイトでは、Twitter上で過去数日間でツイートされたツイートを位置情報(場所)を
指定することで地図上にマッピングし、可視化することが出来るサイトとなっております。
　マーケティング活動などでどのようなツイートがどのような場所で発生しているのかを調べたい時に
活用していただきたいと考えております(想定)。まだ、具体的に「コレに使う!」というのが決まっていないので、
色々遊んでみてください!
　左の項目に調べたい条件を全て入力した上で、ボタンを押していただくことで検索することが可能と
なっております。
　また、本サイトでツイートを収集する際には、以下の条件にお気を付けてご利用ください。
1. 本サイトでツイートを収集する際には、一度に100件を以上の収集を行わないようにご注意ください。
2.プログラムの仕様上、指定したツイート数のツイートが集まらない場合や同じツイートが収集されてしまう
場合がございますが、ご了承ください。
　以上が注意点となっております。では、本サイトのご利用をお楽しみください!
'''

st.text(text)

# 検索条件を入力するフォームを作成する(UI:User Interface)

search_key = st.sidebar.text_input('検索したいキーワードを入力してください。\
                                    (＊1文字指定推奨)')

search_num = st.sidebar.number_input('調べたいツイート数を指定してください', min_value=1, max_value=99)
st.sidebar.markdown(f'{search_num}個のツイート')

location = st.sidebar.text_input('場所を指定してください\
                                 (＊指定した場所から半径5km以内のツイートを調べます。)')
st.sidebar.markdown(f'{location}')

st.sidebar.markdown('***全ての項目を入力**してから、**「検索」ボタン**を押してください。')

# 収集したツイートデータの座標を出力する関数
def search_location(position):
    # 収集したツイートデータの座標を出力する関数
    import geocoder
    # 緯度、経度の指定
    ret = geocoder.osm(position, timeout=5.0)
    geo_date = ret.latlng
    return geo_date

### 以下は、検索したlocationとradius(半径)をマップに表示
try:
    result = st.sidebar.button(label='検索')
    if result:
        with st.spinner('検索中です...。少々、お待ちください。'):
            import tweepy
            # Twitter APIの承認
            api_key = 'h5MEfHXurvG4bMc76bB0j4I3i'
            api_secret = '0Rcnxfu2jupcwAu8vGUzI1CtyyzHnVJvRqThefmg7uLguWlG7A'
            access_key = '866183516635111425-UJFpwBeyhxINzAERxOhJirVoFgQUTSC'
            access_secret = 'oNUWoXgwdoCnUkB8xbEk0AoNxawFot0Cv7WYee57hwXhd'

            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_key, access_secret)
            api = tweepy.API(auth)

            def change_time_JST(u_time):  
                from datetime import datetime,timezone
                import pytz
                import os
                import time
                import folium
                #イギリスのtimezoneを設定するために再定義する
                utc_time = datetime(u_time.year, u_time.month,u_time.day, \
                u_time.hour,u_time.minute,u_time.second, tzinfo=timezone.utc)
                #タイムゾーンを日本時刻に変換
                jst_time = utc_time.astimezone(pytz.timezone("Asia/Tokyo"))
                # 文字列で返す
                str_time = jst_time.strftime("%Y-%m-%d_%H:%M:%S")
                return str_time

            def search_tweet_location(box):
                # 位置情報の取得と加工（四角形で与えられるので中心座標を計算）
                box = tweet.place.bounding_box.coordinates
                lat = (box[0][0][1] + box[0][1][1] + box[0][2][1] + box[0][3][1]) / 4
                lon = (box[0][0][0] + box[0][1][0] + box[0][2][0] + box[0][3][0]) / 4
                user_location_data = lat, lon
                return user_location_data

            lat = search_location(location)[0]
            lon = search_location(location)[1]
            #検索条件を元にツイートを抽出（labelはTwitterのDeveloper portalで設定可能）
            search = f"{search_key} point_radius:[{lon} {lat} 5km]"
            tweets = tweepy.Cursor(api.search_30_day, label='30DaysLabel', query=search,).items(search_num)
            # 先ほど収集したツイートを一度リストにする
            tweets = list(tweets)
            tweet_data = []
            for tweet in tweets:
                # ごくまれに位置情報の入れ物のみあり、中身が無い場合がある。それを回避する。
                if (tweet.place.bounding_box == None): 
                    continue
                # Coordinate関数を呼び出し、ツイートされた場所を指定する
                user_location_date = search_tweet_location(tweet.place.bounding_box.coordinates)
                #change_time_JST関数を呼び出し、ツイート時刻とユーザのアカウント作成時刻を日本時刻にする
                tweet_time = change_time_JST(tweet.created_at)
                tweet_data.append([tweet_time, tweet.user.name, tweet.text, user_location_date])
            
            # 抽出したツイートのツイート時間を抽出
            user_tweet_time = [tweet_data[i][0] for i in range(search_num)]
            # 抽出したツイートのユーザー名を抽出
            tweet_name = [tweet_data[i][1] for i in range(search_num)]
            # 抽出したツイートのツイート内容を抽出
            tweet_contents = [tweet_data[i][2] for i in range(search_num)]
            # 抽出したツイート,あるいはユーザーがいる位置情報の座標を抽出
            lat_list = [tweet_data[i][3][0] for i in range(search_num)]
            lon_list = [tweet_data[i][3][1] for i in range(search_num)]

            # データ格納（名前，緯度経度）
            import pandas as pd
            df = pd.DataFrame({
                'time':user_tweet_time,
                'username': tweet_name,
                'contents': tweet_contents,
                'latitude': lat_list,
                'longtude': lon_list,
            })
            # 地図を生成する(検索した場所を中心としている)
            m = folium.Map(location=[lat, lon], zoom_start=15)
            #マーカープロット
            for i, row in df.iterrows():
                folium.Marker(
                    location=[row['latitude'], row['longtude']],
                    popup= row['time']+\
                           row['username']+\
                            row['contents'],
                    icon=folium.Icon(color='lightblue', icon='cloud')
                ).add_to(m) 
            st.success('終了しました!')
            # 地図を生成する
            folium_static(m) 
        
    elif location:
        # check_str関数:関数にpositionが入力されたら、マップが表示されるプログラム
        def PositionMapping(location):
            import folium
            from streamlit_folium import folium_static
            import geocoder
            lat = search_location(location)[0]
            lon = search_location(location)[1]

            # 地図生成(検索された地域に赤ピンを立てる)
            m = folium.Map(location=[lat, lon], zoom_start=15)
            folium.Marker(
                location=[lat, lon],
                popup=location,
                icon=folium.Icon(color='red', icon='home')
            ).add_to(m)
            folium_static(m)
        PositionMapping(location)
    else:
        st.write('')

except AttributeError:
    st.markdown('位置情報を持つツイートが見つかりませんでした。')

