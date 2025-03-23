import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from yfinance_access import get_stock_data
from plotting import plot_stock_price


# Page Config
st.set_page_config(
    page_title="Finanzapp",
    page_icon=":coin:"
)


# Überblick aktueller Stand
st.title("Überblick Fortschritt")

# st.write("vorvorletzte Session: Safe Write to db mit überschreibeoption bei doppelten primary keys, db handling aufgesetzt")
st.write("Figma Brainstorming der Inhalte, erste Ideen für die Struktur: https://www.figma.com/board/YyKbD6NoNFZ592nX0QGzJZ/Planung-Finanzapp?node-id=0-1&t=8YojrFTIxTDvcbyn-1")
# st.write("letzte Session: Tabelle 'Konten' erstellt und Seite 'Vermögen' angefangen")
st.write("letzte Sessions: Tabelle 'Transaktionen' sowie 'Kontostände' erstellt, diese untereinender und mit 'Konten' verknüpfen und Seite 'Transaktionan' anfangen")
st.write("Nächste Sessions: Erstelle Pflegemaske für sinnvollen, hierarchischen kategorien-Katalog, speichere ihn als Tabelle. Passe Transaktionen an um die tabelle zu nutzen")


st.header("Ausblick/To-Dos")
st.write("1. Transaktionen anpassen, um Kategorien-Katalog zu nutzen")
st.write("2. Auswertung der Transaktionen nach Kategorien, geile Charts dafür mit zeitlichem Verlauf bauen")
st.write("3. Kontostände im zeitlichen Verlauf darstellen")


# #Set title for Streamlit app
# st.title("Hourly Prices of iShares Core MSCI World USD (Acc) ETF in EUR")

# show_missing_data = st.toggle("Show Missing Data", value=True)

# code = "IWDA.L"
# code = "TGT"
# data = get_stock_data(code, "1y", "1d")

# # print(data)

# # Display the Plotly figure in Streamlit
# fig = plot_stock_price(data, interval='d', show_missing_data=show_missing_data)
# st.plotly_chart(fig, use_container_width=True)

# # Create a Plotly line chart
# fig = go.Figure()
# fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name="Price in EUR"))

# # Set chart title and labels
# fig.update_layout(
#     title="Hourly Prices of Core MSCI World USD (Acc) ETF in EUR",
#     xaxis_title="Time",
#     yaxis_title="Price (EUR)",
#     yaxis=dict(automargin=True)  # Auto-adjust y-axis limits based on data
# )

# # Display the Plotly figure in Streamlit
# st.plotly_chart(fig, use_container_width=True)

# tech = yf.Sector('technology')
# software = yf.Industry('software-infrastructure')

# st.write(tech.overview)
# st.write(tech.industries)
# st.write(software.top_companies)


# st.title(':chart_with_upwards_trend: Aktien-App')
# st.header(':construction_worker: Hier entsteht eine einfache Aktien-App, die die Kursentwicklung von Aktien visualisiert')
# st.write(':globe_with_meridians: Aktuelle API von Alpha Vantage: https://www.alphavantage.co/documentation/')
# st.write(':warning: Problem: Nur 25 API-Calls pro Tag möglich')
# st.write(':bulb: Lösung: Daten von ausgewählten Aktien in CSV-Datei speichern und bei Bedarf auslesen, oder andere API nutzen, z.B. Intrinio: https://docs.intrinio.com/documentation/api_v2/getting_started ?')