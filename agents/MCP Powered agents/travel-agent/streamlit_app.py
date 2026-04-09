import os
from typing import Any, Dict, List

import streamlit as st
from dotenv import load_dotenv

from src.agents.orchestrator import create_orchestrator


load_dotenv()


def _init_orchestrator():
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = create_orchestrator(model_name="gpt-4")
    return st.session_state.orchestrator


def _render_properties(properties: List[Dict[str, Any]]) -> None:
    st.subheader("Hotels / Stays")
    if not properties:
        st.info("No properties found for this query.")
        return

    for idx, prop in enumerate(properties, start=1):
        title = prop.get("name", f"Property {idx}")
        score = prop.get("score", "N/A")
        with st.expander(f"{idx}. {title}  |  Score: {score}", expanded=(idx <= 3)):
            st.write(f"Rating: {prop.get('rating', 'N/A')}")
            st.write(f"Price: {prop.get('price', 'N/A')}")
            st.write(f"Accommodation: {prop.get('accommodation', 'N/A')}")
            st.write(f"Badges: {prop.get('badges', 'N/A')}")

            url = prop.get("url", "")
            if url:
                st.markdown(f"[Open listing]({url})")

            pros = prop.get("pros", [])
            if pros:
                st.write("Pros:")
                for p in pros:
                    st.write(f"- {p}")

            cons = prop.get("cons", [])
            if cons:
                st.write("Cons:")
                for c in cons:
                    st.write(f"- {c}")


def _render_flights(flights: List[Dict[str, Any]]) -> None:
    st.subheader("Flights")
    if not flights:
        st.info("No flights found for this query.")
        return

    for idx, flight in enumerate(flights, start=1):
        airline = flight.get("airline", "")
        flight_number = flight.get("flight_number", "")
        dep = flight.get("departure_airport", "")
        arr = flight.get("arrival_airport", "")
        with st.expander(f"{idx}. {airline} {flight_number}  |  {dep} → {arr}", expanded=(idx <= 3)):
            st.write(f"Departure: {flight.get('departure_time', 'N/A')}")
            st.write(f"Arrival: {flight.get('arrival_time', 'N/A')}")
            st.write(f"Arrival terminal: {flight.get('arrival_terminal', 'N/A')}")
            st.write(f"Aircraft: {flight.get('aircraft', 'N/A')}")


def main() -> None:
    st.set_page_config(page_title="Travel Agent", page_icon="✈️", layout="wide")
    st.title("AI Travel Assistant")
    st.caption("Find stays and flight schedules from one query.")

    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY is not set. Add it to a `.env` file or your environment.")
        st.stop()

    query = st.text_area(
        "Travel request",
        placeholder=(
            "I am travelling from Mumbai to Dubai on 25 Feb 2026. "
            "Show me hotels and flights."
        ),
        height=110,
    )

    run = st.button("Search", type="primary")
    if run:
        if not query.strip():
            st.warning("Please enter a query.")
            st.stop()

        with st.spinner("Running travel workflow..."):
            try:
                orchestrator = _init_orchestrator()
                result = orchestrator.run(query.strip())
                st.session_state.last_result = result
            except Exception as exc:
                st.exception(exc)
                st.stop()

    result = st.session_state.get("last_result")
    if not result:
        return

    requirements = result.get("requirements", {})
    with st.expander("Parsed requirements", expanded=False):
        st.json(requirements)

    summary = result.get("summary", "")
    if summary:
        st.subheader("Summary")
        st.markdown(summary)

    col1, col2 = st.columns(2)
    with col1:
        _render_properties(result.get("properties", []))
    with col2:
        _render_flights(result.get("flights", []))


if __name__ == "__main__":
    main()
