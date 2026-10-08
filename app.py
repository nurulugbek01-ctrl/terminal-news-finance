import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from database.db_manager import init_db, get_all_stocks
from analysis.scorer import analyze_ticker

st.set_page_config(page_title="Terminal News Finance", layout="wide", page_icon="📈")

# Инициализация БД
init_db()

st.title("📈 Terminal News Finance")
st.caption("Халяль скрининг и профессиональный технический анализ акций US Market")

# Получение данных из БД
stocks = get_all_stocks()
stocks_dict = {s[0]: {"name": s[1], "halal": s[2], "notes": s[3]} for s in stocks}

# Боковое меню
st.sidebar.header("🔍 Поиск и Настройки")
ticker_input = st.sidebar.text_input("Введите тикер акции:", value="HIMS").upper().strip()

st.sidebar.markdown("---")
st.sidebar.subheader("📋 Выбор из базы")
selected_preset = st.sidebar.selectbox("Популярные тикеры:", [""] + list(stocks_dict.keys()))

ticker = selected_preset if selected_preset else ticker_input

col1, col2 = st.columns([1, 2.2])

with col1:
    st.subheader("📋 Информация о компании")
    st.write(f"**Тикер:** `{ticker}`")
    
    if ticker in stocks_dict:
        status = stocks_dict[ticker]["halal"]
        st.write(f"**Компания:** {stocks_dict[ticker]['name']}")
        
        if status == "Verified":
            st.success(f"Статус Халяль: ✅ **{status}**")
        elif status == "Watch":
            st.warning(f"Статус Халяль: ⚠️ **{status}**")
        else:
            st.info(f"Статус Халяль: ℹ️ **{status}**")
        st.caption(f"**Заметка:** {stocks_dict[ticker]['notes']}")
    else:
        st.info("Статус Халяль: Требуется индивидуальная проверка финансовой отчетности")

    st.markdown("---")
    if st.button("🚀 Запустить полный анализ", use_container_width=True):
        with st.spinner(f"Загрузка биржевых данных для {ticker}..."):
            result, error = analyze_ticker(ticker)
            if error:
                st.error(error)
                if 'analysis' in st.session_state:
                    del st.session_state['analysis']
            else:
                st.session_state['analysis'] = result
                st.session_state['current_ticker'] = ticker

with col2:
    st.subheader("📊 Технический разбор и Setup Score")
    
    if 'analysis' in st.session_state and st.session_state.get('current_ticker') == ticker:
        res = st.session_state['analysis']
        score = res['score']
        
        # Метрики
        m1, m2, m3 = st.columns(3)
        m1.metric("Текущая цена", f"${res['price']}")
        m2.metric("RSI (14)", res['rsi'])
        m3.metric("Setup Score", f"{score} / 100")
        
        # Прогресс бар и вердикт
        st.progress(score / 100)
        if score >= 70:
            st.success("🔥 **Сильный бычий сетап (Strong Buy)**")
        elif score >= 40:
            st.warning("⚖️ **Нейтральный / Накопление (Hold / Watch)**")
        else:
            st.error("❄️ **Слабый сигнал / Медвежий тренд (Avoid / Sell)**")

        st.markdown("**Факторы сигнала:**")
        for r in res['reasons']:
            st.write(f"• {r}")
            
        # Интерактивный свечной график + Объем
        df = res['df']
        fig = make_subplots(
            rows=2, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.03, 
            subplot_titles=(f'График цены {ticker}', 'Объем торгов'),
            row_heights=[0.7, 0.3]
        )

        # Свечи и EMA
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Цена"
        ), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name="EMA 20", line=dict(color='orange', width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], name="EMA 50", line=dict(color='cyan', width=1.5)), row=1, col=1)

        # Гистограмма объемов
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color='purple'), row=2, col=1)

        fig.update_layout(template="plotly_dark", height=520, showlegend=True, margin=dict(l=10, r=10, t=30, b=10))
        fig.update_xaxes(rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Нажмите кнопку **'🚀 Запустить полный анализ'** слева для получения отчета.")