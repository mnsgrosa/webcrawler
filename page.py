import streamlit as st
import datetime
import httpx

st.markdown('# Dashboard de promocoes scrapadas')

st.markdown('## Promocoes gerais')
with httpx.Client() as client:
    response = client.get('http://api:9000/get/all')
    response.raise_for_status()

st.markdown('## Promocoes gerais')
data = response.json().get('data', [])
st.dataframe(data)

col1, col2 = st.columns(2)

with col1:
    st.markdown('## Promocoes playstation')
    with httpx.Client() as client:
        response = client.get('http://api:9000/get/platform', params = {'platform': 'playstation'})
        response.raise_for_status()
    data = response.json().get('items', [])
    st.dataframe(data)

with col2:
    st.markdown('## Promocoes xbox')
    with httpx.Client() as client:
        response = client.get('http://api:9000/get/platform', params = {'platform': 'xbox'})
        response.raise_for_status()
    data = response.json().get('items', [])
    st.dataframe(data)

st.markdown('## Promocoes em datas especificas e plataformas especificas')
date = st.date_input('Selecione uma data',
                min_value = datetime.date(2025, 8, 13),
                max_value = datetime.datetime.now().date())

platform = st.selectbox('Selecione uma plataforma', ['playstation', 'xbox'])

with httpx.Client() as client:
    response = client.get('http://api:9000/get/platform', params = {'platform':platform, 'date':date.isoformat()})
    response.raise_for_status()
data = response.json().get('items', [])
st.dataframe(data)