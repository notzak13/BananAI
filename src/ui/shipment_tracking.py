import streamlit as st
import pandas as pd
from datetime import datetime

from src.services.shipment_simulator import simulate_shipment
from src.controller.order_controller import OrderController
from src.models.inventory import Inventory
from src.repository.batch_repository import BatchRepository
import streamlit as st

def shipment_tracking_ui():
    st.title("📦 Seguimiento de Cargamento")
    st.info("Módulo de seguimiento cargado correctamente.")


def shipment_tracking_ui():
    st.markdown("## 📦 Seguimiento de Cargamento")

    # Inicializar controlador (solo lectura)
    controller = OrderController(Inventory(), BatchRepository())
    history = controller._read_history()

    if not history:
        st.info("Aún no tienes compras registradas.")
        return

    # Tomamos la última compra del cliente
    last_order = history[-1]

    purchase_date = datetime.fromisoformat(last_order["timestamp"])
    destination = last_order["destination"]
    weight = last_order.get("weight_kg", "N/A")
    tier = last_order.get("tier_sold", "N/A")

    # Información general
    st.markdown("### 🧾 Información de la compra")
    st.markdown(f"""
    **Fecha de compra:** {purchase_date.strftime('%d/%m/%Y %H:%M')}  
    **Destino:** {destination}  
    **Cantidad:** {weight} kg  
    **Calidad:** {tier}
    """)

    # Simular ruta
    timeline = simulate_shipment(purchase_date, destination)

    if not timeline:
        st.error("No se pudo generar la ruta para este destino.")
        return

    now = datetime.now()

    # Determinar estado actual
    current_step = timeline[0]
    for step in timeline:
        if step["timestamp"] <= now:
            current_step = step

    # Estado actual
    st.markdown("### 🚢 Estado actual del cargamento")
    st.success(
        f"El cargamento se encuentra en **{current_step['location']}**\n\n"
        f"🕒 {current_step['timestamp'].strftime('%d/%m/%Y %H:%M')}"
    )

    # Línea de tiempo
    st.markdown("### 📍 Línea de tiempo del envío")
    for step in timeline:
        status_icon = "✅" if step["timestamp"] <= now else "⏳"
        st.write(
            f"{status_icon} **{step['location']}** — "
            f"{step['timestamp'].strftime('%d/%m/%Y %H:%M')}"
        )

    # Mapa
    st.markdown("### 🗺️ Ruta del cargamento")

    df_map = pd.DataFrame(timeline)
    df_map = df_map.rename(columns={
        "lat": "latitude",
        "lon": "longitude"
    })

    st.map(df_map)

    # Estado final
    if now >= timeline[-1]["timestamp"]:
        st.success("📦 El cargamento ha llegado a su destino final.")
    else:
        st.info("🚚 El cargamento se encuentra en tránsito.")
