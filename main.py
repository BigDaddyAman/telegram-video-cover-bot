import asyncio
import json
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import Message, MessageEntity, User

from config import BOT_TOKEN
from db import (
    create_user,
    get_user,
    init_db,
    reset_user,
    update_user,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def serialize_caption_entities(message: Message):
    """Convert Telegram caption entities into JSON."""
    if not message.caption_entities:
        return None

    entities = []

    for entity in message.caption_entities:
        data = {
            "offset": entity.offset,
            "length": entity.length,
            "type": entity.type,
            "user": None,
        }

        if entity.type == "text_mention" and entity.user:
            data["user"] = entity.user.model_dump()

        entities.append(data)

    return json.dumps(entities)


def restore_caption_entities(data):
    """Convert stored JSON caption entities back to aiogram objects."""
    if not data:
        return None

    entities = json.loads(data)

    result = []

    for entity in entities:
        user = None

        if entity.get("user"):
            user = User.model_validate(entity["user"])

        result.append(
            MessageEntity(
                type=entity["type"],
                offset=entity["offset"],
                length=entity["length"],
                user=user,
            )
        )

    return result


@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id

    await create_user(user_id)

    await message.answer(
        "👋 Welcome!\n\n"
        "🎬 Send me a video, then send the image you'd like "
        "to use as its cover."
    )


@dp.message(F.video)
async def handle_video(message: Message):
    user_id = message.from_user.id
    video = message.video

    await create_user(user_id)

    caption_entities = serialize_caption_entities(message)

    await update_user(
        user_id,
        state="waiting_for_image",
        video_file_id=video.file_id,
        video_caption=message.caption,
        caption_entities=caption_entities,
        image_file_id=None,
    )

    await message.answer(
        "🎬 Video received!\n\n"
        "🖼️ Now send the image you'd like to use as the cover."
    )


@dp.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id

    user = await get_user(user_id)

    if not user:
        await create_user(user_id)
        user = await get_user(user_id)

    if user["state"] != "waiting_for_image":
        await message.answer(
            "ℹ️ Please send a video first, then send an image "
            "for its cover."
        )
        return

    # Telegram provides multiple sizes of the same photo.
    largest = max(
        message.photo,
        key=lambda photo: photo.file_size or 0,
    )

    await update_user(
        user_id,
        image_file_id=largest.file_id,
    )

    user = await get_user(user_id)

    await message.answer(
        "🖼️ Cover image received!\n"
        "⏳ Creating your video..."
    )

    try:
        entities = restore_caption_entities(
            user["caption_entities"]
        )

        await bot.send_video(
            chat_id=message.chat.id,
            video=user["video_file_id"],
            cover=user["image_file_id"],
            caption=user["video_caption"],
            caption_entities=entities,
            supports_streaming=True,
            has_spoiler=bool(user["has_spoiler"]),
        )

        await message.answer(
            "✅ Done! Your video has been sent with the new cover."
        )

    except TelegramAPIError as e:
        logger.exception("Failed to send video")

        await message.answer(
            "❌ Sorry, I couldn't send the video with that cover.\n"
            "Please try again."
        )

        logger.error(f"Telegram API error: {e}")

    finally:
        await reset_user(user_id)


async def main():
    logger.info("Starting bot...")

    await init_db()

    try:
        await dp.start_polling(bot)

    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")