import streamlit as st
import pandas as pd
from db_handler import df_to_db, df_from_db, df_to_db_and_replace

### Page Config ###
st.set_page_config(page_title="Transaktionen", page_icon=":arrows_clockwise:")


### Datenbank ###
# lade bestehende Konten in session state
st.session_state["df_konten"] = df_from_db("konten")
st.session_state["existierende_konten"] = df_from_db("konten")["name"].tolist()
st.session_state["eigene_konten"] = df_from_db("konten")[df_from_db("konten")["eigenes_konto"] == True]
st.session_state["externe_konten"] = df_from_db("konten")[df_from_db("konten")["eigenes_konto"] == False]
st.session_state["df_transaktionen"] = df_from_db("transaktionen")

konto_ids = st.session_state["df_konten"]["konto_id"]
konto_namen = st.session_state["df_konten"]["name"]
indizes_intern = st.session_state["df_konten"]["eigenes_konto"]
st.session_state["konto_dict"] = dict(zip(konto_ids,konto_namen))

st.write(st.session_state["df_konten"][indizes_intern])

### Funktionen ###

def neue_transaktion():
    # add account to database
    st.header("Transaktion eintragen")
    form = st.form(key="add_transaction")
    art = form.selectbox("Art", ["Einnahme", "Ausgabe", "Verschiebung"], key="transaktions_art")
    if st.session_state["transaktions_art"] == "Einnahme":
        konto_eingehend = form.selectbox("Konto eingehend", st.session_state["eigene_konten"]["name"].tolist())
        konto_ausgehend = form.selectbox("Konto ausgehend", st.session_state["externe_konten"]["name"].tolist())
    elif st.session_state["transaktions_art"] == "Ausgabe":
        konto_eingehend = form.selectbox("Konto eingehend", st.session_state["externe_konten"]["name"].tolist())
        konto_ausgehend = form.selectbox("Konto ausgehend", st.session_state["eigene_konten"]["name"].tolist())
    else:
        konto_eingehend = form.selectbox("Konto eingehend", st.session_state["eigene_konten"]["name"].tolist())
        konto_ausgehend = form.selectbox("Konto ausgehend", st.session_state["eigene_konten"]["name"].tolist())
    kategorie = form.multiselect("Kategorie", ["Lebensmittel", "Miete", "Gehalt", "Versicherung", "Auto", "Sonstiges"]) ## Lege Katalog fest. Mit über- und unterkategorien, speichere in DB
    datum = form.date_input("Datum")
    betrag = form.number_input("Betrag")
    waehrung = form.selectbox("Währung", ["EUR", "USD", "CHF", "NOK"])
    beschreibung = form.text_input("Beschreibung")
    submit = form.form_submit_button("Transaktion eintragen")

    if submit:
        try:
            df = pd.DataFrame({
                "konto_id_incoming": [st.session_state["eigene_konten"][st.session_state["eigene_konten"]["name"] == konto_eingehend]["konto_id"].values[0]],
                "konto_id_outgoing": [st.session_state["externe_konten"][st.session_state["externe_konten"]["name"] == konto_ausgehend]["konto_id"].values[0]],
                "datum": [datum],
                "betrag": [betrag],
                "beschreibung": [beschreibung],
                "kategorie": [kategorie],
                "dauerauftrag": [False],
                "waehrung": [waehrung]
            })
            df_to_db(df, "transaktionen", safe_write=False, overwrite_db_in_conflict=True)

            st.success("Transaktion erfolgreich hinzugefügt")
            st.session_state["df_transaktionen"] = df_from_db("transaktionen")

        except Exception as e:
            st.error(f"Fehler beim Hinzufügen der Transaktion: {e}")

### UI ###
st.title("Transaktionen")

neue_transaktion()

st.write(st.session_state["df_transaktionen"])

## INHALTE AUF DIESER SEITE
    # Filter für Transaktionen 
        #  Art der Transaktion: Einnahmen, Ausgaben, Verschiebungen zwischen eigenen Konten
        #  Kategorie: (optional) Multiselect mit allen Kategorien
        #  Zeitraum: Datumsslider
        #  Betrag: Slider
        #  eigene Konto: Multiselect mit allen eigenen Konten
        #  externe Konten: Multiselect mit allen externen Konten
        #  Wort in Beschreibung: Textfeld
        #  Daueraufträge: Checkbox

    # Tabelle mit allen gefilterten Transaktionen

    # input form für neue Transaktion (überlege noch Kategorien)

    # input form für Dauerauftrag (überlege noch wie ich die Speicherung mache)

    # löschen von Transaktionen (evtl. mit checkbox in der Tabelle und dann löschen button)

    # editieren von Transaktionen (evtl. mit checkbox in der Tabelle und dann editieren button)

    # löschen von Daueraufträgen