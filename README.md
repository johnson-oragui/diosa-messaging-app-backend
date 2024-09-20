# fastapi-chatroom-with-websocket
Contains project on a chatroom with fastapi and jinja templates/react



### API Flow

1. **User Authentication**:
   - **Login**: Users log in using an authentication system (JWT tokens or OAuth2). 
     - Endpoint: `POST /auth/login`
     - Request: `{ "username": "user1", "password": "password" }`
     - Response: `{ "access_token": "jwt_token", "token_type": "bearer" }`

   - **Signup**: Users register by creating an account.
     - Endpoint: `POST /auth/signup`
     - Request: `{ "username": "user1", "password": "password", "email": "email@example.com" }`
     - Response: `{"message": "User created"}`

   - **Token Authentication for WebSockets**: Every WebSocket connection requires a valid JWT token for the user.
     - Users connect to WebSocket URLs using an Authorization header or token query parameter.

2. **General Chat (Public Chat)**:
   - **Join General Chat**: Anyone can join and send messages in a general chat (for all users).
     - WebSocket Endpoint: `ws://<server>/ws/general`
     - WebSocket Request: 
       - Join message sent to the WebSocket.
       - Incoming messages are broadcasted to all users in the general chat.

   - **Message Persistence**: Store every message in the PostgreSQL database using SQLAlchemy.
     - Message Model: `{ "id": int, "user_id": int, "content": str, "timestamp": datetime, "chat_type": "general" }`
     - Store every incoming message in the `messages` table.

   - **Retrieve Chat History**: Users can fetch the history of general chat messages.
     - Endpoint: `GET /chats/general/history`
     - Request: `{ "limit": 50, "offset": 0 }`
     - Response: `{ "messages": [ { "user_id": 1, "content": "hello", "timestamp": "2024-09-19T10:00:00Z" } ] }`

3. **Private Chats**:
   - **Start Private Chat**: Users can initiate a private chat by sending a request.
     - Endpoint: `POST /chats/private`
     - Request: `{ "receiver_id": 2 }`
     - Response: `{ "chat_id": 1, "status": "created" }`

   - **Send Private Message**: Messages between two users are sent over WebSocket.
     - WebSocket Endpoint: `ws://<server>/ws/private/{chat_id}`
     - WebSocket Message Format: `{ "content": "Hello!", "chat_id": 1 }`

   - **Message Persistence**: Store private chat messages in the database.
     - Message Model: `{ "id": int, "sender_id": int, "receiver_id": int, "content": str, "timestamp": datetime, "chat_type": "private" }`

   - **Retrieve Private Chat History**: Users can fetch the history of their private messages.
     - Endpoint: `GET /chats/private/{chat_id}/history`
     - Response: `{ "messages": [ { "sender_id": 1, "receiver_id": 2, "content": "Hi", "timestamp": "2024-09-19T10:00:00Z" } ] }`

4. **Chat Rooms**:
   - **Create Chat Room**: Any authenticated user can create a chat room.
     - Endpoint: `POST /chats/room`
     - Request: `{ "name": "Room Name", "description": "Room Description" }`
     - Response: `{ "room_id": 1, "invite_link": "http://<server>/chats/room/1/invite" }`

   - **Invite Users via Invite Link**: Users can send invite links to others.
     - WebSocket Endpoint: `ws://<server>/ws/room/{room_id}`
     - Creator has to approve users trying to join using the invite link.
     - Invite Approval: `POST /chats/room/{room_id}/invite/approve`
     - Response: `{ "status": "approved" }`

   - **Join Chat Room**: Users can join a chat room using the invite link.
     - Endpoint: `POST /chats/room/{room_id}/join`
     - Request: `{ "invite_link": "http://<server>/chats/room/1/invite" }`
     - Response: `{ "status": "pending_approval" }`

   - **Send Message in Chat Room**: Once in a room, users can send messages via WebSocket.
     - WebSocket Endpoint: `ws://<server>/ws/room/{room_id}`
     - WebSocket Message Format: `{ "content": "Hello everyone!" }`

   - **Message Persistence**: Store messages in the `room_messages` table in the database.
     - Message Model: `{ "id": int, "room_id": int, "user_id": int, "content": str, "timestamp": datetime, "chat_type": "room" }`

   - **Retrieve Chat Room History**: Users can view previous chat room messages.
     - Endpoint: `GET /chats/room/{room_id}/history`
     - Response: `{ "messages": [ { "user_id": 1, "content": "Welcome!", "timestamp": "2024-09-19T10:00:00Z" } ] }`

