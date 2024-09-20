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
