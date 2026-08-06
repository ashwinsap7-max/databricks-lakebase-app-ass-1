import os
import streamlit as st
from databricks.sdk import WorkspaceClient
from datetime import datetime

# Initialize Databricks client
w = WorkspaceClient()

# SQL Warehouse configuration
SQL_WAREHOUSE_ID = "50388acf2e5bb865"  # Serverless Starter Warehouse

# Unity Catalog tables
CATALOG = "workspace"
SCHEMA = "support_tickets"

# Helper functions to query Unity Catalog using SDK
def execute_query(query):
    """Execute SQL query using Databricks SDK Statement Execution API"""
    try:
        # Use the SDK's statement execution API (works in Apps environment)
        result = w.statement_execution.execute_statement(
            warehouse_id=SQL_WAREHOUSE_ID,
            statement=query,
            wait_timeout="30s"
        )
        
        # Extract results
        if result.result and result.result.data_array:
            return result.result.data_array
        return []
    except Exception as e:
        st.error(f"Query failed: {str(e)}")
        return []

def get_all_tickets():
    """Fetch all support tickets"""
    query = f"""
        SELECT ticket_id, title, status, created_by, created_at 
        FROM {CATALOG}.{SCHEMA}.tickets 
        ORDER BY created_at DESC
    """
    return execute_query(query)

def get_ticket_messages(ticket_id):
    """Fetch all messages for a specific ticket"""
    query = f"""
        SELECT message_id, message_text, author, created_at 
        FROM {CATALOG}.{SCHEMA}.ticket_messages 
        WHERE ticket_id = {ticket_id} 
        ORDER BY created_at ASC
    """
    return execute_query(query)

def create_ticket(title, status, created_by):
    """Create a new support ticket"""
    try:
        # Get max ticket_id
        max_id_query = f"SELECT COALESCE(MAX(ticket_id), 0) as max_id FROM {CATALOG}.{SCHEMA}.tickets"
        result = execute_query(max_id_query)
        new_id = int(result[0][0]) + 1 if result and result[0] else 1
        
        # Escape single quotes
        safe_title = title.replace("'", "''")
        
        # Insert new ticket
        query = f"""
            INSERT INTO {CATALOG}.{SCHEMA}.tickets 
            VALUES ({new_id}, '{safe_title}', '{status}', '{created_by}', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        """
        execute_query(query)
        return new_id
    except Exception as e:
        st.error(f"Failed to create ticket: {str(e)}")
        return None

def add_message(ticket_id, message_text, author):
    """Add a message to an existing ticket"""
    try:
        # Get max message_id
        max_id_query = f"SELECT COALESCE(MAX(message_id), 0) as max_id FROM {CATALOG}.{SCHEMA}.ticket_messages"
        result = execute_query(max_id_query)
        new_id = int(result[0][0]) + 1 if result and result[0] else 1
        
        # Escape single quotes
        safe_text = message_text.replace("'", "''")
        
        # Insert new message
        query = f"""
            INSERT INTO {CATALOG}.{SCHEMA}.ticket_messages 
            VALUES ({new_id}, {ticket_id}, '{safe_text}', '{author}', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        """
        execute_query(query)
    except Exception as e:
        st.error(f"Failed to add message: {str(e)}")

def update_ticket_status(ticket_id, new_status):
    """Update the status of a ticket"""
    try:
        query = f"""
            UPDATE {CATALOG}.{SCHEMA}.tickets 
            SET status = '{new_status}' 
            WHERE ticket_id = {ticket_id}
        """
        execute_query(query)
    except Exception as e:
        st.error(f"Failed to update status: {str(e)}")

# Streamlit UI
st.set_page_config(page_title="Support Center", page_icon="🎫", layout="wide")
st.title("🎫 Support Ticket Center")

st.success("✅ Connected to Unity Catalog")
st.caption(f"Data Source: `{CATALOG}.{SCHEMA}` (Delta tables)")

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
        
        # Display tickets
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
                new_id = create_ticket(ticket_title, ticket_status, ticket_creator)
                if new_id:
                    st.success(f"Ticket #{new_id} '{ticket_title}' created successfully!")
                    st.balloons()
            else:
                st.error("Please fill in all required fields")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Data Source**  
Catalog: {CATALOG}  
Schema: {SCHEMA}  
Tables: tickets, ticket_messages
""")
