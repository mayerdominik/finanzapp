import streamlit as st
import pandas as pd
from db_handler import df_to_db, df_from_db, df_to_db_and_replace
import datetime

### Page Config ###
st.set_page_config(page_title="Transaktionen", page_icon=":arrows_clockwise:")

st.warning("Bugfix: Transaktion hinzufügen funktioniert nicht(Wird nicht in Datenbank gespeichert)")

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
st.session_state["konto_dict_intern"] = dict(zip(konto_ids[indizes_intern],konto_namen[indizes_intern]))
st.session_state["konto_dict_extern"] = dict(zip(konto_ids[~indizes_intern],konto_namen[~indizes_intern]))
max_id = max(st.session_state["df_konten"]["konto_id"])

### Funktionen ###

def format_transaction_to_markdown(art, betrag, waehrung):
    waehrung_symbol = {"EUR": "€", "USD": "$", "CHF": "CHF", "NOK": "NOK"}
    if art == "Einnahme":
        return f'<p style="color:green; font-size:20px; font-weight:bold;"> + {betrag:.2f} {waehrung_symbol[waehrung]}</p>'
    elif art == "Ausgabe":
        return f'<p style="color:red; font-size:20px; font-weight:bold;"> - {betrag:.2f} {waehrung_symbol[waehrung]}</p>'
    elif art == "Verschiebung":
        return f'<p style="color:blue; font-size:20px; font-weight:bold;"> {betrag:.2f} {waehrung_symbol[waehrung]}</p>'

def transaktionen_anzeigen():
    st.header("Transaktionsübersicht")

    df_transaktionen = st.session_state["df_transaktionen"].copy()
    if df_transaktionen.empty:
        st.info("Keine Transaktionen vorhanden, füge unten die erste hinzu!")
        return

    ## Filter ##

    # Zeitraum filtern
    cols = st.columns([1, 2])
    today = datetime.date.today()
    zeitraeume = {"Aktueller Monat": (datetime.date(today.year, today.month, 1), today), 
                  "Letzte 30 Tage": (today - datetime.timedelta(days=30), today), 
                  "Letzte 90 Tage": (today - datetime.timedelta(days=90), today), 
                  "Aktuelles Jahr": (datetime.date(today.year, 1, 1), today),
                  "Letzte 365 Tage": (today - datetime.timedelta(days=90), today),
                  "Eigener Zeitraum": (df_transaktionen["datum"].min(), today)}
    with cols[0]:
        preselected_date = st.selectbox("Zeitraum", list(zeitraeume.keys()))
    with cols[1]:
        if preselected_date == "Eigener Zeitraum":
            # Eigenen Zeitraum einschränken
            if len(df_transaktionen["datum"]) == 1:
                date_slider = (df_transaktionen["datum"].values[0], df_transaktionen["datum"].values[0])
            else:
                today = datetime.date.today()
                min_date = df_transaktionen["datum"].min()
                max_date = df_transaktionen["datum"].max()
                date_slider = st.slider("Eigener Zeitraum", min_value=min_date, max_value=max_date, value=(min_date, today), format="DD.MM.YYYY")
        else:
            date_slider = zeitraeume[preselected_date]    
    
    df_transaktionen_copy = df_transaktionen[df_transaktionen["datum"].between(date_slider[0], date_slider[1])]
    df_transaktionen = df_transaktionen_copy

    with st.expander("Art & Kategorie"):
        cols = st.columns(2)
        with cols[0]:
            # Einnahmen, Ausgaben, Verschiebungen filtern
            arten = df_transaktionen["art"].unique()
            art = st.multiselect("Art", arten, default=arten)
        with cols[1]:
            # Nach Kategorie filtern
            kategorien = df_transaktionen["kategorie"].unique()
            kategorie = st.multiselect("Kategorie", kategorien, default=kategorien)

    # Konten filtern
    with st.expander("Konten"):
        cols = st.columns(2)
        with cols[0]:
            # Eigene Konten filtern
            eigene_konten_options = {konto_id: konto_name for konto_id, konto_name in zip(st.session_state["eigene_konten"]["konto_id"], st.session_state["eigene_konten"]["name"])}
            eigenes_konto = st.multiselect("Eigene Konten", eigene_konten_options.keys(), format_func=lambda x: eigene_konten_options[x], default=eigene_konten_options.keys())
        with cols[1]:
            # Externe Konten filtern
            externe_konten_options = {konto_id: konto_name for konto_id, konto_name in zip(st.session_state["externe_konten"]["konto_id"], st.session_state["externe_konten"]["name"])}
            externes_konto = st.multiselect("Externe Konten", externe_konten_options.keys(), format_func=lambda x: externe_konten_options[x], default=externe_konten_options.keys())


    st.divider()
    # Ergebnisse filtern und anzeigen
    df_transaktionen = df_transaktionen[df_transaktionen["art"].isin(art) & df_transaktionen["kategorie"].isin(kategorie)]
    df_transaktionen = df_transaktionen[(df_transaktionen["art"] == "Verschiebung") | df_transaktionen["konto_id_incoming"].isin(externes_konto) | df_transaktionen["konto_id_outgoing"].isin(externes_konto)]
    df_transaktionen = df_transaktionen[df_transaktionen["konto_id_incoming"].isin(eigenes_konto) | df_transaktionen["konto_id_outgoing"].isin(eigenes_konto)]
    # st.dataframe(df_transaktionen)

    # Tabelle anzeigen
    if df_transaktionen.empty:
        st.info("Keine Transaktionen für den ausgewählten Zeitraum und Filter vorhanden")
        return
    cols = st.columns(5)
    cols[0].subheader("Datum")
    cols[1].subheader("Von")
    # cols[2].write("")
    cols[3].subheader("An")
    cols[4].subheader("Kat.")

    df_transaktionen = df_transaktionen.sort_values("datum", ascending=False)
    for i, row in df_transaktionen.iterrows():
        cols = st.columns(5)
        cols[0].write(row["datum"].strftime("%d.%m.%Y"))
        cols[1].write(st.session_state["konto_dict"][row["konto_id_outgoing"]])
        cols[2].markdown(format_transaction_to_markdown(row["art"], row["betrag"], row["waehrung"]), unsafe_allow_html=True)
        cols[3].write(st.session_state["konto_dict"][row["konto_id_incoming"]])
        cols[4].write(row["kategorie"])