### Frontend Flow

1. **Authentication (Login/Register)**:
   - On the login screen, users enter their username and password.
   - **API Call**: `POST /auth/login`
   - If successful, store the JWT token in local storage or a cookie.
   - Redirect the user to the chat dashboard.

2. **General Chat**:
   - On the chat dashboard, there's a section for general chat.
   - When users click the "General Chat" tab, connect to the WebSocket.
     - **Connect**: `ws://<server>/ws/general` with JWT token in the header.
   - Display messages in real-time as they arrive via WebSocket.
   - Users can type and send messages, which will be broadcast to everyone in the general chat.

3. **Private Chats**:
   - In the user dashboard, users can start a private chat by searching for another user.
   - When a private chat starts, open a WebSocket connection:
     - **Connect**: `ws://<server>/ws/private/{chat_id}`
   - Display chat history (fetched from the API) and allow real-time messaging.
   - Messages are sent via WebSocket and displayed instantly in the conversation.

4. **Chat Rooms**:
   - Users can create or join a chat room from the dashboard.
   - **Create Room**: When a user creates a room, they get an invite link to share.
   - **Join Room**: Users can join a room by clicking on the invite link.
     - If approval is required, display a "waiting for approval" message.
     - Once approved, connect to the WebSocket room endpoint:
       - **Connect**: `ws://<server>/ws/room/{room_id}`
   - Display the room's chat history and allow real-time messaging within the room.

5. **Invite and Approve Members in Chat Rooms**:
   - When someone joins a chat room via an invite link, notify the room creator.
   - The creator has a button to approve or deny the new member.
   - Once approved, the new member can start chatting in real-time via WebSocket.

6. **Notification System**:
   - For both private chats and room chats, implement notifications when new messages arrive.
   - This can be done using WebSockets and the `Notification API` on the frontend.
   - Notifications should appear in real-time, alerting users to new messages.

7. **Logout**:
   - When a user logs out, disconnect from all WebSocket connections.
   - Clear the JWT token from storage and redirect the user to the login page.

---

### Database Schema

- **Users Table**: Stores user information (`id`, `username`, `email`, `password_hash`).
- **Messages Table**: Stores general, private, and room messages (`id`, `chat_type`, `sender_id`, `receiver_id`, `room_id`, `content`, `timestamp`).
- **ChatRooms Table**: Stores chat room info (`id`, `creator_id`, `name`, `description`, `invite_link`).
- **RoomMembers Table**: Stores members of chat rooms (`user_id`, `room_id`, `is_approved`).

---

### Tools and Libraries

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, JWT for authentication, WebSockets for real-time messaging.
- **Frontend**: React (or any preferred framework), WebSockets for real-time updates, JWT for authentication.



### **Project Structure**

