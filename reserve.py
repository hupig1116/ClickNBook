
import streamlit as st
from datetime import date, datetime, timedelta, time
import time as time_mod
import db

def _is_admin(user):
    if not user:
        return False
    if user.short_name == "admin":
        return True
    db.get_admins()
    return db.is_admin_check(user.short_name)

## Login Page ##
@st.dialog("Log in")
def _login_dialog():
    st.info("Please log in to continue.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in"):
        if not username.strip() or not password.strip():
            st.error("Please enter both username and password")
        else:
            if username.strip() == "Admin" and password.strip() == "Admin":
                st.session_state.user = db.Teacher(short_name="admin", full_name="Administrator", email="admin@example.com")
                st.success("Log in successful")
                time_mod.sleep(1.0)
                st.rerun()
            else:
                success = db.verify_login(username.strip(), password.strip())
                if success:
                    st.session_state.user = success
                    st.success("Log in successful")
                    time_mod.sleep(1.0)
                    st.rerun()
                else:
                    st.error("Invalid credentials")

## Admin edit booking Function ##
@st.dialog("Edit Booking")
def _edit_booking_dialog(booking):
    rooms = db.get_all_rooms()
    room_options = {room.id: f"{room.name} (Capacity: {room.capacity})" for room in rooms}
    room_ids = list(room_options.keys())
    room_index = room_ids.index(booking.room_id) if booking.room_id in room_ids else 0
    col1, col2 = st.columns(2)
    with col1:
        new_room_id = st.selectbox("Room", options=room_ids, index=room_index, format_func=lambda i: room_options[i])
        new_date = st.date_input("Date", value=booking.booking_date)
        new_start = st.time_input("Start time", value=booking.start_time)
        new_end = st.time_input("End time", value=booking.end_time)
    with col2:
        new_visitor = st.text_input("Reserver full name", value=booking.visitor_name)
        new_email = st.text_input("Reserver email", value=booking.visitor_email)
        new_purpose = st.text_area("Purpose", value=booking.purpose or "", height="stretch")

    if st.button("Save changes"):
        error_new_booking = []
        if new_start >= new_end:
            error_new_booking.append("End time must be after start time.")
        if not new_visitor.strip():
            error_new_booking.append("Reserver name is required.")
        if not new_email.strip() or "@" not in new_email:
            error_new_booking.append("Valid email is required.")
        if not new_purpose.strip():
            error_new_booking.append("Purpose is required.")
        if error_new_booking:
            for i in error_new_booking:
                st.error(i)
        else:
            if db.is_available_excluding(booking.id, new_room_id, new_date, new_start, new_end):
                ok = db.update_booking(
                    booking_id=booking.id,
                    room_id=new_room_id,
                    visitor_name=new_visitor.strip(),
                    visitor_email=new_email.strip().lower(),
                    booking_date=new_date,
                    start_time=new_start,
                    end_time=new_end,
                    purpose=new_purpose.strip(),
                    user_email=booking.user_email,
                )
                if ok:
                    st.success("Booking updated")
                    time_mod.sleep(0.4)
                    st.rerun()
                else:
                    st.error("Failed to update booking")
            else:
                st.error("The selected time slot conflicts with another booking")

@st.dialog("Delete Booking")
def _delete_booking_dialog(booking):
    st.subheader("Delete Booking")
    st.error(f"Delete booking {booking.visitor_name}'s booking for {booking.room_name} on {booking.booking_date} from {booking.start_time.strftime('%H:%M')} to {booking.end_time.strftime('%H:%M')}?")
    if st.button("Confirm delete"):
        db.delete_booking_by_id(booking.id)
        st.success("Booking deleted")
        time_mod.sleep(0.8)
        st.rerun()
    
