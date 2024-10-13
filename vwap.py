import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import time

# Título de la aplicación
st.title("VWAP en Tiempo Real")

# Dividir los controles en 3 columnas
col1, col2, col3 = st.columns(3)

# Entrada para el ticker (activo a monitorear)
with col1:
    ticker = st.text_input("Ticker del activo:", "GGAL")
    
    # Parámetro para la cantidad de registros a graficar (debajo del ticker)
    num_records = st.number_input("Cantidad de registros a graficar:", min_value=1, value=100)

# Parámetros para las ventanas deslizantes
with col2:
    window1 = st.number_input("Ventana 1 (periodos):", min_value=1, value=14)
    window2 = st.number_input("Ventana 2 (periodos):", min_value=1, value=26)
    window3 = st.number_input("Ventana 3 (periodos):", min_value=1, value=50)

# Parámetros para seleccionar el periodo y el intervalo
with col3:
    period = st.selectbox(
        "Periodo de datos:",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
    )

    interval = st.selectbox(
        "Intervalo de datos:",
        ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1d", "5d", "1wk", "1mo", "3mo"]
    )

# Parámetro para la actualización automática
update_interval = st.slider("Intervalo de actualización (segundos):", min_value=10, max_value=600, value=60)

# Loop para actualizar la aplicación en tiempo real
while True:
    # Descargar datos basados en el periodo y el intervalo seleccionados
    data = yf.download(ticker, period=period, interval=interval, progress=False)

    # Verificar que el número de registros no supere el máximo disponible
    max_records = len(data)
    if num_records > max_records:
        num_records = max_records

    # Reducir los datos a la cantidad solicitada
    data = data.tail(num_records)

    # Calcular VWAP con ventanas deslizantes
    data['Price * Volume'] = data['Adj Close'] * data['Volume']

    # VWAP1
    data['Rolling Price * Volume1'] = data['Price * Volume'].rolling(window=window1).sum()
    data['Rolling Volume1'] = data['Volume'].rolling(window=window1).sum()
    data['VWAP1'] = data['Rolling Price * Volume1'] / data['Rolling Volume1']

    # VWAP2
    data['Rolling Price * Volume2'] = data['Price * Volume'].rolling(window=window2).sum()
    data['Rolling Volume2'] = data['Volume'].rolling(window=window2).sum()
    data['VWAP2'] = data['Rolling Price * Volume2'] / data['Rolling Volume2']

    # VWAP3
    data['Rolling Price * Volume3'] = data['Price * Volume'].rolling(window=window3).sum()
    data['Rolling Volume3'] = data['Volume'].rolling(window=window3).sum()
    data['VWAP3'] = data['Rolling Price * Volume3'] / data['Rolling Volume3']

    # Crear el gráfico interactivo usando Plotly
    fig = go.Figure()

    # Añadir el precio ajustado de cierre
    fig.add_trace(go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name='Precio', line=dict(color='black')))

    # Añadir las líneas VWAP
    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP1'], mode='lines', name=f'VWAP ({window1} periodos)', line=dict(color='blue', dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP2'], mode='lines', name=f'VWAP ({window2} periodos)', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=data.index, y=data['VWAP3'], mode='lines', name=f'VWAP ({window3} periodos)', line=dict(color='green', dash='dash')))

    # Configurar el layout del gráfico con la leyenda alineada a la izquierda y sobre el gráfico
    fig.update_layout(
        title=f'VWAP para {ticker} en Intervalo de {interval}',
        xaxis_title='Fecha',
        yaxis_title='Precio',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        hovermode='x unified'
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Mostrar las señales de si el precio está por encima o por debajo de los VWAPs
    st.subheader("Señales de VWAP:")
    col_sig1, col_sig2, col_sig3 = st.columns(3)
    
    with col_sig1:
        try:
            if data['Adj Close'].iloc[-1] > data['VWAP1'].iloc[-1]:
                st.success(f"Precio por encima de VWAP ({window1} periodos)")
            else:
                st.error(f"Precio por debajo de VWAP ({window1} periodos)")
        except:
            pass

    with col_sig2:
        try:
            if data['Adj Close'].iloc[-1] > data['VWAP2'].iloc[-1]:
                st.success(f"Precio por encima de VWAP ({window2} periodos)")
            else:
                st.error(f"Precio por debajo de VWAP ({window2} periodos)")
        except:
            pass
            
    with col_sig3:
        try:
            if data['Adj Close'].iloc[-1] > data['VWAP3'].iloc[-1]:
                st.success(f"Precio por encima de VWAP ({window3} periodos)")
            else:
                st.error(f"Precio por debajo de VWAP ({window3} periodos)")
        except:
            pass

    # Esperar el tiempo especificado antes de actualizar
    time.sleep(update_interval)

    # Refrescar la aplicación
    st.rerun()