```
├── backend/                           # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py              # Authentication routes (login/signup)
│   │   │   └── dependencies.py        # Authentication logic (JWT, OAuth, etc.)
│   │   ├── chats/
│   │   │   ├── __init__.py
│   │   │   ├── models.py              # SQLAlchemy models (User, Chat, Message, etc.)
│   │   │   ├── schemas.py             # Pydantic schemas for chat messages
│   │   │   ├── routes.py              # Chat routes (message history, chat room creation, etc.)
│   │   │   └── websocket.py           # WebSocket handlers (general, private, room)
│   │   ├── rooms/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py              # Routes for creating and managing rooms
│   │   │   └── websocket.py           # WebSocket logic for room chats
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── models.py              # User models and database logic
│   │   │   ├── routes.py              # User-specific endpoints (profile, chats, etc.)
│   │   │   └── services.py            # User services (fetch, create, update users)
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── session.py             # SQLAlchemy session and engine
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py              # App settings and configurations (env variables)
│   │   │   ├── dependencies.py        # Common dependencies (DB, authentication)
│   │   │   └── security.py            # Security utilities (JWT handling, password hashing)
│   │   ├── tests/
│   │   │   ├── test_auth.py           # Unit tests for authentication
│   │   │   ├── test_chats.py          # Unit tests for chat functionality
│   │   │   └── test_websocket.py      # Unit tests for WebSocket functionality
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py             # Utility functions (e.g., token handling, data formatting)
│   ├── Dockerfile                     # Docker setup for the FastAPI backend
│   ├── requirements.txt               # Python dependencies (FastAPI, SQLAlchemy, etc.)
│   └── alembic/                       # Alembic migrations directory (for PostgreSQL)
│       ├── env.py
│       └── versions/                  # Versioned migration scripts
├── frontend/                          # Remix frontend
│   ├── app/
│   │   ├── routes/
│   │   │   ├── index.tsx              # Main entry (login/signup or redirect to dashboard)
│   │   │   ├── dashboard.tsx          # Dashboard with general chat, rooms, private chats
│   │   │   ├── chats/
│   │   │   │   ├── $chatId.tsx        # Private chat based on dynamic chatId route
│   │   │   │   └── general.tsx        # General chat route
│   │   │   ├── rooms/
│   │   │   │   ├── $roomId.tsx        # Chat room route (dynamic roomId)
│   │   │   │   └── new.tsx            # Create new room
│   │   ├── components/
│   │   │   ├── ChatInput.tsx          # Reusable chat input component
│   │   │   ├── ChatMessages.tsx       # Reusable component to display chat messages
│   │   │   ├── PrivateChatList.tsx    # List of private chats for a user
│   │   │   └── RoomList.tsx           # List of chat rooms
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts        # Hook to manage WebSocket connections
│   │   │   ├── useChatHistory.ts      # Hook to fetch chat history via loader
│   │   │   └── useAuth.ts             # Hook for authentication-related logic
│   │   ├── styles/
│   │   │   ├── global.css             # Global CSS styles (if not using Tailwind)
│   │   │   └── chat.css               # Styles specific to chat components
│   │   └── utils/
│   │       ├── api.ts                 # API utility functions (fetch requests to backend)
│   │       └── auth.ts                # Utility for handling authentication in Remix
│   ├── public/
│   │   └── favicon.ico                # Public assets (favicon, etc.)
│   ├── Dockerfile                     # Docker setup for Remix frontend
│   ├── package.json                   # Node.js dependencies
│   └── tailwind.config.js             # Tailwind CSS configuration (if using Tailwind)
├── docker-compose.yml                 # Docker Compose for the full stack (FastAPI + Remix + PostgreSQL)
├── .env                               # Environment variables (database URLs, secrets, etc.)
└── README.md                          # Project documentation
```

---

### **Backend (FastAPI)**

1. **Authentication (`auth/`)**
   - Handles JWT-based user authentication, including login, signup, and token management.

2. **Chats (`chats/`)**
   - Includes routes for chat history, sending messages, and WebSocket connections for real-time communication.
   - Models define users, chats, rooms, and messages stored in PostgreSQL.
   
3. **Rooms (`rooms/`)**
   - Manages chat room creation, invites, and handling join requests via WebSocket.

4. **Users (`users/`)**
   - Provides user-specific functionality like fetching user profiles, listing private chats, and roles.

5. **Database (`database/`)**
   - Manages SQLAlchemy engine and sessions.
   - Alembic for migrations.

6. **Core Configurations (`core/`)**
   - Manages app settings, security utilities like JWT handling, and common dependencies.

7. **WebSocket Handling**
   - WebSocket routes (`websocket.py`) to handle real-time message delivery for general, private, and room chats.

### **Frontend (Remix)**

1. **Routes (`routes/`)**
   - **`index.tsx`**: Landing page that directs to login/signup or dashboard if already authenticated.
   - **`dashboard.tsx`**: Main dashboard showing private chats, general chat, and rooms.
   - **Chats**: `chats/$chatId.tsx` and `chats/general.tsx` for individual and general chat.
   - **Rooms**: Room creation (`rooms/new.tsx`) and room chat based on room ID (`rooms/$roomId.tsx`).

2. **Components**
   - Reusable UI components like chat input fields, message displays, and lists of rooms/private chats.

3. **Hooks**
   - Custom hooks like `useWebSocket` for managing WebSocket connections and `useAuth` for handling authentication.

4. **Styles**
   - CSS styles or Tailwind configuration for styling.

5. **API Utilities**
   - API utility functions to make authenticated requests from the frontend to the FastAPI backend.

---

### **Key Integrations**

- **WebSocket Communication**: Use WebSockets for real-time messaging in general chat, private chats, and chat rooms.
- **Authentication**: JWT-based authentication, securely managed on the backend and stored on the frontend.
- **PostgreSQL**: SQLAlchemy models are used to store user messages, chats, and rooms.
- **Remix**: Handles server-side rendering and dynamic data fetching, with hooks managing WebSocket connections and authentication.
- **Docker**: The app is Dockerized with services for FastAPI, PostgreSQL, and the Remix frontend.

---
