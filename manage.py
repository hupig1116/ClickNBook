
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

    all_bookings = db.get_bookings()

    months = ["All", "Jan", "Feb", "Mar", "Apr", "May", "Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = sorted({getattr(b, "booking_date").year for b in all_bookings})
    years_options = ["All"] + [str(y) for y in years]

    owner_list = sorted({(getattr(b, "short_name") or "").upper() for b in all_bookings if (getattr(b, "short_name", None) or "").strip()})
    owner_options = ["All"] + owner_list

    DEFAULT_COLS = [
        "Room ID",
        "Room",
        "Date",
        "Start Time",
        "End Time",
        "End User",
        "Email",
        "Purpose",
        "Created At",
        "Owner"
    ]

    if "selected_columns" not in st.session_state:
        st.session_state["selected_columns"] = list(DEFAULT_COLS)
    for col_name in DEFAULT_COLS:
        key_chk = f"chk_{col_name}"
        if key_chk not in st.session_state:
            st.session_state[key_chk] = True

    col_left, col_right = st.columns([3, 7])

    with col_left:
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
                "key_owner",
            ]:
                st.session_state.pop(k, None)
            st.session_state["key_selected_room"] = 0
            st.session_state["key_date_mode"] = "All Dates"
            st.session_state["key_time_mode"] = "All times"
            st.session_state["key_reserver"] = ""
            st.session_state["key_purpose"] = ""
            st.session_state["key_owner"] = "All"

        c1, c2 = st.columns([3, 2])
        with c1:
            st.caption("Filters apply automatically when changed.")
        with c2:
            st.button("Clear filters", use_container_width=True, on_click=clear_filters)

        st.markdown("---")
        st.selectbox(
            "Room",
            options=list(room_filter_options.keys()),
            format_func=lambda x: room_filter_options[x],
            key="key_selected_room",
        )

        date_scope = st.selectbox(
            "Date scope",
            options=["All Dates", "Specific Date", "Specific Month/Year"],
            index=0,
            key="key_date_mode",
        )

        if date_scope == "Specific Date":
            st.date_input(
                "Date",
                value=st.session_state.get("key_date", date.today()),
                key="key_date",
            )
            st.session_state["key_month"] = "All"
            st.session_state["key_year"] = "All"
        elif date_scope == "Specific Month/Year":
            st.selectbox(
                "Month",
                options=months,
                index=months.index(st.session_state.get("key_month", "All")),
                key="key_month",
            )
            st.selectbox(
                "Year",
                options=years_options,
                index=years_options.index(st.session_state.get("key_year", "All")),
                key="key_year",
            )
            st.session_state["key_date"] = None
        else:
            st.session_state["key_date"] = None
            st.session_state["key_month"] = "All"
            st.session_state["key_year"] = "All"

        time_scope = st.selectbox(
            "Time scope",
            options=["All times", "Specific time range"],
            index=0,
            key="key_time_mode",
        )

        if time_scope == "Specific time range":
            ct1, ct2 = st.columns(2)
            with ct1:
                st.time_input(
                    "From",
                    value=st.session_state.get("key_time_from", time(hour=9, minute=0)),
                    key="key_time_from",
                )
            with ct2:
                st.time_input(
                    "To",
                    value=st.session_state.get("key_time_to", time(hour=17, minute=0)),
                    key="key_time_to",
                )

        st.selectbox(
            "Owner contains (Initial)",
            options=owner_options,
            index=owner_options.index(st.session_state.get("key_owner", "All")) if st.session_state.get("key_owner", "All") in owner_options else 0,
            key="key_owner",
        )

        st.text_input(
            "End User name contains",
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
        if sel_month and sel_month != "All":
            month_int = months.index(sel_month)
        if sel_year and sel_year != "All":
            year_int = int(sel_year)

    sel_time_scope = st.session_state.get("key_time_mode")
    if sel_time_scope == "Specific time range":
        time_from = st.session_state.get("key_time_from")
        time_to = st.session_state.get("key_time_to")
    else:
        time_from = None
        time_to = None

    sel_owner = st.session_state.get("key_owner") or "All"
    sel_reserver = st.session_state.get("key_reserver") or ""
    sel_purpose = st.session_state.get("key_purpose") or ""

    owner_filter_value = None if sel_owner == "All" else sel_owner

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
            short_name=owner_filter_value,
        )
    except Exception:
        bookings = db.get_bookings()

    all_bookings_raw = db.get_bookings()

    def row(b):
        start_t = getattr(b, "start_time", None)
        end_t = getattr(b, "end_time", None)
        created_at = getattr(b, "created_at", None)
        booking_date_val = getattr(b, "booking_date", None)
        return {
            "Room ID": getattr(b, "room_id", None),
            "Room": getattr(b, "room_name", None),
            "Date": booking_date_val.strftime("%Y-%m-%d") if booking_date_val else None,
            "Start Time": start_t.strftime("%H:%M") if start_t else None,
            "End Time": end_t.strftime("%H:%M") if end_t else None,
            "End User": getattr(b, "visitor_name", None),
            "Email": getattr(b, "visitor_email", None),
            "Purpose": getattr(b, "purpose", None),
            "Created At": created_at.strftime("%Y-%m-%d %H:%M") if created_at else None,
            "Owner": (getattr(b, "short_name", "") or "").upper(),
        }

    filtered_df = pd.DataFrame([row(b) for b in bookings])
    all_df = pd.DataFrame([row(b) for b in all_bookings_raw])

    with col_right:
        st.subheader("Filtered results")
        no_filters = (
            room_id is None
            and sel_date_scope == "All Dates"
            and st.session_state.get("key_month", "All") in ("All", None)
            and st.session_state.get("key_year", "All") in ("All", None)
            and st.session_state.get("key_time_mode", "All times") == "All times"
            and (st.session_state.get("key_reserver", "") or "") == ""
            and (st.session_state.get("key_purpose", "") or "") == ""
            and (st.session_state.get("key_owner", "All") in ("All", None))
        )

        if filtered_df.empty:
            if no_filters:
                if all_df.empty:
                    st.info("No Bookings in the System.", icon="🔍")
                else:
                    filtered_df = all_df.copy()
            else:
                st.info("No Bookings Found based on your Selected Filters.", icon="🔍")

        top_bar_left, top_bar_right = st.columns(2, vertical_alignment="bottom")
        with top_bar_left:
            st.caption("Columns for Filtered results")
        with top_bar_right:
            with st.popover("Columns", use_container_width= True):
                    sel_cols = st.session_state.get("selected_columns", list(DEFAULT_COLS))
                    if not isinstance(sel_cols, list):
                        try:
                            sel_cols = list(sel_cols)
                        except Exception:
                            sel_cols = list(DEFAULT_COLS)
                    for col_name in DEFAULT_COLS:
                        current = st.session_state.get(f"chk_{col_name}", True)
                        new_val = st.checkbox(col_name, value=current, key=f"chk_{col_name}")
                        if new_val:
                            if col_name not in sel_cols:
                                sel_cols.append(col_name)
                        else:
                            if col_name in sel_cols:
                                sel_cols.remove(col_name)
                    sel_cols = [c for c in DEFAULT_COLS if c in sel_cols]
                    st.session_state["selected_columns"] = sel_cols
                    def _reset_columns():
                        st.session_state["selected_columns"] = list(DEFAULT_COLS)
                        for col_name in DEFAULT_COLS:
                            st.session_state[f"chk_{col_name}"] = True

                    st.button("Reset", use_container_width=True, on_click=_reset_columns)

        show_cols = [c for c in list(st.session_state["selected_columns"]) if c in filtered_df.columns]
        if not show_cols:
            show_cols = [c for c in DEFAULT_COLS if c in filtered_df.columns]

        st.dataframe(filtered_df[show_cols], use_container_width=True)

        st.markdown(
            f"Showing {len(filtered_df)} booking(s) out of {len(all_df)} total.",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.subheader("All bookings")
        st.dataframe(all_df[[c for c in DEFAULT_COLS if c in all_df.columns]], use_container_width=True)
