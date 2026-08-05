# Support Center - Databricks Lakebase App

A full-stack support ticket management application built with Databricks Apps and Lakebase Postgres.

## Features

- **View All Tickets**: Browse and filter support tickets by status (open, in_progress, resolved)
- **Ticket Details**: View complete ticket information and message history
- **Create Tickets**: Submit new support tickets with title, status, and creator information
- **Add Messages**: Post messages to existing tickets for collaboration
- **Update Status**: Change ticket status with a simple dropdown interface

## Architecture

### Backend
- **Database**: Lakebase Postgres (`support-system` database)
- **Schema**: `service_mgmt`
- **Tables**: 
  - `tickets` - Stores ticket information (ticket_id, title, status, created_by, created_at)
  - `ticket_messages` - Stores ticket messages with foreign key to tickets

### Frontend
- **Framework**: Streamlit
- **UI Components**: Expandable tickets, forms, status filters
- **Real-time**: Auto-refresh on data changes

### Integration
- **Connection**: SQLAlchemy with OAuth token auto-refresh
- **Security**: Uses Databricks SDK for credential management
- **Token Refresh**: Automatic every 15 minutes for long-running sessions

## Files

- `app.py` - Main Streamlit application with UI and database logic
- `app.yaml` - Databricks App configuration with Lakebase resource
- `requirements.txt` - Python dependencies

## Database Schema

```sql
-- Tickets table
CREATE TABLE service_mgmt.tickets (
    ticket_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE service_mgmt.ticket_messages (
    message_id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL,
    message_text TEXT,
    author VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticket FOREIGN KEY (ticket_id) 
        REFERENCES service_mgmt.tickets(ticket_id)
);
```

## Deployment

This app is deployed on Databricks Apps V2:
```bash
databricks apps deploy support-center --source-code-path /Workspace/Users/<user>/support-center
```

## Environment Variables

Automatically provided by Databricks Apps when Lakebase is configured:
- `PGHOST` - Database hostname
- `PGDATABASE` - Database name
- `PGUSER` - Username
- `PGPORT` - Port number
- `DATABRICKS_CLIENT_ID` - Service principal client ID