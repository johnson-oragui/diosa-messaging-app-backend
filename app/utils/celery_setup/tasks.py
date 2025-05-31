from celery.utils.log import get_task_logger
from sqlalchemy import text, update, select, func
# from asgiref.sync import async_to_sync

from app.database.session import get_sync_session
from app.utils.celery_setup.setup import app
from app.v1.rooms.models import RoomMember
from app.v1.chats.models import Message


RETRY_DELAY = 60  # 60 seconds delay for retry
MAX_RETRIES = 3   # Maximum 3 retries

logger = get_task_logger("tasks")

@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_DELAY)
def update_roommembers_room_data_in_batches(self, room_id: str, new_room_type: str):
    """
    Updates room_type of roommembers in batches after room type is changed.

    Args:
        room_id(str): The room_id which its type has changed.
        new_room_type(str): The new room type.
    Returns:
        None
    """
    print(f"Updating room members for room_id: {room_id} to new_room_type: {new_room_type}")

    # Define batch size
    batch_size = 1000
    try:
        with get_sync_session() as session:
            stmt_count = select(
                func.count(RoomMember.id)
            ).where(
                RoomMember.room_id == room_id
            )
            # Get total number of rows in room_members
            result = session.execute(stmt_count)

            total_room_members = result.scalar()
            print("total_room_members: ", total_room_members)

            # Process in batches
            for offset in range(0, total_room_members, batch_size):
                stmt_one = select(RoomMember.id).where(
                    RoomMember.room_id == room_id,
                ).limit(batch_size).offset(offset)

                result = session.execute(stmt_one)

                member_ids = result.scalars().all()
                # print(f"member_ids: {member_ids}")

                if member_ids:
                    stmt = update(RoomMember).where(
                        RoomMember.id.in_(member_ids)
                    ).values(
                        room_type="private",
                    )
                    session.execute(stmt)
                    session.commit()
    except Exception as exc:
        logger.error(f"Failed to update room members for room_id {room_id}: {exc}")
        print(f"Failed to update room members for room_id {room_id}: {exc}")
        # Retry the task in case of failure
        try:
            raise self.retry(exc=exc, countdown=RETRY_DELAY, max_retries=MAX_RETRIES)
        except self.MaxRetriesExceededError:
            # retry task incase of failure.
            logger.error(f"Max retries exceeded for task {self.request.id}")



@app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_DELAY)
def update_room_messages_room_data_in_batches(self, room_id: str, new_room_type: str):
    """
    Updates room_type of room messsages in batches after room type is changed.

    Args:
        room_id(str): The room_id which its type has changed.
        new_room_type(str): The new room type.
    Returns:
        None
    """
    print(f"Updating room messages for room_id: {room_id} to new_room_type: {new_room_type}")
    # Define batch size
    batch_size = 1000

    try:
        with get_sync_session() as session:
            # Batching logic for messages
            stmt_count = select(
                func.count(Message.id)
            ).where(
                Message.room_id == room_id,
            )
            result = session.execute(stmt_count)

            total_messages = result.scalar()
            print("total_messages: ", total_messages)

            for offset in range(0, total_messages, batch_size):
                stmt_one = select(Message.id).where(
                    Message.room_id == room_id
                ).order_by(
                    Message.id,
                ).limit(
                    batch_size
                ).offset(
                    offset
                )
                result = session.execute(stmt_one)

                message_ids = result.scalars().all()
                # print(f"message_ids: {message_ids}")
                if message_ids:
                    stmt = update(Message).where(
                        Message.id.in_(message_ids)
                    ).values(
                        chat_type="private"
                    )
                    session.execute(stmt)
                    session.commit()
    except Exception as exc:
        logger.error(f"Failed to update room messages for room_id {room_id}: {exc}")
        print(f"Failed to update room messages for room_id {room_id}: {exc}")
        # Retry the task in case of failure
        try:
            raise self.retry(exc=exc, countdown=RETRY_DELAY, max_retries=MAX_RETRIES)
        except self.MaxRetriesExceededError:
            # retry task incase of failure.
            logger.error(f"Max retries exceeded for task {self.request.id}")

# @app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_DELAY)
# def update_roommembers_room_data_in_batches(self, room_id: str, new_room_type: str):
#     async_to_sync(actual_update_roommembers_room_data_in_batches)(self, room_id, new_room_type)

# async def actual_update_roommembers_room_data_in_batches(self, room_id: str, new_room_type: str):
#     """
#     Updates room_type of roommembers in batches after room type is changed.

