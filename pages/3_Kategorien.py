import streamlit as st
import pandas as pd
from db_handler import df_to_db, df_from_db, df_to_db_and_replace, remove_rows_where
import plotting as plotting


# TODO: Funktion, um Kontostände manuell zu ändern (ohne Transaktion)

### Page Config ###
st.set_page_config(page_title="Vermögen", page_icon=":money_with_wings:")


### Datenbank ###
# lade bestehende Konten in session state
st.session_state["df_kategorien"] = df_from_db("kategorien")

### Funktionen ###
# Darstellung der Kategorien als hierarchie
def display_tree(df, parent_id=None, level=0):
    string = ""
    if parent_id is None:
        filtered = df[df["parent_id"].isnull()]
    else:
        filtered = df[df["parent_id"] == parent_id]
    for _, row in filtered.iterrows():
        indent = "  " * level
        string += f"{indent}* {row['name']}\n"  # Add category to string
        string += display_tree(df, row["kategorie_id"], level + 1)  # Recursive call for subcategories
    if parent_id is None:
        st.markdown(string)
    return string

# Funktion, um Kategorie hinzuzufügen
def add_kategorie(name, parent_id=None):
    # neue Kategorie erstellen
    new_kategorie = pd.DataFrame({"name": [name], "parent_id": [parent_id]})
    # Kategorie in Datenbank speichern
    df_to_db(new_kategorie, "kategorien")
    # Kategorien neu laden
    st.session_state["df_kategorien"] = df_from_db("kategorien")

# Funktion, um Kategorie zu löschen
def delete_kategorie(kategorie_id):
    # Kategorie und alle Unterkategorien löschen
    kategorien = st.session_state["df_kategorien"]
    kategorie_ids = [kategorie_id]
    for i in range(5):  # Maximal 5 Level
        subcategories = kategorien[kategorien["parent_id"].isin(kategorie_ids)]
        if subcategories.empty:
            break
        # Add the subcategories to the list of categories to delete
        kategorie_ids += subcategories["kategorie_id"].tolist()

    # Delete the categories from the database
    remove_rows_where("kategorien", "kategorie_id", kategorie_ids)
    # Kategorien neu laden
    st.session_state["df_kategorien"] = df_from_db("kategorien")

# dialog zum löschen eines kontos
@st.dialog("Kategorie löschen?")
def delete(kategorie_id):
    kategorie_name = st.session_state["df_kategorien"][st.session_state["df_kategorien"]["kategorie_id"] == kategorie_id]["name"].values[0]
    st.write(f":warning: Bist du sicher, dass du die Kategorie {kategorie_name} löschen willst? Dadurch werden alle Unterkategorien ebenfalls gelöscht. :warning:")
    if st.button("Bestätigen"):
        try:
            delete_kategorie(kategorie_id)
            st.success("Kategorie erfolgreich gelöscht")
        except Exception as e:
            st.error(f"Fehler beim Löschen der Kategorie: {e}")

# Recursive function to generate selectboxes up to 5 levels
def generate_category_select(kategorien, parent_id=None, level=0, max_level=5):
    if level >= max_level:
        return parent_id

    # Filter categories for the current parent_id
    if parent_id is None:
        filtered_categories = kategorien[kategorien["parent_id"].isnull()]
    else:
        filtered_categories = kategorien[kategorien["parent_id"] == parent_id]

    if filtered_categories.empty:
        return parent_id

    # Prepare options for the current level
    category_dict = {parent_id: "- Keine Auswahl -"}  # Default option for "New Category"
    category_dict.update(dict(zip(filtered_categories["kategorie_id"], filtered_categories["name"])))

    # Create the selectbox for the current level
    selected_category_id = st.selectbox(f"Level {level + 1} Kategorie", list(category_dict.keys()), format_func=lambda x: category_dict[x], index=0)

    # Recursively call the function to go deeper into the hierarchy
    if selected_category_id == parent_id:
        return parent_id
    else:
        return generate_category_select(kategorien, selected_category_id, level + 1, max_level)



### UI ###
st.title("Kategorienübersicht")

## Kategorienübersicht
st.write("Hierarchische Darstellung der Kategorien:")
kategorien = st.session_state["df_kategorien"]
print("og",kategorien)
display_tree(kategorien)

### Neue Kategorie hinzufügen
st.header("Kategorie hinzufügen / löschen")
# Start the category selection process (up to 5 levels)
cols = st.columns(2)
with cols[0]:
    st.write("Auswahl bestehender Kategorien:")
with cols[1]:
    st.write("Kategorie unter ausgewählter Kategorie hinzufügen:")
cols = st.columns(2)
with cols[0]:
    if kategorien.empty:
        st.warning("Keine Kategorien vorhanden, bitte füge eine hinzu :point_right:")
    selected_category = generate_category_select(kategorien, parent_id=None, level=0, max_level=5)

# Input for new category
with cols[1]:
    new_kategorie = st.text_input("Name")

    # Add category button
    if st.button("Hinzufügen"):
        if new_kategorie:
            # Call your add_kategorie function to add the new category
            add_kategorie(new_kategorie, selected_category)
            st.success(f"Die Kategorie '{new_kategorie}' wurde erfolgreich hinzugefügt.")
        else:
            st.warning("Bitte geben Sie einen Namen für die neue Kategorie an.")
    
    st.write("Ausgewählte Kategorie löschen:")
    if st.button("Löschen"):
        delete(kategorie_id=selected_category)
        st.success(f"Die Kategorie wurde erfolgreich gelöscht.")
