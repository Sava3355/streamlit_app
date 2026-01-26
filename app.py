import streamlit as st
import pandas as pd

st.title('大学 文理別就職内定率')
df = pd.read_csv('FEH_00400402_260126111959.csv')

with st.sidebar:
    year = st.multiselect('年を選択してください。',
                          df['時間軸(12月)'].unique())


st.dataframe(df,width=800, height=220)