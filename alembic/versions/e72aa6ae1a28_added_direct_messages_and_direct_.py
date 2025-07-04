"""added direct-messages and direct-conversation

Revision ID: e72aa6ae1a28
Revises: 7b9bcdd6e89c
Create Date: 2025-06-07 17:43:31.721615

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e72aa6ae1a28"
down_revision: Union[str, None] = "7b9bcdd6e89c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_type t
                    JOIN pg_enum e ON t.oid = e.enumtypid
                    WHERE t.typname = 'message_status_enum'
                ) THEN
                    CREATE TYPE message_status_enum AS ENUM ('delivered', 'sent');
                END IF;
            END $$;
            """
        )
    )
    op.create_table(
        "chat_direct_conversations",
        sa.Column("sender_id", sa.String(length=60), nullable=True),
        sa.Column("recipient_id", sa.String(length=60), nullable=True),
        sa.Column(
            "is_deleted_for_sender",
            sa.Boolean(),
            server_default="FALSE",
            nullable=False,
        ),
        sa.Column(
            "is_deleted_for_recipient",
            sa.Boolean(),
            server_default="FALSE",
            nullable=False,
        ),
        sa.Column("id", sa.String(length=60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["recipient_id"],
            ["chat_users.id"],
            name=op.f("fk_chat_direct_conversations_recipient_id_chat_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["chat_users.id"],
            name=op.f("fk_chat_direct_conversations_sender_id_chat_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chat_direct_conversations")),
    )
    op.create_index(
        op.f("ix_chat_direct_conversations_created_at"),
        "chat_direct_conversations",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_direct_conversations_id"),
        "chat_direct_conversations",
        ["id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_chat_direct_conversations_recipient_id"),
        "chat_direct_conversations",
        ["recipient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_direct_conversations_sender_id"),
        "chat_direct_conversations",
        ["sender_id"],
        unique=False,
    )
    op.create_index(
        "ix_unique_conversations_sender_id_recipient_id",
        "chat_direct_conversations",
        ["sender_id", "recipient_id"],
        unique=True,
    )
    op.create_table(
        "chat_direct_messages",
        sa.Column("sender_id", sa.String(length=60), nullable=True),
        sa.Column("recipient_id", sa.String(length=60), nullable=True),
        sa.Column("conversation_id", sa.String(length=60), nullable=True),
        sa.Column("parent_message_id", sa.String(length=60), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "delivered", "sent", name="message_status_enum", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("media_url", sa.String(), nullable=True),
        sa.Column("media_type", sa.String(), server_default="text", nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_deleted_for_recipient",
            sa.Boolean(),
            server_default="FALSE",
            nullable=False,
            comment="represents if the message is deleted for recipient user",
        ),
        sa.Column(
            "is_deleted_for_sender",
            sa.Boolean(),
            server_default="FALSE",
            nullable=False,
            comment="represents if the message is deleted for sender user",
        ),
        sa.Column("is_edited", sa.Boolean(), server_default="FALSE", nullable=False),
        sa.Column("id", sa.String(length=60), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["chat_direct_conversations.id"],
            name=op.f(
                "fk_chat_direct_messages_conversation_id_chat_direct_conversations"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["parent_message_id"],
            ["chat_direct_messages.id"],
            name=op.f("fk_chat_direct_messages_parent_message_id_chat_direct_messages"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["recipient_id"],
            ["chat_users.id"],
            name=op.f("fk_chat_direct_messages_recipient_id_chat_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["sender_id"],
            ["chat_users.id"],
            name=op.f("fk_chat_direct_messages_sender_id_chat_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chat_direct_messages")),
    )
    op.create_index(
        op.f("ix_chat_direct_messages_conversation_id"),
        "chat_direct_messages",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_direct_messages_created_at"),
        "chat_direct_messages",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_direct_messages_id"), "chat_direct_messages", ["id"], unique=True
    )
    op.create_index(
        op.f("ix_chat_direct_messages_parent_message_id"),
        "chat_direct_messages",
        ["parent_message_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_direct_messages_recipient_id"),
        "chat_direct_messages",
        ["recipient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_direct_messages_sender_id"),
        "chat_direct_messages",
        ["sender_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_chat_direct_messages_status"),
        "chat_direct_messages",
        ["status"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """
    Downgrade
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("ix_chat_direct_messages_status"), table_name="chat_direct_messages"
    )
    op.drop_index(
        op.f("ix_chat_direct_messages_sender_id"), table_name="chat_direct_messages"
    )
    op.drop_index(
        op.f("ix_chat_direct_messages_recipient_id"), table_name="chat_direct_messages"
    )
    op.drop_index(
        op.f("ix_chat_direct_messages_parent_message_id"),
        table_name="chat_direct_messages",
    )
    op.drop_index(op.f("ix_chat_direct_messages_id"), table_name="chat_direct_messages")
    op.drop_index(
        op.f("ix_chat_direct_messages_created_at"), table_name="chat_direct_messages"
    )
    op.drop_index(
        op.f("ix_chat_direct_messages_conversation_id"),
        table_name="chat_direct_messages",
    )
    op.drop_table("chat_direct_messages")
    op.drop_index(
        "ix_unique_conversations_sender_id_recipient_id",
        table_name="chat_direct_conversations",
    )
    op.drop_index(
        op.f("ix_chat_direct_conversations_sender_id"),
        table_name="chat_direct_conversations",
    )
    op.drop_index(
        op.f("ix_chat_direct_conversations_recipient_id"),
        table_name="chat_direct_conversations",
    )
    op.drop_index(
        op.f("ix_chat_direct_conversations_id"), table_name="chat_direct_conversations"
    )
    op.drop_index(
        op.f("ix_chat_direct_conversations_created_at"),
        table_name="chat_direct_conversations",
    )
    op.drop_table("chat_direct_conversations")
    # ### end Alembic commands ###
