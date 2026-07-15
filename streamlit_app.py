# Streamlit app for ordering custom smoothies
# Co-authored with CoCo

import streamlit as st
import requests
from snowflake.snowpark.functions import col

# ----------------------------------------------------
# Page Title
# ----------------------------------------------------

st.title("Custom Smoothie Order Form 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# ----------------------------------------------------
# Customer Name
# ----------------------------------------------------

name_on_order = st.text_input("Name on Smoothie")

if name_on_order:
    st.write(f"The name on your smoothie will be: **{name_on_order}**")

# ----------------------------------------------------
# Connect to Snowflake
# ----------------------------------------------------

cnx = st.connection("snowflake")
session = cnx.session()

# ----------------------------------------------------
# Load Fruit Options
# ----------------------------------------------------

fruit_df = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
    .collect()
)

fruit_list = [row["FRUIT_NAME"] for row in fruit_df]

# ----------------------------------------------------
# Fruit Selection
# ----------------------------------------------------

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# ----------------------------------------------------
# Submit Order
# ----------------------------------------------------

if ingredients_list:

    ingredients_string = ", ".join(ingredients_list)

    st.write("Your smoothie will contain:")
    st.write(ingredients_string)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        if not name_on_order.strip():
            st.error("Please enter a name for your smoothie.")
        else:
            insert_sql = """
                INSERT INTO smoothies.public.orders
                (ingredients, name_on_order)
                VALUES (?, ?)
            """

            session.sql(
                insert_sql,
                params=[ingredients_string, name_on_order]
            ).collect()

            st.success("Your smoothie has been ordered! ✅")

# ----------------------------------------------------
# Nutrition Information
# ----------------------------------------------------

st.divider()
st.subheader("Fruit Nutrition Information")

fruit_to_lookup = st.selectbox(
    "Choose a fruit to view nutrition facts",
    fruit_list
)

if fruit_to_lookup:

    api_url = (
        f"https://my.smoothiefroot.com/api/fruit/"
        f"{fruit_to_lookup.lower()}"
    )

    try:
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            st.dataframe(
                response.json(),
                use_container_width=True
            )
        else:
            st.warning("Nutrition information not found.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error contacting SmoothieFroot API: {e}")