#     Args:
#         room_id(str): The room_id which its type has changed.
#         new_room_type(str): The new room type.
#     Returns:
#         None
#     """
#     logger.info(f"Updating room members for room_id: {room_id} to new_room_type: {new_room_type}")
#     print("updating room_members_room_type")

#     # Define batch size
#     batch_size = 1000
#     try:
#         async with get_context_session() as session:
#             # Get total number of rows in room_members
#             result = await session.execute(
#                 text(
#                     """
#                     SELECT COUNT(*) FROM chat.roommembers
#                     WHERE room_id = :room_id;
#                     """
#                 ),
#                 {
#                     "room_id": room_id
#                 }
#             )

#             total_room_members = result.scalar()
#             print("total_room_members: ", total_room_members)

#             # Process in batches
#             for offset in range(0, total_room_members, batch_size):
#                 result = await session.execute(
#                     text(
#                         """
#                         SELECT id FROM chat.roommembers
#                         WHERE room_id = :room_id
#                         ORDER BY id
#                         LIMIT :batch_size
#                         OFFSET :offset;
#                         """
#                     ),
#                     {
#                         "room_id": room_id,
#                         "batch_size": batch_size,
#                         "offset": offset,
#                     }
#                 )

#                 member_ids = result.scalars().all()
#                 print(f"member_ids: {member_ids}")

#                 if member_ids:
#                     await session.execute(
#                         text(
#                             """
#                             UPDATE chat.roommembers
#                             SET room_type = :room_type
#                             WHERE id = ANY(:member_ids);
#                             """
#                         ),
#                         {
#                             "room_type": new_room_type,
#                             "member_ids": member_ids,
#                         }
#                     )

#                     await session.commit()
#     except Exception as exc:
#         logger.error(f"Failed to update room members for room_id {room_id}: {exc}")
#         # Retry the task in case of failure
#         try:
#             raise self.retry(exc=exc, countdown=RETRY_DELAY, max_retries=MAX_RETRIES)
#         except self.MaxRetriesExceededError:
#             # retry task incase of failure.
#             logger.error(f"Max retries exceeded for task {self.request.id}")



# @app.task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_DELAY)
# def update_room_messages_room_data_in_batches(self, room_id: str, new_room_type: str):
#     async_to_sync(actual_update_room_messages_room_data_in_batches)(self, room_id, new_room_type)

# async def actual_update_room_messages_room_data_in_batches(self, room_id: str, new_room_type: str):
#     """
#     Updates room_type of room messsages in batches after room type is changed.

#     Args:
#         room_id(str): The room_id which its type has changed.
#         new_room_type(str): The new room type.
#     Returns:
#         None
#     """
#     logger.info(f"Updating room messages for room_id: {room_id} to new_room_type: {new_room_type}")
#     print("updating room_messages_chat_type")
#     # Define batch size
#     batch_size = 1000

#     try:
#         async with get_context_session() as session:
#             # Batching logic for messages
#             result = await session.execute(
#                 text(
#                     """
#                     SELECT COUNT(*) FROM chat.messages WHERE room_id = :room_id;
#                     """
#                 ),
#                 {
#                     "room_id": room_id
#                 }
#             )

#             total_messages = result.scalar()
#             print("total_messages: ", total_messages)

#             for offset in range(0, total_messages, batch_size):
#                 result = await session.execute(text(
#                     """
#                     SELECT id FROM chat.messages
#                     WHERE room_id = :room_id
#                     ORDER BY id
#                     OFFSET :offset
#                     LIMIT :batch_size;
#                     """),
#                     {
#                         "room_id": room_id,
#                         "batch_size": batch_size,
#                         "offset": offset
#                     }
#                 )

#                 message_ids = result.scalars().all()
#                 print(f"message_ids: {message_ids}")
#                 if message_ids:
#                     await session.execute(
#                         text(
#                             """
#                             UPDATE chat.messages
#                             SET chat_type = :chat_type
#                             WHERE id = ANY(:message_ids);
#                             """
#                         ),
#                         {
#                             "chat_type": new_room_type,
#                             "message_ids": message_ids,
#                         }
#                     )
#                     await session.commit()
#     except Exception as exc:
#         logger.error(f"Failed to update room messages for room_id {room_id}: {exc}")
#         print("exc: ", exc)
#         # Retry the task in case of failure
#         try:
#             raise self.retry(exc=exc, countdown=RETRY_DELAY, max_retries=MAX_RETRIES)
#         except self.MaxRetriesExceededError:
#             # retry task incase of failure.
#             logger.error(f"Max retries exceeded for task {self.request.id}")


if __name__ == "__main__":
    pass
