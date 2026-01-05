
import sqlite3
from dataclasses import dataclass
from datetime import datetime, date, time
from typing import List, Optional, Tuple

DB_PATH = "data.db"

@dataclass
class Teacher:
    short_name: str
    full_name: str
    email: str = None

@dataclass
class Room:
    id: int
    name: str
    capacity: Optional[int] = None
    description: Optional[str] = None
    img_url: Optional[str] = None
    equipment: Optional[str] = None

@dataclass
class Booking:
    id: int
    room_id: int
    room_name: str
    booking_date: date
    start_time: time
    end_time: time
    visitor_name: str
    visitor_email: str
    purpose: Optional[str]
    created_at: datetime
    user_email: Optional[str] = None

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _run(query: str, params: tuple = (), fetchone: bool = False, fetchall: bool = False, commit: bool = False):
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        result = None
        if fetchone:
            result = cur.fetchone()
        elif fetchall:
            result = cur.fetchall()
        if commit:
            conn.commit()
        return result

def _column_exists(table: str, column: str) -> bool:
    rows = _run(f"PRAGMA table_info({table})", fetchall=True) or []
    return any(row["name"] == column for row in rows)

def _table_exists(table: str) -> bool:
    r = _run(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
        fetchone=True
    )
    return r is not None

def _create_tables():
    _run(
        """
        CREATE TABLE IF NOT EXISTS teachers (
            short_name TEXT PRIMARY KEY NOT NULL,
            full_name  TEXT NOT NULL,
            email      TEXT NOT NULL
        )
        """,
        commit=True,
    )

    _run(
        """
        CREATE TABLE IF NOT EXISTS rooms (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            capacity    INTEGER,
            description TEXT,
            equipment   TEXT,
            img_url     TEXT
        )
        """,
        commit=True,
    )

    _run(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id       INTEGER NOT NULL,
            short_name    TEXT,
            user_email    TEXT,
            booking_date  TEXT NOT NULL,
            start_time    TEXT NOT NULL,
            end_time      TEXT NOT NULL,
            visitor_name  TEXT NOT NULL,
            visitor_email TEXT NOT NULL,
            purpose       TEXT,
            created_at    TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (room_id)
                REFERENCES rooms(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (short_name)
                REFERENCES teachers(short_name)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        )
        """,
        commit=True,
    )
    _run(
        """
        CREATE TABLE IF NOT EXISTS admins (
            short_name TEXT PRIMARY KEY,
            FOREIGN KEY (short_name) REFERENCES teachers(short_name)
            ON DELETE CASCADE ON UPDATE CASCADE
        )
        """,
        commit=True,
    )
    _run(
            """
            CREATE TABLE IF NOT EXISTS logins (
                short_name TEXT NOT NULL UNIQUE,
                password   TEXT NOT NULL,
                FOREIGN KEY (short_name)
                    REFERENCES teachers(short_name)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            )
            """,
            commit=True,
        )

def _seed_table():
    teachers = [
        ("PSM", "Poon Sin Man", "psm@lkpfc.edu.hk"),
        ("YWY", "Yau Wing Yiu", "ywy@lkpfc.edu.hk"),
        ("YHN", "Yue Hin Nang", "yhn@lkpfc.edu.hk"),
        ("MHC", "Ma Ho Ching", "mhc@lkpfc.edu.hk"),
        ("CYT", "Cheung Yat Tak", "cyt@lkpfc.edu.hk"),
        ("KTL", "Kwok Tsz Ling", "ktl@lkpfc.edu.hk"),
        ("CNY", "Chow Ngo Yin", "cny@lkpfc.edu.hk"),
        ("LHN", "Lee Hiu Nam", "lhn@lkpfc.edu.hk"),
    ]
    for short_name, full_name, email in teachers:
        _run(
            "INSERT OR IGNORE INTO teachers (short_name, full_name, email) VALUES (?, ?, ?)",
            (short_name, full_name, email),
            commit=True,
        )

    logins = [
        ("PSM", "Psm8654#"),
        ("YWY", "Ywy8654!"),
        ("YHN", "yhn8654@"),
        ("MHC", "mhc8654#"),
        ("CYT", "cyt8654!"),
        ("KTL", "ktl8654@"),
        ("CNY", "cny8654#"),
        ("LHN", "lhn8654!"),
    ]
    for short_name, password in logins:
        _run(
            """
            INSERT INTO logins (short_name, password)
            VALUES (?, ?)
            ON CONFLICT(short_name) DO UPDATE SET password = excluded.password
            """,
            (short_name, password),
            commit=True,
        )

    rooms = [
        (101, "Room 101", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/Pz9Lloc.jpg"),
        (102, "Room 102", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/Pz9Lloc.jpg"),
        (103, "Room 103", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/Pz9Lloc.jpg"),
        (104, "Room 104", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/Pz9Lloc.jpg"),
        (201, "Room 201", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/UBaU7gj.jpg"),
        (202, "Room 202", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/UBaU7gj.jpg"),
        (203, "Room 203", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/UBaU7gj.jpg"),
        (204, "Room 204", 30, "A well-equipped classroom, featuring advanced audiovisual technology, ergonomic seating, and an environment conducive to academic excellence.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/UBaU7gj.jpg"),
        (901, "Student Activity Center (SAC)", 200, "A dynamic, versatile space designed for student engagement.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/LUAkUcx.jpg"),
        (902, "Aesthetic Activities Room (AA Room)", 200, "A versatile space for activities and events.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/sO0SIUk.jpg"),
        (903, "School Hall", 700, "A spacious, multi-purpose hall.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/m4fciYI.jpg"),
        (904, "Cover Playground", 500, "A sheltered playground offering weather protection.", "projector, whiteboard, Wi-Fi", "https://i.imgur.com/uhbOBpC.jpg"),
        ]
    
    for room_id, name, capacity, description, equipment, img_url in rooms:
            _run(
                "INSERT OR IGNORE INTO rooms (id, name, capacity, description, equipment, img_url) VALUES (?, ?, ?, ?, ?, ?)",
                (room_id, name, capacity, description, equipment, img_url),
                commit=True,
        )

def _init_db():
    _create_tables()
    _seed_table()

_init_db()

###SQL login###
def verify_login(short_name: str, password: str) -> Optional[Teacher]:
    short = short_name.strip()
    login = _run(
        "SELECT password FROM logins WHERE LOWER(short_name) = LOWER(?)",
        (short,),
        fetchone=True,
    )
    if not login:
        return None
    if password != login["password"]:
        return None
    t = _run(
        "SELECT * FROM teachers WHERE LOWER(short_name) = LOWER(?)",
        (short,),
        fetchone=True,
    )
    if not t:
        return None
    return Teacher(short_name=t["short_name"], full_name=t["full_name"], email=t["email"])

### Booking and Room functions ###
def list_teachers() -> List[Teacher]:
    rows = _run("SELECT * FROM teachers ORDER BY short_name", fetchall=True) or []
    return [Teacher(short_name=r["short_name"], full_name=r["full_name"], email=r["email"]) for r in rows]

def all_login_info() -> List[dict]:
    rows = _run("SELECT * FROM logins", fetchall=True) or []
    return [{"short_name": r["short_name"], "password": r["password"]} for r in rows]

def get_all_rooms() -> List[Room]:
    rows = _run("SELECT * FROM rooms ORDER BY id", fetchall=True) or []
    return [
        Room(
            id=r["id"],
            name=r["name"],
            capacity=r["capacity"],
            description=r["description"],
            equipment=r["equipment"],
            img_url=r["img_url"],
        )
        for r in rows
    ]

def get_bookings(room_id: Optional[int] = None, booking_date_filter: Optional[date] = None) -> List[Booking]:
    q = "SELECT b.*, r.name AS room_name FROM bookings b JOIN rooms r ON r.id = b.room_id"
    clauses = []
    params: tuple = ()
    if room_id is not None:
        clauses.append("b.room_id = ?")
        params += (room_id,)
    if booking_date_filter is not None:
        clauses.append("b.booking_date = ?")
        params += (booking_date_filter.isoformat(),)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY b.booking_date, b.start_time"
    rows = _run(q, params, fetchall=True) or []
    return [_booking_from_row(r) for r in rows]

def delete_booking() -> None:
    _run("DELETE FROM bookings", (), commit=True)

def count_bookings() -> int:
    r = _run("SELECT COUNT(*) AS cnt FROM bookings", fetchone=True)
    return r["cnt"] if r else 0

def create_booking(
    room_id: int,
    visitor_name: str,
    visitor_email: str,
    booking_date: date,
    start_time: time,
    end_time: time,
    purpose: Optional[str],
    user_email: Optional[str] = None,
) -> bool:
    _run(
        """
        INSERT INTO bookings
        (room_id, user_email, booking_date, start_time, end_time,
         visitor_name, visitor_email, purpose, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            room_id,
            (user_email.strip().lower() if user_email else None),
            booking_date.isoformat(),
            start_time.strftime("%H:%M:%S"),
            end_time.strftime("%H:%M:%S"),
            visitor_name.strip(),
            visitor_email.strip().lower(),
            (purpose or None),
            datetime.now().isoformat(timespec="minutes"),
        ),
        commit=True,
    )
    return True

