import streamlit as st
import pandas as pd
from db_handler import df_to_db, df_from_db, df_to_db_and_replace
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

# Input neue Kategorie
def input_kategorie():
    # selects mit allen Kategorien
    kategorien = st.session_state["df_kategorien"]
    level_0 = kategorien[kategorien["parent_id"].isnull()]
    level_0_dict = dict(zip(level_0["kategorie_id"], level_0["name"]))
    level_0_select = st.selectbox("Art", level_0_dict.keys(), format_func=lambda x: level_0_dict[x])
    
    level_1 = kategorien[kategorien["parent_id"] == level_0_select]
    level_1_dict={level_0_select: "- Neue Kategorie -"}
    level_1_dict.update(dict(zip(level_1["kategorie_id"], level_1["name"])))
    level_1_select = st.selectbox("Kategorie", level_1_dict.keys(), format_func=lambda x: level_1_dict[x], index=0)

    parent_id = level_1_select

    if level_1_select != level_0_select:
        level_2 = kategorien[kategorien["parent_id"] == level_1_select]
        level_2_dict={level_1_select: "- Neue Unterkategorie -"}
        level_2_dict.update(dict(zip(level_2["kategorie_id"], level_2["name"])))
        level_2_select = st.selectbox("Unterkategorie", level_2_dict.keys(), format_func=lambda x: level_2_dict[x], index=0)
        parent_id = level_2_select

    # Input für neue Kategorie
    new_kategorie = st.text_input("Neue Kategorie")
    if st.button("Hinzufügen"):
        add_kategorie(new_kategorie, parent_id)

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
    category_dict = {parent_id: "- Neue Kategorie -"}  # Default option for "New Category"
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
display_tree(kategorien)

### Neue Kategorie hinzufügen
st.header("Neue Kategorie hinzufügen")
# hierarchische Auswahl der Elternkategorie
# input_kategorie()

st.divider()
# Start the category selection process (up to 5 levels)
cols = st.columns(2)
with cols[0]:
    st.write("Unter welcher Oberkategorie soll die neue Kategorie sein?")
with cols[1]:
    st.write("Wie soll die neue Kategorie heißen?")
cols = st.columns(2)
with cols[0]:
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
