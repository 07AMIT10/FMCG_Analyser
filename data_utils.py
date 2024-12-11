
import streamlit as st

def update_product_data(products):
    if not products:
        return

    for product in products:
        # Check if a product with the same brand and expiry date exists
        existing_product = next(
            (p for p in st.session_state.product_data if p['Brand'] == product['Brand'] and p['Expiry Date'] == product['Expiry Date']),
            None
        )

        if existing_product:
            # Increase the count and update timestamp
            existing_product['Count'] += product['Count']
            existing_product['Timestamp'] = product['Timestamp']
        else:
            # Assign Sl No
            product["Sl No"] = len(st.session_state.product_data) + 1
            st.session_state.product_data.append(product)