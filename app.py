"""Streamlit UI for the AI-powered lead research and enrichment MVP."""

import streamlit as st

from lead_agent.database import (
    delete_lead,
    get_lead,
    initialize_database,
    list_leads,
    save_lead,
)
from lead_agent.enrichment import EnrichmentError, enrich_lead


st.set_page_config(page_title="Lead Research Agent", page_icon="🔎", layout="wide")
initialize_database()

st.title("AI-Powered Lead Research & Enrichment Agent")
st.caption(
    "Organize leads and generate cautious AI suggestions from information you provide."
)

with st.sidebar:
    st.header("Add a lead")
    with st.form("new_lead_form", clear_on_submit=True):
        company_name = st.text_input("Company name *")
        website = st.text_input("Website")
        contact_name = st.text_input("Contact name")
        job_title = st.text_input("Job title")
        email = st.text_input("Work email")
        industry = st.text_input("Industry")
        location = st.text_input("Location")
        research_notes = st.text_area(
            "Research notes",
            help="Enter notes you collected from sources you are authorized to use.",
        )
        source_urls = st.text_area("Source URLs", help="One source link per line.")
        submitted = st.form_submit_button("Add lead", type="primary")
        if submitted:
            if not company_name.strip():
                st.error("Company name is required.")
            else:
                try:
                    save_lead(
                        {
                            "company_name": company_name,
                            "website": website,
                            "contact_name": contact_name,
                            "job_title": job_title,
                            "email": email,
                            "industry": industry,
                            "location": location,
                            "research_notes": research_notes,
                            "source_urls": source_urls,
                        }
                    )
                except (ValueError, OSError) as exc:
                    st.error(f"Could not save lead: {exc}")
                else:
                    st.success("Lead added.")
                    st.rerun()

search_term = st.text_input("Search leads", placeholder="Company, contact, or email")
leads = list_leads(search_term)

if not leads:
    st.info("No leads yet. Add one using the form in the sidebar.")
else:
    st.subheader(f"Leads ({len(leads)})")
    st.dataframe(
        [
            {
                "Company": lead["company_name"],
                "Contact": lead["contact_name"],
                "Title": lead["job_title"],
                "Industry": lead["industry"],
                "Location": lead["location"],
                "Fit": lead["fit_score"] or "",
                "Website": lead["website"],
            }
            for lead in leads
        ],
        use_container_width=True,
        hide_index=True,
    )

    lead_by_label = {
        f"{lead['company_name']} — {lead['contact_name'] or 'No contact'} (#{lead['id']})": lead[
            "id"
        ]
        for lead in leads
    }
    selected_label = st.selectbox("Lead details", list(lead_by_label))
    selected_id = lead_by_label[selected_label]
    selected = get_lead(selected_id)

    if selected is not None:
        st.markdown(f"### {selected['company_name']}")
        details_col, enrichment_col = st.columns(2)
        with details_col:
            st.write(f"**Website:** {selected['website'] or '—'}")
            st.write(f"**Contact:** {selected['contact_name'] or '—'}")
            st.write(f"**Title:** {selected['job_title'] or '—'}")
            st.write(f"**Email:** {selected['email'] or '—'}")
            st.write(f"**Industry:** {selected['industry'] or '—'}")
            st.write(f"**Location:** {selected['location'] or '—'}")
            st.write(f"**Research notes:** {selected['research_notes'] or '—'}")
            st.write(f"**Source URLs:** {selected['source_urls'] or '—'}")

        with enrichment_col:
            if selected["ai_summary"]:
                st.write("**AI summary:**")
                st.write(selected["ai_summary"])
                st.write(f"**Suggested fit score:** {selected['fit_score']}/5")

            if st.button("Enrich with AI", type="primary"):
                with st.spinner("Generating suggestions from supplied information..."):
                    try:
                        suggestions = enrich_lead(selected)
                        save_lead(
                            {
                                **selected,
                                "industry": suggestions["industry"] or selected["industry"],
                                "location": suggestions["location"] or selected["location"],
                                "ai_summary": suggestions["summary"],
                                "fit_score": suggestions["fit_score"],
                            },
                            lead_id=selected_id,
                        )
                    except (EnrichmentError, ValueError, OSError) as exc:
                        st.error(str(exc))
                    else:
                        st.success("AI suggestions saved. Review them before treating them as facts.")
                        st.rerun()

        with st.expander("Edit lead"):
            with st.form(f"edit_lead_{selected_id}"):
                edited = {
                    "company_name": st.text_input(
                        "Company name", value=selected["company_name"], key=f"company_{selected_id}"
                    ),
                    "website": st.text_input(
                        "Website", value=selected["website"], key=f"website_{selected_id}"
                    ),
                    "contact_name": st.text_input(
                        "Contact name", value=selected["contact_name"], key=f"contact_{selected_id}"
                    ),
                    "job_title": st.text_input(
                        "Job title", value=selected["job_title"], key=f"title_{selected_id}"
                    ),
                    "email": st.text_input(
                        "Work email", value=selected["email"], key=f"email_{selected_id}"
                    ),
                    "industry": st.text_input(
                        "Industry", value=selected["industry"], key=f"industry_{selected_id}"
                    ),
                    "location": st.text_input(
                        "Location", value=selected["location"], key=f"location_{selected_id}"
                    ),
                    "research_notes": st.text_area(
                        "Research notes",
                        value=selected["research_notes"],
                        key=f"notes_{selected_id}",
                    ),
                    "source_urls": st.text_area(
                        "Source URLs",
                        value=selected["source_urls"],
                        key=f"sources_{selected_id}",
                    ),
                    "ai_summary": st.text_area(
                        "AI summary", value=selected["ai_summary"], key=f"summary_{selected_id}"
                    ),
                    "fit_score": st.number_input(
                        "Fit score (1–5)",
                        min_value=1,
                        max_value=5,
                        value=selected["fit_score"] or 3,
                        key=f"score_{selected_id}",
                    ),
                }
                if st.form_submit_button("Save changes"):
                    try:
                        save_lead(edited, lead_id=selected_id)
                    except (ValueError, OSError) as exc:
                        st.error(f"Could not update lead: {exc}")
                    else:
                        st.success("Lead updated.")
                        st.rerun()

        if st.button("Delete this lead", type="secondary"):
            try:
                delete_lead(selected_id)
            except (ValueError, OSError) as exc:
                st.error(f"Could not delete lead: {exc}")
            else:
                st.success("Lead deleted.")
                st.rerun()