###Admin Edit Teacher Functions###
@st.dialog("Edit Teacher")
def _edit_teacher_dialog(record, current_user_short):
    current_short = record["short_name"]
    is_admin_now = db.is_admin_check(current_short)
    col1, col2 = st.columns(2)
    with col1:
        new_short = st.text_input("Username", value=current_short).upper().strip()
        new_full = st.text_input("Full name", value=record["full_name"])
        new_email = st.text_input("Email", value=record["email"] or "")

    with col2:
        new_password = st.text_input("New password (optional)", type="password")
        role_admin = st.checkbox("Grant admin role", value=is_admin_now)

    if st.button("Save changes"):
        error_teacher_updated = []
        if not new_short:
            error_teacher_updated.append("Username is required.")
        if not new_full.strip():
            error_teacher_updated.append("Full name is required.")
        if not new_email.strip() or "@" not in new_email:
            error_teacher_updated.append("Valid email is required.")

        emails = db.list_teachers()
        for short_name, (_, email) in emails.items():
            if email and email.strip().lower() == new_email.strip().lower() and short_name != current_short:
                error_teacher_updated.append("Email is already used by another teacher.")
                break
            
        if error_teacher_updated:
            for i in error_teacher_updated:
                st.error(i)

        elif role_admin and not db.is_admin_check(new_short):
            db.add_admin(new_short)
            st.success("Teacher updated")
            time_mod.sleep(0.4)
            st.rerun()

        elif not role_admin and db.is_admin_check(new_short):
                if new_short == current_user_short:
                    st.error("You cannot remove your own admin role.")
                else:
                    db.remove_admin(new_short)
                    st.success("Teacher updated")
                    time_mod.sleep(0.4)
                    st.rerun()
        else:
            if new_short != current_short:
                ok_rename = db.rename_teacher(current_short, new_short)
                if not ok_rename:
                    st.error("Username already exists.")
                    return
                
            ok_update = db.update_teacher(new_short, new_full.strip(), new_email.strip().lower(), new_password.strip())

            if not ok_update:
                st.error("Failed to update teacher.")
                return
            
            st.success("Teacher updated")
            time_mod.sleep(0.4)
            st.rerun()
  
@st.dialog("Delete Teacher")
def _delete_teacher_dialog(record, current_user_short):
    short = record["short_name"]
    
    st.error(f"Delete teacher {short} ({record['full_name']})?")
    
    if st.button("Confirm delete"):
        if short == current_user_short:
            st.error("You cannot delete your own account.")
        else:
            db.delete_teacher(short)
            st.success("Teacher deleted")
            time_mod.sleep(0.4)
            st.rerun()


