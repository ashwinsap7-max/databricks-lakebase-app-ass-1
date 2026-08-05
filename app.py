import os
import uuid
import time
import streamlit as st
from sqlalchemy import create_engine, text, event
from databricks.sdk import WorkspaceClient
from datetime import datetime

# Initialize Databricks client
w = WorkspaceClient()

# Database configuration from environment variables
db_host = os.environ.get('PGHOST')
db_name = os.environ.get('PGDATABASE', 'support-system')
db_user = os.environ.get('PGUSER')
db_port = os.environ.get('PGPORT', 5432)

# Global password management for token refresh
postgres_password = None
last_password_refresh = 0

# Create SQLAlchemy engine
engine = create_engine(
    f"postgresql+psycopg2://{db_user}:@{db_host}:{db_port}/{db_name}"
)

@event.listens_for(engine, "do_connect")
def provide_token(dialect, conn_rec, cargs, cparams):
    """Auto-refresh OAuth token every 15 minutes"""
    global postgres_password, last_password_refresh
    if postgres_password is None or time.time() - last_password_refresh > 900:
        cred = w.database.generate_database_credential(
            request_id=str(uuid.uuid4()),
            instance_names=[db_name]
        )
        postgres_password = cred.token
        last_password_refresh = time.time()
    cparams["password"] = postgres_password
    cparams["sslmode"] = "require"

# Helper functions
def get_all_tickets():
    """Fetch all support tickets"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT ticket_id, title, status, created_by, created_at 
            FROM service_mgmt.tickets 
            ORDER BY created_at DESC
        """))
        return result.fetchall()

def get_ticket_messages(ticket_id):
    """Fetch all messages for a specific ticket"""
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT message_id, message_text, author, created_at 
                FROM service_mgmt.ticket_messages 
                WHERE ticket_id = :ticket_id 
                ORDER BY created_at ASC
            """),
            {"ticket_id": ticket_id}
        )
        return result.fetchall()

def create_ticket(title, status, created_by):
    """Create a new support ticket"""
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO service_mgmt.tickets (title, status, created_by) 
                VALUES (:title, :status, :created_by)
            """),
            {"title": title, "status": status, "created_by": created_by}
        )
        conn.commit()

def add_message(ticket_id, message_text, author):
    """Add a message to an existing ticket"""
    with engine.connect() as conn:
        conn.execute(
            text("""
                INSERT INTO service_mgmt.ticket_messages (ticket_id, message_text, author) 
                VALUES (:ticket_id, :message_text, :author)
            """),
            {"ticket_id": ticket_id, "message_text": message_text, "author": author}
        )
        conn.commit()

def update_ticket_status(ticket_id, new_status):
    """Update the status of a ticket"""
    with engine.connect() as conn:
        conn.execute(
            text("""
                UPDATE service_mgmt.tickets 
                SET status = :status 
                WHERE ticket_id = :ticket_id
            """),
            {"ticket_id": ticket_id, "status": new_status}
        )
        conn.commit()

# Streamlit UI
st.set_page_config(page_title="Support Center", page_icon="🎫", layout="wide")
st.title("🎫 Support Ticket Center")

# Sidebar for navigation
page = st.sidebar.radio("Navigation", ["View Tickets", "Create Ticket"])

if page == "View Tickets":
    st.header("All Support Tickets")
    
    # Filter by status
    status_filter = st.selectbox(
        "Filter by Status", 
        ["All", "open", "in_progress", "resolved"]
    )
    
    # Fetch and display tickets
    tickets = get_all_tickets()
    
    if tickets:
        # Filter tickets if needed
        if status_filter != "All":
            tickets = [t for t in tickets if t[2] == status_filter]
        
        # Display tickets in a table
        st.subheader(f"Total Tickets: {len(tickets)}")
        
        for ticket in tickets:
            ticket_id, title, status, created_by, created_at = ticket
            
            with st.expander(f"#{ticket_id} - {title} [{status}]"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Created by:** {created_by}")
                    st.write(f"**Created at:** {created_at}")
                    st.write(f"**Status:** {status}")
                
                with col2:
                    # Update status
                    new_status = st.selectbox(
                        "Update Status",
                        ["open", "in_progress", "resolved"],
                        index=["open", "in_progress", "resolved"].index(status),
                        key=f"status_{ticket_id}"
                    )
                    
                    if st.button("Update", key=f"update_{ticket_id}"):
                        if new_status != status:
                            update_ticket_status(ticket_id, new_status)
                            st.success(f"Status updated to {new_status}")
                            st.rerun()
                
                # Display messages
                st.markdown("---")
                st.subheader("Messages")
                messages = get_ticket_messages(ticket_id)
                
                if messages:
                    for msg in messages:
                        msg_id, msg_text, author, msg_created_at = msg
                        st.markdown(f"**{author}** *({msg_created_at})*")
                        st.write(msg_text)
                        st.markdown("")
                else:
                    st.info("No messages yet")
                
                # Add new message
                st.markdown("---")
                st.subheader("Add a Message")
                
                with st.form(key=f"msg_form_{ticket_id}"):
                    new_message = st.text_area("Message", key=f"msg_text_{ticket_id}")
                    message_author = st.text_input("Your Email", key=f"msg_author_{ticket_id}")
                    
                    if st.form_submit_button("Send Message"):
                        if new_message and message_author:
                            add_message(ticket_id, new_message, message_author)
                            st.success("Message added!")
                            st.rerun()
                        else:
                            st.error("Please fill in all fields")
    else:
        st.info("No tickets found")

elif page == "Create Ticket":
    st.header("Create New Support Ticket")
    
    with st.form("create_ticket_form"):
        ticket_title = st.text_input("Ticket Title *")
        ticket_status = st.selectbox("Initial Status", ["open", "in_progress", "resolved"])
        ticket_creator = st.text_input("Your Email *")
        
        submitted = st.form_submit_button("Create Ticket")
        
        if submitted:
            if ticket_title and ticket_creator:
                create_ticket(ticket_title, ticket_status, ticket_creator)
                st.success(f"Ticket '{ticket_title}' created successfully!")
                st.balloons()
            else:
                st.error("Please fill in all required fields")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Connected to Lakebase Postgres database")