def _booking_from_row(r: sqlite3.Row) -> Booking:
    keys = set(r.keys())
    return Booking(
        id=r["id"],
        room_id=r["room_id"],
        room_name=r["room_name"],
        booking_date=datetime.strptime(r["booking_date"], "%Y-%m-%d").date(),
        start_time=datetime.strptime(r["start_time"], "%H:%M:%S").time(),
        end_time=datetime.strptime(r["end_time"], "%H:%M:%S").time(),
        visitor_name=r["visitor_name"],
        visitor_email=r["visitor_email"],
        purpose=r["purpose"],
        created_at=datetime.fromisoformat(r["created_at"]),
        user_email=(r["user_email"] if "user_email" in keys else None),
    )

def query_bookings(
    room_id: Optional[int] = None,
    date_mode: str = "All Dates",
    booking_date: Optional[date] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    time_from: Optional[time] = None,
    time_to: Optional[time] = None,
    reserver: Optional[str] = None,
    purpose: Optional[str] = None,
) -> List[Booking]:
    q = (
        "SELECT b.*, r.name AS room_name "
        "FROM bookings b JOIN rooms r ON r.id = b.room_id"
    )
    clauses: List[str] = []
    params: Tuple = ()

    if room_id is not None:
        clauses.append("b.room_id = ?")
        params += (room_id,)

    if date_mode == "Specific Date" and booking_date is not None:
        clauses.append("b.booking_date = ?")
        params += (booking_date.isoformat(),)
    elif date_mode == "Specific Month/Year":
        if year is not None:
            clauses.append("strftime('%Y', b.booking_date) = ?")
            params += (f"{int(year):04d}",)
        if month is not None:
            clauses.append("strftime('%m', b.booking_date) = ?")
            params += (f"{int(month):02d}",)

    if time_from and time_to:
        clauses.append("NOT (b.end_time <= ? OR b.start_time >= ?)")
        params += (time_from.strftime("%H:%M:%S"), time_to.strftime("%H:%M:%S"))
    elif time_from:
        clauses.append("b.end_time > ?")
        params += (time_from.strftime("%H:%M:%S"),)
    elif time_to:
        clauses.append("b.start_time < ?")
        params += (time_to.strftime("%H:%M:%S"),)

    if reserver:
        clauses.append("LOWER(b.visitor_name) LIKE ?")
        params += (f"%{reserver.strip().lower()}%",)
    if purpose:
        clauses.append("LOWER(b.purpose) LIKE ?")
        params += (f"%{purpose.strip().lower()}%",)

    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY b.booking_date, b.start_time"

    rows = _run(q, params, fetchall=True) or []
    return [_booking_from_row(r) for r in rows]

