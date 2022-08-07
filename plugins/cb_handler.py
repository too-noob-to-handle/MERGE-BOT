from pyrogram import Client, filters
import asyncio
from bot import *
from pyrogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from helpers import database
from plugins.mergeVideo import mergeNow
from plugins.mergeVideoSub import mergeSub
from plugins.mergeVideoAudio import mergeAudio
import os

from plugins.usettings import userSettings


@Client.on_callback_query()
async def callback_handler(c: Client, cb: CallbackQuery):
    #     await cb_handler.cb_handler(c, cb)
    MERGE_MODE
    # async def cb_handler(c: Client, cb: CallbackQuery):

    if cb.data == "merge":
        await cb.message.edit(
            text="Where do you want to upload?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📤 To Telegram", callback_data="to_telegram"
                        ),
                        InlineKeyboardButton("🌫️ To Drive", callback_data="to_drive"),
                    ],
                    [InlineKeyboardButton("⛔ Cancel ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "to_drive":
        try:
            urc = await database.getUserRcloneConfig(cb.from_user.id)
            await c.download_media(
                message=urc, file_name=f"userdata/{cb.from_user.id}/rclone.conf"
            )
        except Exception as err:
            await cb.message.reply_text("Rclone not Found, Unable to upload to drive")
        if os.path.exists(f"userdata/{cb.from_user.id}/rclone.conf") is False:
            await cb.message.delete()
            await delete_all(root=f"downloads/{cb.from_user.id}/")
            queueDB.update({cb.from_user.id: {"videos": [], "subtitles": []}})
            formatDB.update({cb.from_user.id: None})
            return
        UPLOAD_TO_DRIVE.update({f"{cb.from_user.id}": True})
        await cb.message.edit(
            text="Okay I'll upload to drive\nDo you want to rename? Default file name is **[@BangladeshHoarding]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👆 Default", callback_data="rename_NO"),
                        InlineKeyboardButton("✍️ Rename", callback_data="rename_YES"),
                    ],
                    [InlineKeyboardButton("⛔ Cancel ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "to_telegram":
        UPLOAD_TO_DRIVE.update({f"{cb.from_user.id}": False})
        await cb.message.edit(
            text="How do yo want to upload file",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🎞️ Video", callback_data="video"),
                        InlineKeyboardButton("📁 File", callback_data="document"),
                    ],
                    [InlineKeyboardButton("⛔ Cancel ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "document":
        UPLOAD_AS_DOC.update({f"{cb.from_user.id}": True})
        await cb.message.edit(
            text="Do you want to rename? Default file name is **[@BangladeshHoarding]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👆 Default", callback_data="rename_NO"),
                        InlineKeyboardButton("✍️ Rename", callback_data="rename_YES"),
                    ],
                    [InlineKeyboardButton("⛔ Cancel ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data == "video":
        UPLOAD_AS_DOC.update({f"{cb.from_user.id}": False})
        await cb.message.edit(
            text="Do you want to rename? Default file name is **[@BangladeshHoarding]_merged.mkv**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("👆 Default", callback_data="rename_NO"),
                        InlineKeyboardButton("✍️ Rename", callback_data="rename_YES"),
                    ],
                    [InlineKeyboardButton("⛔ Cancel ⛔", callback_data="cancel")],
                ]
            ),
        )
        return

    elif cb.data.startswith("rclone_"):
        if "save" in cb.data:
            fileId = cb.message.reply_to_message.document.file_id
            print(fileId)
            await c.download_media(
                message=cb.message.reply_to_message,
                file_name=f"./userdata/{cb.from_user.id}/rclone.conf",
            )
            await database.addUserRcloneConfig(cb, fileId)
        else:
            await cb.message.delete()
        return

    elif cb.data.startswith("rename_"):
        if "YES" in cb.data:
            await cb.message.edit(
                "Current filename: **[@BangladeshHoarding]_merged.mkv**\n\nSend me new file name without extension: You have 1 minute"
            )
            res: Message = await c.listen(
                cb.message.chat.id, filters=filters.text, timeout=60
            )
            if res.text:
                new_file_name = f"./downloads/{str(cb.from_user.id)}/{res.text.replace(' ','_')}.mkv"
                await res.delete(True)
                if MERGE_MODE[cb.from_user.id]==1:
                    await mergeNow(c, cb, new_file_name)
                elif MERGE_MODE[cb.from_user.id] == 2:
                    await mergeAudio(c, cb, new_file_name)
                elif MERGE_MODE[cb.from_user.id]==3:
                    await mergeSub(c, cb, new_file_name)
                
            return
        if "NO" in cb.data:
            if MERGE_MODE[cb.from_user.id]==1:
                await mergeNow(
                    c,
                    cb,
                    new_file_name=f"./downloads/{str(cb.from_user.id)}/[@BangladeshHoarding]_merged.mkv",
                )
            elif MERGE_MODE[cb.from_user.id]==2:
                await mergeAudio(
                    c,
                    cb,
                    new_file_name=f"./downloads/{str(cb.from_user.id)}/[@BangladeshHoarding]_merged.mkv",
                )
            elif MERGE_MODE[cb.from_user.id]==3:
                await mergeSub(
                    c,
                    cb,
                    new_file_name=f"./downloads/{str(cb.from_user.id)}/[@BangladeshHoarding]_merged.mkv",
                )

    elif cb.data == "cancel":
        await delete_all(root=f"downloads/{cb.from_user.id}/")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": []}})
        formatDB.update({cb.from_user.id: None})
        await cb.message.edit("Sucessfully Cancelled")
        await asyncio.sleep(5)
        await cb.message.delete(True)
        return

    elif cb.data.startswith("gUPcancel"):
        cmf = cb.data.split("/")
        chat_id, mes_id, from_usr = cmf[1], cmf[2], cmf[3]
        if int(cb.from_user.id) == int(from_usr):
            await c.answer_callback_query(
                cb.id, text="Going to Cancel . . . 🛠", show_alert=False
            )
            gDict[int(chat_id)].append(int(mes_id))
        else:
            await c.answer_callback_query(
                callback_query_id=cb.id,
                text="⚠️ Opps ⚠️ \n I Got a False Visitor 🚸 !! \n\n 📛 Stay At Your Limits !!📛",
                show_alert=True,
                cache_time=0,
            )
        await delete_all(root=f"downloads/{cb.from_user.id}/")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": []}})
        formatDB.update({cb.from_user.id: None})
        return

    elif cb.data.startswith("ch@ng3M0de_"):
        uid = cb.data.split("_")[1]
        mode = int(cb.data.split("_")[2])
        database.setUserMergeMode(uid=int(uid), mode=mode)
        await userSettings(
            cb.message, int(uid), cb.from_user.first_name, cb.from_user.last_name
        )
        return

    elif cb.data == "close":
        await cb.message.delete(True)
        try:
            await cb.message.reply_to_message.delete(True)
        except Exception as err:
            pass

    elif cb.data.startswith("showFileName_"):
        id = int(cb.data.rsplit("_", 1)[-1])
        print(
            queueDB.get(cb.from_user.id)["videos"],
            queueDB.get(cb.from_user.id)["subtitles"],
        )
        sIndex = queueDB.get(cb.from_user.id)["videos"].index(id)
        m = await c.get_messages(chat_id=cb.message.chat.id, message_ids=id)
        if queueDB.get(cb.from_user.id)["subtitles"][sIndex] is None:
            try:
                await cb.message.edit(
                    text=f"File Name: {m.video.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ Remove",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "📜 Add Subtitle",
                                    callback_data=f"addSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 Back", callback_data="back")],
                        ]
                    ),
                )
            except:
                await cb.message.edit(
                    text=f"File Name: {m.document.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ Remove",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "📜 Add Subtitle",
                                    callback_data=f"addSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 Back", callback_data="back")],
                        ]
                    ),
                )
            return
        else:
            sMessId = queueDB.get(cb.from_user.id)["subtitles"][sIndex]
            s = await c.get_messages(chat_id=cb.message.chat.id, message_ids=sMessId)
            try:
                await cb.message.edit(
                    text=f"File Name: {m.video.file_name}\n\nSubtitles: {s.document.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ Remove File",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "❌ Remove Subtitle",
                                    callback_data=f"removeSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 Back", callback_data="back")],
                        ]
                    ),
                )
            except:
                await cb.message.edit(
                    text=f"File Name: {m.document.file_name}\n\nSubtitles: {s.document.file_name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "❌ Remove File",
                                    callback_data=f"removeFile_{str(m.id)}",
                                ),
                                InlineKeyboardButton(
                                    "❌ Remove Subtitle",
                                    callback_data=f"removeSub_{str(sIndex)}",
                                ),
                            ],
                            [InlineKeyboardButton("🔙 Back", callback_data="back")],
                        ]
                    ),
                )
            return

    elif cb.data.startswith("addSub_"):
        sIndex = int(cb.data.split(sep="_")[1])
        vMessId = queueDB.get(cb.from_user.id)["videos"][sIndex]
        rmess = await cb.message.edit(
            text=f"Send me a subtitle file, you have 1 minute",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔙 Back", callback_data=f"showFileName_{vMessId}"
                        )
                    ]
                ]
            ),
        )
        subs: Message = await c.listen(
            cb.message.chat.id, filters="filters.document", timeout=60
        )
        if subs is not None:
            media = subs.document or subs.video
            if media.file_name.rsplit(".")[-1] not in "srt":
                await subs.reply_text(
                    text=f"Please go back first",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🔙 Back", callback_data=f"showFileName_{vMessId}"
                                )
                            ]
                        ]
                    ),
                    quote=True,
                )
                return
            queueDB.get(cb.from_user.id)["subtitles"][sIndex] = subs.id
            await subs.reply_text(
                f"Added {subs.document.file_name}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔙 Back", callback_data=f"showFileName_{vMessId}"
                            )
                        ]
                    ]
                ),
                quote=True,
            )
            await rmess.delete(True)
            print("Added sub to list")
        return

    elif cb.data.startswith("removeSub_"):
        sIndex = int(cb.data.rsplit("_")[-1])
        vMessId = queueDB.get(cb.from_user.id)["videos"][sIndex]
        queueDB.get(cb.from_user.id)["subtitles"][sIndex] = None
        await cb.message.edit(
            text=f"Subtitle Removed Now go back or send next video",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔙 Back", callback_data=f"showFileName_{vMessId}"
                        )
                    ]
                ]
            ),
        )
        print("Sub removed from list")
        return

    elif cb.data == "back":
        await showQueue(c, cb)
        return

    elif cb.data.startswith("removeFile_"):
        sIndex = queueDB.get(cb.from_user.id)["videos"].index(
            int(cb.data.split("_", 1)[-1])
        )
        queueDB.get(cb.from_user.id)["videos"].remove(int(cb.data.split("_", 1)[-1]))
        await showQueue(c, cb)
        return
