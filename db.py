import aiosqlite

from config import DATABASE_PATH


async def init_db():
    """Create the database and users table if they do not exist."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL;")

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                state TEXT NOT NULL DEFAULT 'idle',
                video_file_id TEXT,
                video_caption TEXT,
                caption_entities TEXT,
                image_file_id TEXT,
                has_spoiler INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        await db.commit()


async def get_user(user_id: int):
    """Get a user from the database."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT *
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        ) as cursor:
            return await cursor.fetchone()


async def create_user(user_id: int, username: str | None = None):
    """Create a user or update their current username."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET username = excluded.username
            """,
            (user_id, username),
        )

        await db.commit()


async def update_user(
    user_id: int,
    *,
    state=None,
    video_file_id=None,
    video_caption=None,
    caption_entities=None,
    image_file_id=None,
    has_spoiler=None,
):
    """Update user data."""
    fields = []
    values = []

    if state is not None:
        fields.append("state = ?")
        values.append(state)

    if video_file_id is not None:
        fields.append("video_file_id = ?")
        values.append(video_file_id)

    if video_caption is not None:
        fields.append("video_caption = ?")
        values.append(video_caption)

    if caption_entities is not None:
        fields.append("caption_entities = ?")
        values.append(caption_entities)

    if image_file_id is not None:
        fields.append("image_file_id = ?")
        values.append(image_file_id)

    if has_spoiler is not None:
        fields.append("has_spoiler = ?")
        values.append(int(has_spoiler))

    if not fields:
        return

    values.append(user_id)

    query = f"""
        UPDATE users
        SET {", ".join(fields)}
        WHERE user_id = ?
    """

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(query, values)
        await db.commit()


async def reset_user(user_id: int):
    """Reset a user's temporary video and cover data."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            UPDATE users
            SET
                state = 'idle',
                video_file_id = NULL,
                video_caption = NULL,
                caption_entities = NULL,
                image_file_id = NULL,
                has_spoiler = 0
            WHERE user_id = ?
            """,
            (user_id,),
        )

        await db.commit()