def is_available(room_id: int, booking_date: date, start_time: time, end_time: time) -> bool:
    q = (
        "SELECT 1 FROM bookings "
        "WHERE room_id = ? AND booking_date = ? "
        "AND NOT (end_time <= ? OR start_time >= ?)"
    )
    params = (
        room_id,
        booking_date.isoformat(),
        start_time.strftime("%H:%M:%S"),
        end_time.strftime("%H:%M:%S"),
    )
    row = _run(q, params, fetchone=True)
    return row is None

def update_booking(
    booking_id: int,
    room_id: int,
    visitor_name: str,
    visitor_email: str,
    booking_date: date,
    start_time: time,
    end_time: time,
    purpose: Optional[str],
    user_email: Optional[str] = None,
) -> bool:
    _run(
        """
        UPDATE bookings
        SET room_id = ?, user_email = ?, booking_date = ?, start_time = ?, end_time = ?,
            visitor_name = ?, visitor_email = ?, purpose = ?
        WHERE id = ?
        """,
        (
            room_id,
            (user_email.strip().lower() if user_email else None),
            booking_date.isoformat(),
            start_time.strftime("%H:%M:%S"),
            end_time.strftime("%H:%M:%S"),
            visitor_name.strip(),
            visitor_email.strip().lower(),
            (purpose or None),
            booking_id,
        ),
        commit=True,
    )
    return True

