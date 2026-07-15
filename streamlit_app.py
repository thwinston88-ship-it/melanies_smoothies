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
    .select(col("FRUIT_NAME"),col('SEARCH_ON))
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
# Display Nutrition Information
# ----------------------------------------------------

if ingredients_list:

    st.divider()
    st.subheader("Nutrition Information")

    for fruit in ingredients_list:

        st.markdown(f"### 🍎 {fruit}")

        api_url = f"https://my.smoothiefroot.com/api/fruit/{fruit.lower()}"

        try:
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                nutrition = response.json()

                # Convert dictionary to table
                st.table(nutrition)

            else:
                st.warning(f"No nutrition information found for {fruit}.")

        except requests.exceptions.RequestException as e:
            st.error(f"Error retrieving nutrition information for {fruit}: {e}")

# ----------------------------------------------------
# Submit Order
# ----------------------------------------------------

if ingredients_list:

    ingredients_string = ", ".join(ingredients_list)

    st.write("### Your Smoothie")
    st.write(f"**Name:** {name_on_order}")
    st.write(f"**Ingredients:** {ingredients_string}")

    if st.button("Submit Order"):

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

            st.success("✅ Your smoothie has been ordered!")