###admin_bookings_filters###
def _admin_bookings_filters():
    rooms = db.get_all_rooms()
    room_filter_options = {0: "All Rooms"}
    for room in rooms:
        room_filter_options[room.id] = room.name
    all_bookings = db.get_bookings()
    months = ["All", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = sorted({b.booking_date.year for b in all_bookings})
    years_options = ["All"] + [str(y) for y in years]

    col_filters, col_result = st.columns([3, 7])
    with col_filters:
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
        filtered = db.query_bookings(
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
        filtered = db.get_bookings()
    page_size = st.session_state.get("key_page_size", 10)
    page_index = st.session_state.get("key_page_index", 0)
    total = len(filtered)
    max_index = max(0, (total - 1) // page_size)
    page_index = min(page_index, max_index)
    start = page_index * page_size
    end = start + page_size
    current_page = filtered[start:end]
    with col_result:
        st.subheader("Filtered Bookings")
        st.caption(f"Showing {len(current_page)} of {total} bookings")
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 8])
        with nav_col1:
            if st.button("Prev", disabled=page_index <= 0):
                st.session_state["key_page_index"] = max(0, page_index - 1)
                st.rerun()
        with nav_col2:
            if st.button("Next", disabled=page_index >= max_index):
                st.session_state["key_page_index"] = min(max_index, page_index + 1)
                st.rerun()

    with col_result:
        if db.count_bookings() != 0:
            col_top = st.columns([1, 1, 2.5, 0.8, 0.8])
            with col_top[0]:
                        st.markdown("Time")
            with col_top[1]:
                        st.markdown("Reserver")
            with col_top[2]:
                        st.markdown("Purpose")
            for b in current_page:
                box = st.container(border=True)
                with box:
                    if b.booking_date == date.today():
                        st.markdown(f"<div style='background-color:#e6ffed;padding:8px;border-radius:6px;margin-bottom:8px'><strong> {b.booking_date}: {b.room_name} </strong></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='background-color:#e5ffff;padding:8px;border-radius:6px;margin-bottom:8px'><strong> {b.booking_date}: {b.room_name}</strong></div>", unsafe_allow_html=True)
                    
                    col_top = st.columns([1, 1, 2.5, 0.8, 0.8])
                    with col_top[0]:
                        st.write(f"{b.start_time.strftime('%H:%M')} - {b.end_time.strftime('%H:%M')}")
                    with col_top[1]:
                        st.write(b.visitor_name)
                    with col_top[2]:
                        st.write(b.purpose or "")
                    with col_top[3]:
                        if st.button("Edit", key=f"edit_b_{b.id}",type="primary", width="stretch"):
                            _edit_booking_dialog(b)
                    with col_top[4]:
                        if st.button("Delete", key=f"del_b_{b.id}",type="primary", width="stretch"):
                            _delete_booking_dialog(b)

            @st.dialog("Delete All Bookings")
            def delete_all_bookings_dialog():
                st.error("This will permanently delete all bookings.", icon="⚠️")
                confirm = st.button("Confirm Delete", type="primary", use_container_width=True)

                if confirm:
                    db.delete_booking()
                    st.success("All bookings deleted")
                    time_mod.sleep(0.8)
                    st.rerun()
            if st.button("Delete All Bookings", type="primary", use_container_width=True):
                delete_all_bookings_dialog()
                
        else:
            st.info("No bookings in the system.", icon="🔍")

#### Admin Teacher Management ###
def admin_panel_teacher(user):
    db.get_admins()
    records = db.list_teachers_with_passwords()
    admin_set = set(db.get_admins())
    st.subheader("Teacher Directory")

    if not records:
        st.info("No teachers found.")
    else:
        st.caption(f"Total teachers: {len(records)}")
       
        for r in records:
            is_self = r["short_name"] == user.short_name
            role = "Admin" if r["short_name"] in admin_set else "Teacher"
            header_html = f"<div style='background-color:#fff9e5;padding:8px;border-radius:6px;margin-bottom:8px'><strong>{r['full_name']}</strong>&emsp;&emsp;&emsp;<span style='background:#222;color:#fff;border-radius:4px;padding:2px 6px;font-size:12px'>{role}</span></div>"
            box = st.container(border=True)
            with box:
                st.markdown(header_html, unsafe_allow_html=True)
                col_top = st.columns([2.5, 2.5, 2.5, 0.6, 1])
                with col_top[0]:
                    st.write(r["email"])
                with col_top[1]:
                    st.write(f"{r['short_name']}")
                with col_top[2]:
                    st.write(f"{r['password']}")
                with col_top[3]:
                    if st.button("Edit", key=f"edit_t_{r['short_name']}"):
                        _edit_teacher_dialog(r, user.short_name)
                with col_top[4]:
                    if st.button("Delete", key=f"del_t_{r['short_name']}"):
                        _delete_teacher_dialog(r, user.short_name)

#### Admin Teacher Management - Add New Teacher ###
    st.subheader("Add New Teacher")
    st.caption("Create a new teacher account")
    with st.form("add_teacher"):
        col1, col2 = st.columns(2)
        with col1:
            new_short = st.text_input("Username").upper().strip()
            new_full = st.text_input("Full name")
            new_is_admin = st.checkbox("Grant admin role")

        with col2:
            new_password = st.text_input("Password", type="password")
            new_email = st.text_input("Email")
            tempcol1, tempcol2 = st.columns([3,1])
            with tempcol1:
                st.caption("")
            with tempcol2:
                submit = st.form_submit_button("Add teacher")

        if submit:
            errors = []
            new_short_stripped = new_short.strip()
            new_full_stripped = new_full.strip()
            new_email_stripped = new_email.strip().lower()
            new_password_stripped = new_password.strip()

            if not new_short_stripped:
                errors.append("Username is required.")
            if not new_full_stripped:
                errors.append("Full name is required.")
            if not new_email_stripped or "@" not in new_email_stripped:
                errors.append("Valid email is required.")
            if not new_password_stripped:
                errors.append("Password is required.")

            existing = db.list_teachers() or {}
            if new_short_stripped in existing:
                errors.append("Username already exists.")
            else:
                for sn, (_, em) in existing.items():
                    if em and em.strip().lower() == new_email_stripped:
                        errors.append("Email is already used by another teacher.")
                        break

            if errors:
                for e in errors:
                    st.error(e)
            else:
                short_disp = new_short.strip()
                full_disp = new_full.strip()
                email_disp = new_email.strip().lower()
                role_label = "Admin" if new_is_admin else "Teacher"

                summary_html = f"""
                <div style="background-color:#e5ffff;padding:8px;border-radius:12px;margin-bottom:8px">
                <strong>You are about to add:</strong> {short_disp} ({full_disp})<br>
                <strong>Role:</strong> {role_label}<br>
                <strong>Email:</strong> {email_disp}
                </div>
                """

                @st.dialog("Add Teacher")
                def add_teacher_dialog():
                    st.markdown(summary_html, unsafe_allow_html=True)
                    if st.button("Confirm add"):
                        try:
                            ok = db.create_teacher(short_disp, full_disp, email_disp, new_password.strip())
                            if ok:
                                if new_is_admin:
                                    db.add_admin(short_disp)
                                st.success("Teacher added")
                                time_mod.sleep(0.8)
                                st.rerun()
                            else:
                                st.error("Failed to add teacher")
                        except Exception as e:
                            st.error(f"Failed to add teacher. Username or email may already exist. Details: {e}")

                add_teacher_dialog()




def app():
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center;'>Reserve</h1>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center;'>Find a room that fits your needs.</h6>", unsafe_allow_html=True)

    if "user" not in st.session_state:
        st.session_state.user = None
    user = st.session_state.user

    if user is None:
        _login_dialog()
        st.stop()
    else:
        top_bar = st.columns([7, 1])
        with top_bar[0]:
            st.write(f"Logged in as: **{user.full_name} ({user.short_name})**")
        with top_bar[1]:
            if st.button("Log out"):
                st.session_state.user = None
                st.rerun()

    rooms = db.get_all_rooms()
    if not rooms:
        st.warning("No rooms are available to reserve.")
        return
    st.subheader("Create a Booking")
    st.caption("Fill in the form to reserve a room")

    room_options = {room.id: f"{room.name} (Capacity: {room.capacity if room.capacity is not None else 'N/A'})" for room in rooms}
    options = list(room_options.keys())
    with st.form("reserve"):
        col1, col2 = st.columns([3, 2])
        with col1:
            selected_room_id = st.selectbox("Select Room", options=options, format_func=lambda i: room_options[i])
            booking_date = st.date_input("Booking Date", min_value=date.today(), value=date.today())
            default_start = (datetime.now() + timedelta(hours=1)).time().replace(minute=0, second=0, microsecond=0)
            default_end = (datetime.now() + timedelta(hours=4)).time().replace(minute=0, second=0, microsecond=0)
            start_time = st.time_input("Start Time", value=default_start)
            end_time = st.time_input("End Time", value=default_end)
        with col2:
            reserver_name = st.text_input("Reserver Full Name", value=user.full_name or "")
            reserver_email = st.text_input("Email Address", value=user.email or "")
            purpose = st.text_area("Purpose of Meeting", placeholder="Brief description of the meeting purpose", height=120)
        submitted = st.form_submit_button("Create Booking")

    if submitted:
        errors = []
        if not reserver_name.strip():
            errors.append("Reserver name is required")
        if not reserver_email.strip():
            errors.append("Reserver email is required")
        elif "@" not in reserver_email:
            errors.append("A valid email address is required")
        if start_time >= end_time:
            errors.append("End time must be after start time")
        if not purpose.strip():
            errors.append("Purpose of meeting is required")
        if errors:
            for e in errors:
                st.error(e)
        else:
            if db.is_available(selected_room_id, booking_date, start_time, end_time):
                success = db.create_booking(
                    selected_room_id,
                    reserver_name.strip(),
                    reserver_email.strip(),
                    booking_date,
                    start_time,
                    end_time,
                    purpose.strip(),
                    user_email=user.email if user.short_name != "admin" else None,
                )
                if success:
                    st.success(f"Booking created for {room_options[selected_room_id]} on {booking_date} from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}")
                else:
                    st.error("Failed to create booking. Please try again.")
            else:
                st.error(f"The selected room is not available during {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} on {booking_date}. Please choose a different time slot or room.")

    if _is_admin(user):
        st.markdown("---")
        st.markdown("<h2 style='text-align: center;'>Admin Panel</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>Booking</h3>", unsafe_allow_html=True)
        st.markdown("---")
        _admin_bookings_filters()
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>Teachers</h3>", unsafe_allow_html=True)
        st.markdown("---")
        admin_panel_teacher(user)
