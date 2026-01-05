
import streamlit as st
import pandas as pd
from datetime import date, time
import db

def app():
    st.markdown("<h1 style='text-align: center;'>Manage</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>View and Manage Room Bookings..</h6>", unsafe_allow_html=True)

    rooms = db.get_all_rooms()
    room_filter_options = {0: "All Rooms"}
    room_filter_options.update({room.id: room.name for room in rooms})

    all_bookings_raw = db.get_bookings()

    months = ["All", "Jan", "Feb", "Mar", "Apr", "May", "Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    years = sorted({b.booking_date.year for b in all_bookings_raw})
    years_options = ["All"] + [str(y) for y in years]

    col1, col2 = st.columns([3, 7])
    with col1:
        st.subheader("Filters")

        def clear_filters():
            for k in [
                "key_selected_room",
                "key_date_mode",
                "key_date",
                "key_month",
                "key_year",
                "key_time_mode",
                "key_time_from",
                "key_time_to",
                "key_reserver",
                "key_purpose",
            ]:
                st.session_state.pop(k, None)
            st.session_state["key_selected_room"] = 0
            st.session_state["key_date_mode"] = "All Dates"
            st.session_state["key_time_mode"] = "All times"
            st.session_state["key_reserver"] = ""
            st.session_state["key_purpose"] = ""

        col_btn1, col_btn2 = st.columns([3, 2])
        with col_btn1:
            st.caption("Filters apply automatically when changed.")
        with col_btn2:
            st.button("Clear filters", on_click=clear_filters)

        st.markdown("---")
        st.selectbox(
            "Room",
            options=list(room_filter_options.keys()),
            format_func=lambda x: room_filter_options[x],
            key="key_selected_room")

        date_scope = st.selectbox(
            "Date scope",
            options=["All Dates", "Specific Date", "Specific Month/Year"],
            index=0,
            key="key_date_mode")

        if date_scope == "Specific Date":
            st.date_input(
                "Date",
                value=st.session_state.get("key_date", date.today()),
                key="key_date")
            st.session_state["key_month"] = "All"
            st.session_state["key_year"] = "All"

        elif date_scope == "Specific Month/Year":
            st.selectbox(
                "Month",
                options=months,
                index=months.index(st.session_state.get("key_month", "All")),
                key="key_month")
            st.selectbox(
                "Year",
                options=years_options,
                index=years_options.index(st.session_state.get("key_year", "All")),
                key="key_year")
            st.session_state["key_date"] = None

        else:
            st.session_state["key_date"] = None
            st.session_state["key_month"] = "All"
            st.session_state["key_year"] = "All"

        time_scope = st.selectbox(
            "Time scope",
            options=["All times", "Specific time range"],
            index=0,
            key="key_time_mode")
        
        if time_scope == "Specific time range":
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.time_input(
                    "From",
                    value=st.session_state.get("key_time_from", time(hour=9, minute=0)),
                    key="key_time_from")
            with col_t2:
                st.time_input(
                    "To",
                    value=st.session_state.get("key_time_to", time(hour=17, minute=0)),
                    key="key_time_to")

        st.text_input(
            "Reserver name contains",
            value=st.session_state.get("key_reserver", ""),
            key="key_reserver",
        )
        st.text_input(
            "Purpose contains",
            value=st.session_state.get("key_purpose", ""),
            key="key_purpose",
        )

    sel_room = st.session_state.get("key_selected_room")
    room_id = sel_room if sel_room != 0 else None

    sel_date_scope = st.session_state.get("key_date_mode")
    date_of_booked = None
    month_int = None
    year_int = None
    sel_month = st.session_state.get("key_month")
    sel_year = st.session_state.get("key_year")
    if sel_date_scope == "Specific Date":
        date_of_booked = st.session_state.get("key_date", date.today())
    elif sel_date_scope == "Specific Month/Year":
        if sel_month != "All":
            month_int = months.index(sel_month)
        if sel_year != "All":
            year_int = int(sel_year)

    sel_time_scope = st.session_state.get("key_time_mode")
    if sel_time_scope == "Specific time range":
        time_from = st.session_state.get("key_time_from")
        time_to = st.session_state.get("key_time_to")
    else:
        time_from = None
        time_to = None

    sel_reserver = st.session_state.get("key_reserver") or ""
    sel_purpose = st.session_state.get("key_purpose") or ""

    try:
        bookings = db.query_bookings(
            room_id=room_id,
            date_mode=sel_date_scope,
            booking_date=date_of_booked,
            month=month_int,
            year=year_int,
            time_from=time_from,
            time_to=time_to,
            reserver=sel_reserver,
            purpose=sel_purpose,
        )
    except Exception:
        bookings = (
            db.get_bookings(),
            room_id,
            sel_date_scope,
            date_of_booked,
            month_int,
            year_int,
            time_from,
            time_to,
            sel_reserver,
            sel_purpose,
        )

    all_bookings_raw = db.get_bookings()

    def row(b):
        return {
            "Room ID": b.room_id,
            "Room": b.room_name,
            "Date": b.booking_date.strftime("%Y-%m-%d"),
            "Start Time": b.start_time.strftime("%H:%M"),
            "End Time": b.end_time.strftime("%H:%M"),
            "Reserver": b.visitor_name,
            "Email": b.visitor_email,
            "Purpose": b.purpose,
            "Created At": b.created_at.strftime("%Y-%m-%d %H:%M"),
            "User Email": b.user_email or "",
        }

    filtered_df = pd.DataFrame([row(b) for b in bookings])
    all_df = pd.DataFrame([row(b) for b in all_bookings_raw])

    with col2:
        st.subheader("Filtered results")
        if filtered_df.empty:
            st.info("No bookings found with the selected filters.", icon="🔍")
        else:
            st.dataframe(filtered_df, use_container_width=True)
        st.markdown(
            f"Showing {len(filtered_df)} filtered booking(s) out of {len(all_df)} total.",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.subheader("All bookings")
        if all_df.empty:
            st.info("No bookings in the system.", icon="🔍")
        else:
            st.dataframe(all_df, use_container_width=True)