def delete_booking_by_id(booking_id: int) -> bool:
    _run("DELETE FROM bookings WHERE id = ?", (booking_id,), commit=True)
    return True

def is_available_excluding(
    booking_id: int,
    room_id: int,
    booking_date: date,
    start_time: time,
    end_time: time,
) -> bool:
    q = (
        "SELECT 1 FROM bookings "
        "WHERE room_id = ? AND booking_date = ? AND id != ? "
        "AND NOT (end_time <= ? OR start_time >= ?)"
    )
    params = (
        room_id,
        booking_date.isoformat(),
        booking_id,
        start_time.strftime("%H:%M:%S"),
        end_time.strftime("%H:%M:%S"),
    )
    row = _run(q, params, fetchone=True)
    return row is None

### Admin role functions ###
def get_admins() -> List[str]:
    rows = _run("SELECT short_name FROM admins", fetchall=True) or []
    return [r["short_name"] for r in rows]

def add_admin(short_name: str) -> bool:
    _run("INSERT OR IGNORE INTO admins (short_name) VALUES (?)", (short_name,), commit=True)
    return True

def remove_admin(short_name: str) -> bool:
    _run("DELETE FROM admins WHERE short_name = ?", (short_name,), commit=True)
    return True

def is_admin_check(short_name: str) -> bool:
    r = _run("SELECT 1 FROM admins WHERE short_name = ?", (short_name,), fetchone=True)
    return r is not None

### Teacher management functions ###
def list_teachers_with_passwords() -> List[dict]:
    teachers = list_teachers() or []
    logins = all_login_info() or []
    pw_map = {r["short_name"]: r["password"] for r in logins}
    return [{"short_name": t.short_name, "full_name": t.full_name, "email": t.email, "password": pw_map.get(t.short_name)} for t in teachers]

def create_teacher(short_name: str, full_name: str, email: str, password: str) -> bool:
    _run(
        "INSERT INTO teachers (short_name, full_name, email) VALUES (?, ?, ?)",
        (short_name, full_name, email),
        commit=True,
    )
    _run(
        """
        INSERT INTO logins (short_name, password)
        VALUES (?, ?)
        ON CONFLICT(short_name) DO UPDATE SET password = excluded.password
        """,
        (short_name, password),
        commit=True,
    )
    return True

def update_teacher(short_name: str, full_name: str, email: str, password: Optional[str] = None) -> bool:
    _run(
        "UPDATE teachers SET full_name = ?, email = ? WHERE short_name = ?",
        (full_name, email, short_name),
        commit=True,
    )
    if password and password.strip():
        _run(
            "UPDATE logins SET password = ? WHERE short_name = ?",
            (password.strip(), short_name),
            commit=True,
        )
    return True

def rename_teacher(old_short_name: str, new_short_name: str) -> bool:
    r = _run("SELECT 1 FROM teachers WHERE short_name = ?", (new_short_name,), fetchone=True)
    if r:
        return False
    _run(
        "UPDATE teachers SET short_name = ? WHERE short_name = ?",
        (new_short_name, old_short_name),
        commit=True,
    )
    return True

def delete_teacher(short_name: str) -> bool:
    _run("DELETE FROM teachers WHERE short_name = ?", (short_name,), commit=True)
    return True



