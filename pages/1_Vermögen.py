import streamlit as st
import pandas as pd
from db_handler import df_to_db, df_from_db, df_to_db_and_replace
import plotting as plotting


# TODO: Funktion, um Kontostände manuell zu ändern (ohne Transaktion)

### Page Config ###
st.set_page_config(page_title="Vermögen", page_icon=":money_with_wings:")


### Datenbank ###
# lade bestehende Konten in session state
st.session_state["df_konten"] = df_from_db("konten")
st.session_state["existierende_konten"] = st.session_state["df_konten"]["name"].tolist()
st.session_state["konten_dict"] = dict(zip(st.session_state["df_konten"]["konto_id"], st.session_state["df_konten"]["name"]))


### Funktionen ###
# funktion um aktuell existierende kontonamen zu bekommen
def existierende_kontonamen():
    return st.session_state["existierende_konten"]

# dialog zum löschen eines kontos
@st.dialog("Konto löschen?")
def delete(konto_id):
    konto_name = st.session_state["df_konten"][st.session_state["df_konten"]["konto_id"] == konto_id]["name"].values[0]
    st.write(f":warning: Bist du sicher, dass du das Konto {konto_name} löschen willst? Dadurch werden alle zugehörigen Transaktionen und Kontostände ebenfalls gelöscht. :warning:")
    if st.button("Bestätigen"):
        try:
            konten = df_from_db("konten")
            konten = konten[konten["konto_id"] != konto_id]
            df_to_db_and_replace(konten, "konten")
            st.success("Konto erfolgreich gelöscht")
            st.session_state["df_konten"] = df_from_db("konten")
        except Exception as e:
            st.error(f"Fehler beim Löschen des Kontos: {e}")

def neues_konto():
    # add account to database
    st.header("Konto hinzufügen")
    form = st.form(key="add_account")
    name = form.text_input("Name")
    bank = form.text_input("Bank")
    typ = form.selectbox("Typ", ["Girokonto", "Sparkonto", "Depot", "Gebundenes Kapital", "Externes Konto"])
    balance = form.number_input("Kontostand")
    waehrung = form.selectbox("Währung", ["EUR", "USD", "CHF", "NOK"])
    iban = form.text_input("IBAN")
    eigenes_konto = form.checkbox("Eigenes Konto", value=True)
    submit = form.form_submit_button("Konto hinzufügen")

    if submit:
        if name in existierende_kontonamen():
            st.error("Kontoname bereits vorhanden")
        else:
            try:
                df = pd.DataFrame({
                    "erstellungsdatum": [pd.Timestamp.now()],
                    "name": [name],
                    "bank": [bank],
                    "typ": [typ],
                    "kontostand": [balance],
                    "waehrung": [waehrung],
                    "iban": [iban],
                    "eigenes_konto": [eigenes_konto]
                })
                df_to_db(df, "konten", safe_write=False, overwrite_db_in_conflict=True)

                st.success("Konto erfolgreich hinzugefügt")
                revert = st.button("Rückgängig", key="revert")
                st.session_state["df_konten"] = df_from_db("konten")

            except Exception as e:
                st.error(f"Fehler beim Hinzufügen des Kontos: {e}")

    if "revert" in st.session_state:
        if st.session_state["revert"]:
            delete(name)
            st.session_state["df_konten"] = df_from_db("konten")

def konto_loeschen():
    # delete account from database
    st.header("Konto löschen")
    form = st.form(key="delete_account")
    konto_id = form.selectbox("Konto", st.session_state["konten_dict"].keys(), format_func=lambda x: st.session_state["konten_dict"][x])
    submit = form.form_submit_button("Konto löschen")

    if submit:
        delete(konto_id)

def kontostand_manuell_aendern():
    # Kontostand manuell ändern
    st.header("Kontostand ändern")
    form = st.form(key="change_balance")
    konto_id = form.selectbox("Konto", st.session_state["konten_dict"].keys(), format_func=lambda x: st.session_state["konten_dict"][x])
    new_balance = form.number_input("Neuer Kontostand")
    submit = form.form_submit_button("Kontostand ändern")

    if submit:
        try:
            # Tabelle Konten anpassen (Eintrag ändern)
            konten= df_from_db("konten")
            konten.loc[konten["konto_id"] == konto_id, "kontostand"] = new_balance
            df_to_db_and_replace(konten, "konten")

            # Tabelle Kontostände anpassen (Eintrag hinzufügen)
            row = pd.DataFrame({
                "konto_id": [konto_id],
                "datum": [pd.Timestamp.now()],
                "kontostand": [new_balance],
                "waehrung": konten.loc[konten["konto_id"] == konto_id, "waehrung"].values[0]
            })
            df_to_db(row, "kontostaende", safe_write=False)

            st.success("Kontostand erfolgreich geändert")

        except Exception as e:
            st.error(f"Fehler beim Ändern des Kontostands: {e}")

def kontostaende_anzeigen():
    # Kontoübersicht
    st.header("Kontenübersicht")
    df_eigene_konten = st.session_state["df_konten"][st.session_state["df_konten"]["eigenes_konto"] == True]

    st.subheader(f"Gesamtes Vermögen: {df_eigene_konten['kontostand'].sum():.2f} €")
    
    # Pie charts
    # Vermögen nach Kontoart
    fig = plotting.pie_chart(df_eigene_konten, "typ", "kontostand", "Vermögen nach Kontoart")
    st.plotly_chart(fig)


    # Vermögen nach Bank
    fig = plotting.pie_chart(df_eigene_konten, "bank", "kontostand", "Vermögen nach Bank")
    st.plotly_chart(fig)


    # Vermögen nach Konto
    fig = plotting.pie_chart(df_eigene_konten, "name", "kontostand", "Vermögen nach Konten")
    st.plotly_chart(fig)

### UI ###
st.title("Vermögensübersicht")

# Kontostände anzeigen
kontostaende_anzeigen()

st.title("Kontenverwaltung")
cols = st.columns(2)

with cols[0]:
    # Konto hinzufügen
    neues_konto()

with cols[1]:
    # Kontostand manuell ändern
    kontostand_manuell_aendern()

    # Konto löschen
    konto_loeschen()


