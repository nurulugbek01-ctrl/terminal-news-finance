import yfinance as yf
import pandas as pd
import pandas_ta as ta

def analyze_ticker(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        # Запрашиваем данные за 1 год для устойчивого расчета индикаторов
        df = stock.history(period="1y")
        
        if df.empty or len(df) < 50:
            return None, f"Недостаточно данных по тикеру '{ticker_symbol}'. Проверьте правильность написания."

        # Вычисление технических индикаторов
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        df['EMA_50'] = ta.ema(df['Close'], length=50)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        macd_df = ta.macd(df['Close'])
        if macd_df is not None and not macd_df.empty:
            df['MACD'] = macd_df.iloc[:, 0]
            df['MACD_SIGNAL'] = macd_df.iloc[:, 1]
        else:
            df['MACD'] = 0
            df['MACD_SIGNAL'] = 0

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        score = 0
        reasons = []

        # 1. Анализ тренда (EMA)
        if latest['Close'] > latest['EMA_20'] > latest['EMA_50']:
            score += 35
            reasons.append("Сильный бычий тренд: Цена > EMA20 > EMA50")
        elif latest['Close'] > latest['EMA_20']:
            score += 20
            reasons.append("Умеренный бычий тренд: Цена выше EMA20")
        else:
            reasons.append("Медвежий тренд: Цена ниже ключевых скользящих средних")

        # 2. Индикатор RSI
        rsi_val = latest['RSI']
        if pd.isna(rsi_val):
            rsi_val = 50
        
        if rsi_val < 30:
            score += 25
            reasons.append(f"RSI в зоне перепроданности ({rsi_val:.1f} < 30) — Зона покупок")
        elif 40 <= rsi_val <= 60:
            score += 15
            reasons.append(f"RSI в нейтральной зоне ({rsi_val:.1f})")
        elif rsi_val > 70:
            reasons.append(f"RSI в зоне перекупленности ({rsi_val:.1f} > 70) — Риск коррекции")

        # 3. Индикатор MACD
        if latest['MACD'] > latest['MACD_SIGNAL']:
            score += 25
            reasons.append("MACD показывает бычий импульс (линия выше сигнала)")
            if prev['MACD'] <= prev['MACD_SIGNAL']:
                score += 15
                reasons.append("🔥 Свежее бычье пересечение MACD!")

        # 4. Анализ объема торгов
        avg_vol = df['Volume'].tail(20).mean()
        if latest['Volume'] > avg_vol * 1.2:
            score += 10
            reasons.append("Повышенный объем торгов (Подтверждение интереса покупателей)")

        score = min(score, 100)
        
        result = {
            'price': round(float(latest['Close']), 2),
            'rsi': round(float(rsi_val), 1),
            'score': score,
            'reasons': reasons,
            'df': df
        }
        return result, None

    except Exception as e:
        return None, f"Ошибка при загрузке данных: {str(e)}"