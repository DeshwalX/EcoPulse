import pandas as pd
import requests
import streamlit as st


def show_admin_view(backend_url: str):
    """Render overall performance analytics metrics and the comprehensive system audit table."""
    st.title("🔑 Global Infrastructure Operations Control")
    st.write(
        "System status metrics, resource asset audits, and model drift telemetry indices."
    )

    try:
        response = requests.get(f"{backend_url}/api/logs/all")
        if response.status_code == 200:
            logs = response.json()

            total_inferences = len(logs)
            approved = len([l for l in logs if l["is_verified"] == 1])
            overridden = len([l for l in logs if l["is_verified"] == -1])

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Transactions Packets Processed", total_inferences)
            c2.metric("Expert Verified Datasets", approved)
            c3.metric("Model Classification Divergences", overridden)

            st.markdown("### System Telemetry Log Audits")
            if logs:
                df = pd.DataFrame(logs)
                df = df[
                    [
                        "id",
                        "user_id",
                        "predicted_species",
                        "confidence",
                        "is_verified",
                        "corrected_species",
                        "timestamp",
                    ]
                ]
                st.dataframe(df, use_container_width=True)
            else:
                st.info(
                    "System tracking register empty. Log metrics data generation pending operations execution."
                )
    except Exception as e:
        st.error(f"Global resource tracing access module failure: {e}")