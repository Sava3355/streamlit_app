import streamlit as st
import pandas as pd
import plotly.express as px

#タイトルとcsvデータの取得
st.title('大学 文理別就職内定率')
df = pd.read_csv('FEH_00400402_260126184621.csv')

#使用方法の説明
with st.expander('使用方法について(クリックで展開します)'):
    st.subheader('1. スライダーの使用方法')
    st.write('画面左部にあります。見たい内容に合わせて項目を選択してください。')
    st.write('上部のトグルスイッチによって詳細表示が可能になります。')

    st.subheader('2. グラフ・図について')
    st.write('このアプリでは2種類の図（折れ線グラフ・散布図）を表示します。')
    st.write('スライダーの内容に合わせてそれぞれ変化します。')

    st.subheader('3. グラフの説明について')
    st.write('それぞれのグラフについて、下部に概要を記載しています。')

#スライダーの設定(項目の選択)
with st.sidebar:
    #詳細説明表示の有無(トグルスイッチ)
    active = st.toggle('詳細表示', value=True)
    #表章項目の選択
    category = st.selectbox('表章項目を選択してください',
                            df['表章項目'].unique())
    if active:
        st.write('内定率 もしくは 同期増減値を選択します')
    #学校区分の選択
    scoole_media = st.selectbox('学校区分を選択してください',
                         ['大学全体','国公立大学のみ','私立大学のみ'])
    if active:
        st.write('学校区分(大学全体・国公立・私立)を選択します')
    #csv表記と異なるので修正
    if scoole_media == '大学全体':
        scoole_media = '大学'
    elif scoole_media == '国公立大学のみ':
        scoole_media = '大学_うち国公立大学'
    elif scoole_media == '私立大学のみ':
        scoole_media = '大学_うち私立大学'
    #学部の選択
    faculty_media = st.selectbox('学部を選択してください',
                                 ['全体','文系','理系'])
    if faculty_media == '全体':
        value_col = '全体'
    elif faculty_media == '文系':
        value_col = '文系'
    elif faculty_media == '理系':
        value_col = '理系'
    if active:
        st.write('学部(文系・理系)を選択します')
    #生データの表示選択
    show_data = st.radio('データ(表)を表示しますか？',
    options=['表示しない', '表示する'],
    index=0
    )

#グラフの絞り込み
# sidebar の選択結果を使って絞り込み
#行を絞る(新しい変数に格納)
filtered_df = df.copy()

# 表章項目
filtered_df = filtered_df[
    filtered_df['表章項目'] == category
]

# 学校区分
filtered_df = filtered_df[
    filtered_df['学校区分'] == scoole_media
]

#年度による列を作成
filtered_df['年度'] = (
    filtered_df['時間軸(12月)']
    .str[:4]
    .astype(int)
)

#グラフ表示(折れ線グラフ)
st.subheader('折れ線グラフ')
#nan対策
filtered_df[value_col] = pd.to_numeric(
    filtered_df[value_col],
    errors='coerce'
)

y_min = filtered_df[value_col].astype(float).min()
y_max = filtered_df[value_col].astype(float).max()

fig = px.line(
    filtered_df.sort_values('年度'),
    x='年度',
    y=value_col,
    markers=True
)
fig.update_layout(
    xaxis=dict(
        title='年度(年12月)',
        range=[1996, 2025]
    ),
    yaxis=dict(
        title=faculty_media,
        range=[y_min, y_max]
    )
)
st.plotly_chart(fig, use_container_width=True)

#グラフ表示(散布図)
st.subheader('散布図')
# 文系・理系の利用
scatter_df = filtered_df[['年度', '文系', '理系']].copy()
#nan対策
scatter_df['文系'] = pd.to_numeric(scatter_df['文系'], errors='coerce')
scatter_df['理系'] = pd.to_numeric(scatter_df['理系'], errors='coerce')

scatter_long = scatter_df.melt(
    id_vars='年度',
    value_vars=['文系', '理系'],
    var_name='学部',
    value_name='値'
).dropna()
fig_scatter = px.scatter(
    scatter_long,
    x='年度',
    y='値',
    color='学部',
    labels={
        '年度': '年度',
        '値': category
    }
)

fig_scatter.update_layout(
    xaxis=dict(range=[1996, 2025])
)
st.plotly_chart(fig_scatter, use_container_width=True)

#概要の作成
col1, col2 = st.columns(2)

with col1:
    st.markdown('折れ線グラフの概要')
    summary_df = filtered_df[['年度', value_col]].dropna()
    max_row = summary_df.loc[summary_df[value_col].idxmax()]
    min_row = summary_df.loc[summary_df[value_col].idxmin()]
    st.metric(
        label='最大値',
        value=f"{max_row[value_col]:.2f}",
        help=f"{int(max_row['年度'])}年"
    )
    st.metric(
        label='最小値',
        value=f"{min_row[value_col]:.2f}",
        help=f"{int(min_row['年度'])}年"
    )
    max_year = int(max_row['年度'])
    min_year = int(min_row['年度'])
    st.write(f'{max_year}年が高く、')
    st.write(f'{min_year}年が低いことが確認できます。')

with col2:
    st.markdown('散布図の概要（文系・理系）')
    scatter_summary = scatter_long.groupby('学部')['値'].agg(['min', 'max', 'mean'])
    # 表示を見やすく整形
    st.dataframe(scatter_summary.style.format('{:.2f}'))

#元データ表示の有無
if show_data == '表示する':
    st.subheader('データ(表)')
    st.dataframe(filtered_df)
