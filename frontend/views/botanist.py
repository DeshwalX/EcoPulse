import requests
import streamlit as st


def show_botanist_view(backend_url: str):
    """Render the curation suite interface listing pending entries for expert validation."""
    st.title("🔬 Botanist Verification & Data Curation Suite")
    st.write(
        "Review production-line system inputs to build verified training datasets for the next sprint."
    )

    try:
        response = requests.get(f"{backend_url}/api/logs/all")
        if response.status_code == 200:
            logs = response.json()
            pending_logs = [l for l in logs if l["is_verified"] == 0]

            st.metric("Total Pending Review Items", len(pending_logs))
            st.markdown("---")

            if not pending_logs:
                st.success(
                    "All prediction telemetry metrics perfectly verified!"
                )
            else:
                for log in pending_logs:
                    with st.container(border=True):
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.image(
                                log["image_path"],
                                caption=f"Log ID Reference: {log['id']}",
                                use_column_width=True,
                )
                        with col2:
                            st.subheader(f"Proposed: {log['predicted_species']}")
                            st.write(
                                f"**Model Confidence:** {log['confidence']*100:.2f}%"
                            )
                            st.write(
                                f"**Submission Date:** {log['timestamp']}"
                            )

                            with st.form(f"curate_form_{log['id']}"):
                                action = st.radio(
                                    "Curation Strategy Verdict",
                                    ["Approve Prediction", "Override Taxonomy"],
                                    key=f"act_{log['id']}",
                                )
                                correction = st.text_input(
                                    "Corrected Species Taxonomy Title Name",
                                    placeholder="Only fill if overriding",
                                    key=f"corr_{log['id']}",
                                )
                                submit_action = st.form_submit_button(
                                    "Commit Curation Entry"
                                )

                                if submit_action:
                                    status_code = (
                                        1
                                        if action == "Approve Prediction"
                                        else -1
                                    )
                                    payload = {
                                        "log_id": log["id"],
                                        "status": status_code,
                                        "correction": (
                                            correction
                                            if status_code == -1
                                            else None
                                        ),
                                    }

                                    res = requests.post(
                                        f"{backend_url}/api/curate",
                                        data=payload,
                                    )
                                    if res.status_code == 200:
                                        st.toast(
                                            f"Log Entry {log['id']} successfully logged to history!"
                                        )
                                        st.rerun()
                                    else:
                                        st.error(
                                            "Failed to commit verification adjustment matrix."
                                        )
    except Exception as e:
        st.error(f"Curation engine pipeline link down exception trace: {e}")