def neue_transaktion():
    st.header("Transaktion eintragen")

    cols = st.columns(3)
    # Select transaction type outside the form for dynamic updates
    transaktions_art = cols[0].selectbox("Art", ["Einnahme", "Ausgabe", "Verschiebung"], key="transaktions_art")

    # Determine dropdown options dynamically
    if transaktions_art == "Einnahme":
        konto_eingehend_options = st.session_state["konto_dict_intern"]
        konto_ausgehend_options = st.session_state["konto_dict_extern"]
    elif transaktions_art == "Ausgabe":
        konto_eingehend_options = st.session_state["konto_dict_extern"]
        konto_ausgehend_options = st.session_state["konto_dict_intern"]
    else:
        konto_eingehend_options = st.session_state["konto_dict_intern"]
        konto_ausgehend_options = st.session_state["konto_dict_intern"]

    # Add "Other" option to allow user input
    if transaktions_art == "Einnahme":
        konto_ausgehend_options[max_id+1] = "Andere (bitte eingeben)"
    if transaktions_art == "Ausgabe":
        konto_eingehend_options[max_id+1] = "Andere (bitte eingeben)"

    # Konto ausgehend selection with optional text input
    konto_ausgehend = cols[1].selectbox("Konto ausgehend", konto_ausgehend_options.keys(), format_func=lambda x: konto_ausgehend_options[x])
    if konto_ausgehend == max_id+1:
        konto_ausgehend_text = cols[1].text_input("Neues Konto ausgehend")

    # Konto eingehend selection with optional text input, nur wenn es ein externes Konto ist
    konto_eingehend = cols[2].selectbox("Konto eingehend", konto_eingehend_options.keys(), format_func=lambda x: konto_eingehend_options[x])
    if konto_eingehend == max_id+1:
        konto_eingehend_text = cols[2].text_input("Neues Konto eingehend")



    # Start the form
    form = st.form(key="add_transaction")
    kategorie = form.selectbox("Kategorie", ["Lebensmittel", "Miete", "Gehalt", "Versicherung", "Auto", "Sonstiges"]) #überarbeiten, erstelle eigenen Katalog oberste ebene einnahmen, ausgaben, verschiebungen
    datum = form.date_input("Datum")
    betrag = form.number_input("Betrag")
    waehrung = form.selectbox("Währung", ["EUR", "USD", "CHF", "NOK"])
    beschreibung = form.text_input("Beschreibung")
    submit = form.form_submit_button("Transaktion eintragen")

    if submit:
        try:
            # Wenn ein neues Konto eingetragen wurde, füge es der Kontentabelle hinzu
            if konto_eingehend == max_id+1:
                df = pd.DataFrame({
                    "erstellungsdatum": [pd.Timestamp.now()],
                    "name": [konto_eingehend_text],
                    "bank": [""],
                    "typ": ["Externes Konto"],
                    "kontostand": [0],
                    "waehrung": [waehrung],
                    "iban": [""],
                    "eigenes_konto": [False]
                })
                df_to_db(df, "konten", safe_write=False, overwrite_db_in_conflict=True)
            
            if konto_ausgehend == max_id+1:
                df = pd.DataFrame({
                    "erstellungsdatum": [pd.Timestamp.now()],
                    "name": [konto_ausgehend_text],
                    "bank": [""],
                    "typ": ["Externes Konto"],
                    "kontostand": [0],
                    "waehrung": [waehrung],
                    "iban": [""],
                    "eigenes_konto": [False]
                })
                df_to_db(df, "konten", safe_write=False, overwrite_db_in_conflict=True)

            

            # speichere Transaktion in Datenbank
            df_trans = pd.DataFrame({
                "konto_id_incoming": [konto_eingehend],  # Store custom input if entered
                "konto_id_outgoing": [konto_ausgehend],
                "art": [transaktions_art],
                "datum": [datum],
                "betrag": [betrag],
                "beschreibung": [beschreibung],
                "kategorie": [kategorie],
                "dauerauftrag": [False],
                "waehrung": [waehrung]
            })

            df_to_db(df_trans, "transaktionen", safe_write=False, overwrite_db_in_conflict=True)

            # ändere Kontostände in Datenbank
            st.session_state["df_konten"].loc[st.session_state["df_konten"]["konto_id"] == konto_eingehend, "kontostand"] += betrag
            st.session_state["df_konten"].loc[st.session_state["df_konten"]["konto_id"] == konto_ausgehend, "kontostand"] -= betrag
            df_to_db_and_replace(st.session_state["df_konten"], "konten")

            # Speichere geänderte Kontostände
            df = pd.DataFrame({
                "konto_id": [konto_eingehend, konto_ausgehend],
                "datum": [datum, datum],
                "kontostand": [st.session_state["df_konten"].loc[st.session_state["df_konten"]["konto_id"] == konto_eingehend, "kontostand"].values[0], 
                           st.session_state["df_konten"].loc[st.session_state["df_konten"]["konto_id"] == konto_ausgehend, "kontostand"].values[0]],
                "waehrung": [waehrung, waehrung]
            })
            df_to_db(df, "kontostaende", safe_write=False, overwrite_db_in_conflict=True)

            # Update session state
            st.session_state["df_transaktionen"] = df_from_db("transaktionen")
            st.session_state["df_konten"] = df_from_db("konten")
            st.session_state["df_kontostaende"] = df_from_db("kontostaende")
                
            st.success("Transaktion erfolgreich hinzugefügt")

        except Exception as e:
            st.error(f"Fehler beim Hinzufügen der Transaktion: {e}")

### UI ###
st.title("Transaktionen")


# Transaktionen anzeigen
transaktionen_anzeigen()

st.divider()

# Formular für neue Transaktion
neue_transaktion()


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