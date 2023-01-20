import requests
from time import sleep
from utils import send_to_assembly
from utils import dubbing
from utils import create_zip
import streamlit as st

with st.sidebar:
    tk_assembly = st.text_input("assemblyai.com - توکنی که از سایت اسمبلی اِی آی دات کام دریافت کردید وارد کنید", type="password")
    tk_api_audio = st.text_input("api.audio - توکنی که از سایت اِی پی آی دات آدیو دریافت کردید وارد کنید", type="password")
    speed = st.slider("سرعت صدا را انتخاب کنید", 50, 120, 80)
    voice = st.selectbox("کدام صدا را می خواهید؟", ("liam", "sonia", "aria", "ryan"))


st.title(
    """ دوبلور
اولین سامانه دوبله اتوماتیک فیلم توسط هوش مصنوعی
"""
)

p_name = st.text_input("یک نام برای این پروژه درج کنید")

uploaded_file = st.file_uploader("یک ویدیو را انتخاب کنید")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    
    with open(f'{uploaded_file.name}', 'wb') as wfile:
      wfile.write(bytes_data)

    st.video(bytes_data)

if st.button("دوبله"):
    if not tk_assembly or not tk_api_audio :
        st.error('هر دو توکن باید ارائه شوند')
        st.stop()
    with st.spinner("در انتظار تولید زیرنویس..."):
        headers, sub_endpoint = send_to_assembly(bytes_data, auth=tk_assembly)
        polling_response = requests.get(sub_endpoint, headers=headers)

        while polling_response.json()["status"] != "completed":
            sleep(5)
            print("پردازش رونوشت ...")
            try:
                polling_response = requests.get(sub_endpoint, headers=headers)
            except:
                print("رونویسی ناموفق")

    st.success("زیرنویس ایجاد شد، اکنون ویدیو شما را دوبله می کنم")
    response_srt = requests.get(f"{sub_endpoint}/srt", headers=headers)

    subtitle = response_srt.text.split("\n")

    with open(f"{p_name}.srt", "w") as _file:
        _file.write(response_srt.text)

    with st.spinner("منتظر دوبله..."):
        final_video, audio_file = dubbing(
            p_name,
            subtitle,
            uploaded_file.name,
            speed=speed,
            voice=voice,
            auth=tk_api_audio,
        )

    video_file = open(f"{final_video}", "rb")
    video_bytes = video_file.read()
    st.success("ویدیوی شما آماده است!")
    st.video(video_bytes)

    create_zip(p_name, f'{p_name}.srt',
                              final_video, audio_file)
 
    st.write("برای دانلود فایل های تولید شده اینجا کلیک کنید")
    with open(f"{p_name}.zip", "rb") as fp:
        btn = st.download_button(
            label="Download ZIP",
            data=fp,
            file_name="mydubbedvideo.zip",
            mime="application/zip"
        )
st.write("نسخه استریملیت:", st.__version__)
