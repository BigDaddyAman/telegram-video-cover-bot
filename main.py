import asyncio
import json
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import Message, MessageEntity

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
    if not message.caption_entities:
        return None

    return json.dumps([
        entity.model_dump(mode="json", exclude_none=True)
        for entity in message.caption_entities
    ])

def restore_caption_entities(data):
    if not data:
        return None

    entities = json.loads(data)

    return [
        MessageEntity.model_validate(entity)
        for entity in entities
    ]

@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    await create_user(user_id, username)

    await message.answer(
        "👋 Welcome!\n\n"
        "🎬 Send me a video, then send the image you'd like "
        "to use as its cover."
    )

def validate_caption_entities(caption, entities):
    if not caption or not entities:
        return None

    caption_length = len(caption.encode("utf-16-le")) // 2
    valid_entities = []

    for entity in entities:
        start = entity.offset
        end = start + entity.length

        if start < 0 or entity.length <= 0 or end > caption_length:
            logger.warning(
                "Skipping invalid caption entity: "
                "type=%s offset=%s length=%s caption_length=%s",
                entity.type,
                start,
                entity.length,
                caption_length,
            )
            continue

        valid_entities.append(entity)

    return valid_entities or None

@dp.message(F.video)
async def handle_video(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    video = message.video

    await create_user(user_id, username)

    caption_entities = serialize_caption_entities(message)

    await update_user(
        user_id,
        state="waiting_for_image",
        video_file_id=video.file_id,
        video_caption=message.caption,
        caption_entities=caption_entities,
        image_file_id=None,
        has_spoiler=bool(message.has_media_spoiler),
    )

    await message.answer(
        "🎬 Video received!\n\n"
        "🖼️ Now send the image you'd like to use as the cover."
    )


@dp.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    await create_user(user_id, username)

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

        entities = validate_caption_entities(
            user["video_caption"],
            entities,
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

    except TelegramAPIError:
        logger.exception("Failed to send video")

        await message.answer(
            "❌ Sorry, I couldn't send the video with that cover.\n"
            "Please try again."
        )

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