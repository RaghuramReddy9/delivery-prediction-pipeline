import streamlit as st 
import requests
import json


# Fast API backend URL
API_URL = "http://localhost:8000/predict"

st.set_page_config(page_title="Delivery Time Predictor", layout="centered")

st.title("📦 Delivery Time Prediction App")
st.write("Enter shipment details below to estimate delivery days.")

# Input Form

with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        order_id = st.text_input("Order ID", "TEST123")
        weight_kg = st.number_input("Package Weight (kg)", min_value=0.0, value=3.5, step=0.1)
        customer_zip = st.text_input("Customer ZIP", "94085")

    with col2:
        carrier = st.selectbox("Carrier", ["UPS", "FEDEX", "DHL"])
        warehouse = st.selectbox("Warehouse", ["NEW_YORK", "LOS_ANGELES", "MIAMI", "SAN_JOSE"])
        event_time = st.text_input("Event Time (ISO)", "2025-11-18T13:00:00Z")
    
    submitted = st.form_submit_button("Predict Delivery Days")

if submitted:
    payload = {
        "order_id": order_id,
        "weight_kg": weight_kg,
        "customer_zip": customer_zip,
        "carrier": carrier,
        "warehouse": warehouse,
        "event_time": event_time
    }

    st.write("### 🔍 Request Sent to API:")
    st.json(payload)

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            result = response.json()
            predicted_days = result["predicted_delivery_days"]

            st.success(f"📢 Estimated Delivery Time: **{predicted_days:.2f} days**")

        else:
            st.error(f"API Error: {response.status_code}")
            st.write(response.text)

    except Exception as e:
        st.error("Failed to connect to FastAPI backend.")
        st.write(e)