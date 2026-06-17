import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium


CSV_PATH = "weekendpopular.csv"
MAP_CENTER = [37.5665, 126.9780]


def load_station_data(path: str) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            df = pd.read_csv(path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("CSV 파일 인코딩을 읽을 수 없습니다.")

    df.columns = ["station_name", "latitude", "longitude", "usage"]
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["usage"] = pd.to_numeric(df["usage"], errors="coerce")

    return df.dropna(subset=["latitude", "longitude", "usage"])


def usage_color(usage: float) -> str:
    if usage >= 5000:
        return "red"
    if usage >= 3000:
        return "orange"
    return "blue"


st.set_page_config(page_title="따릉이 대여소 지도", layout="wide")
st.title("따릉이 주말 인기 대여소 지도")

stations = load_station_data(CSV_PATH)

m = folium.Map(location=MAP_CENTER, zoom_start=12)

for _, station in stations.iterrows():
    color = usage_color(station["usage"])
    folium.CircleMarker(
        location=[station["latitude"], station["longitude"]],
        radius=max(6, station["usage"] / 800),
        popup=(
            f"<b>{station['station_name']}</b><br>"
            f"주말 이용량: {int(station['usage']):,}"
        ),
        tooltip=station["station_name"],
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
    ).add_to(m)

st.caption(f"총 {len(stations)}개 대여소를 표시했습니다.")
st_folium(m, width=1100, height=600)

with st.expander("데이터 보기"):
    st.dataframe(
        stations.rename(
            columns={
                "station_name": "대여소명",
                "latitude": "위도",
                "longitude": "경도",
                "usage": "주말 이용량",
            }
        ),
        width="stretch",
        hide_index=True,
    )
