import asyncio
import tempfile
import typing
from ... import database, shared, common, constants
from .messages import kyc_steps, UserPayload, bot_utils, add_new_temp_driver
from telethon import TelegramClient, events, Button, types, utils, functions
from telethon.errors import rpcerrorlist
from telethon.tl import patched
from tortoise.queryset import Q

import logging
import os

logger = logging.getLogger("drivers.callbacks")
callback_data_binds = {}


def cb_handler(data: str):
    def decorator(
            func: typing.Callable[
                [events.CallbackQuery.Event, str, database.User], typing.Awaitable[None]
            ]
    ):
        global callback_data_binds
        callback_data_binds[data] = {"f": func}
        return func

    return decorator


@cb_handler("start")
async def cb_start_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    if "clear" in data:
        user_state = await user.get_state(await event.client.get_peer_id("me"))
        user_state.payload = ""
        for step, step_data in kyc_steps.items():
            # we want to clear all files that may be uploaded
            if step_data.response_type != common.ResponseType.PHOTO:
                continue
        user_state.value = {}
        await user_state.save()
    driver = await user.get_driver()
    if driver.pending:
        await event.edit(user.loc.drivers_your_application_is_pending_text)
        return
    if driver.confirmed:
        if driver.is_subscribed:
            await event.edit(
                user.loc.drivers_you_are_already_a_driver_has_sub_text.format(
                    sub_end_date=driver.subscription_until.strftime("%d %B %Y"),
                    invite_link=shared.config.driver_group_invite_link,
                )
            )
            return
        await event.edit(
            user.loc.drivers_you_are_already_a_driver_no_sub_text,
            buttons=user.loc.drivers_begin_payment_button,
        )
        return
    await event.edit(
        user.loc.drivers_please_complete_the_registration_text,
        buttons=user.loc.drivers_start_registration_button,
    )


@cb_handler("lang")
async def cb_lang_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    user.lang_code = data.split("|")[1]
    await user.save()
    await cb_start_handler(event, data, user)


@cb_handler("start_registration")
async def cb_start_registration_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    driver = await user.get_driver()
    if driver.pending or driver.confirmed:
        await cb_start_handler(event, data, user)
        return
    first_question_key, first_question = list(kyc_steps.items())[0]
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = UserPayload.kyc_step
    state.value = {
        "step": first_question_key,
        "data": {},
    }
    await state.save()
    await event.edit(
        first_question.get_text(user),
        buttons=Button.inline(user.loc.cancel_btntext, data="start|clear"),
    )


@cb_handler("kyc_goto_step")
async def cb_kyc_goto_step_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    driver = await user.get_driver()
    if driver.pending or driver.confirmed:
        await cb_start_handler(event, data, user)
        return
    question_key = data.split("|")[1]
    question = kyc_steps[question_key]
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = UserPayload.kyc_step
    state.value["step"] = question_key
    await state.save()
    kyc_steps_keys = list(kyc_steps.keys())
    is_first = question_key == kyc_steps_keys[0]

    buttons = []
    if not is_first:
        buttons.append(
            [
                Button.inline(
                    user.loc.prev_step_btntext,
                    data=f"kyc_goto_step|"
                         + kyc_steps_keys[kyc_steps_keys.index(question_key) - 1],
                )
            ]
        )

    buttons.append([Button.inline(user.loc.cancel_btntext, data="start|clear")])

    await event.edit(
        question.get_text(user),
        buttons=buttons,
    )


@cb_handler("kyc_category")
async def cb_kyc_category_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    state = await user.get_state(await event.client.get_peer_id("me"))
    changed_category = int(data.split("|")[1])

    if changed_category in state.value["data"]["categories"]:
        state.value["data"]["categories"].remove(changed_category)
    else:
        state.value["data"]["categories"].append(changed_category)

    await state.save()
    all_enabled_categories = await database.CabCategory.filter(enabled=True)
    buttons = []
    for category in all_enabled_categories:
        buttons.append(
            [
                Button.inline(
                    (
                        "❌ "
                        if category.id not in state.value["data"]["categories"]
                        else "✅ "
                    )
                    + category.name,
                    data=f"kyc_category|{category.id}",
                )
            ]
        )
    if len(state.value["data"]["categories"]) > 0:
        buttons.append(
            [
                Button.inline(
                    user.loc.finish_btntext,
                    data=f"finish_kyc",
                )
            ]
        )
    last_step = list(kyc_steps.keys())[-1]
    buttons.append(
        [
            Button.inline(
                user.loc.prev_step_btntext,
                data=f"kyc_goto_step|{last_step}",
            )
        ]
    )
    buttons.append([Button.inline(user.loc.cancel_btntext, data="start|clear")])
    await event.edit(
        user.loc.drivers_please_select_categories_text,
        buttons=buttons,
    )


@cb_handler("finish_kyc")
async def cb_finish_kyc_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    asyncio.create_task(
        bot_utils.send_user_to_privacy_share_group(event.client, event.get_sender())
    )
    state = await user.get_state(await event.client.get_peer_id("me"))
    await event.answer(user.loc.please_wait_text)
    sender_entity = await event.client.get_entity(event.sender_id)
    full_sender_entity = await event.client(
        functions.users.GetFullUserRequest(sender_entity)
    )
    from_info = bot_utils.get_max_user_info(sender_entity, full_sender_entity)
    categories = ", ".join(
        [
            (await database.CabCategory.get(id=category_id)).name
            for category_id in state.value["data"]["categories"]
        ]
    )

    kyc_data = state.value["data"]

    text_to_owner = f"""
New submission:
From:
 {from_info}
Categories:
 {categories}
Full name: {kyc_data["full_name"]}
Vehicle number: {kyc_data["vehicle_number"]}
Phone number: {kyc_data["phone"]}
Vehicle name: {kyc_data["vehicle_name"]}
"""
    client: TelegramClient = event.client
    sent = await client.send_file(
        shared.config.owner_id,
        file=[kyc_data["aadhar_card_photo"], kyc_data["car_photo"]]
    )
    await client.send_message(
        shared.config.owner_id,
        text_to_owner,
        buttons=[
            [Button.inline("Approve ✅", data=f"approve_kyc|{user.user_id}")],
            [Button.inline("Reject ❌", data=f"reject_kyc|{user.user_id}")],
        ],
        reply_to=sent[-1],
    )

    driver = await user.get_driver()
    driver.car_photo = kyc_data["car_photo"]
    driver.pending = True
    driver.vehicle_name = kyc_data["vehicle_name"]
    driver.vehicle_number = kyc_data["vehicle_number"]
    driver.phone = kyc_data["phone"]
    driver.full_name = kyc_data["full_name"]
    user.full_name = kyc_data["full_name"]
    user.phone_number = kyc_data["phone"]
    await user.save()
    # driver.categories is many to many relation
    to_set = await database.CabCategory.filter(
        id__in=state.value["data"]["categories"],
    )

    await driver.categories.clear()
    await driver.categories.add(*to_set)

    await driver.save()
    await event.edit(user.loc.drivers_thank_you_for_submission_text)
    state.payload = ""
    state.value = {}
    await state.save()


@cb_handler("approve_kyc")
async def cb_approve_kyc_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    user_id = int(data.split("|")[1])
    driver_user = await database.User.get(user_id=user_id)
    driver = await driver_user.get_driver()
    driver.pending = False
    driver.confirmed = True
    await driver.save()
    await event.answer("✅")
    await event.edit(buttons=None)
    await event.reply("Approved ✅")
    if not driver.is_subscribed:
        await event.client.send_message(
            driver_user.user_id,
            driver_user.loc.drivers_kyc_application_approved_no_sub_text,
            buttons=user.loc.drivers_begin_payment_button,
        )
        return
    await event.client.send_message(
        driver_user.user_id,
        driver_user.loc.drivers_kyc_application_approved_has_sub_text.format(
            group_link=shared.config.driver_group_invite_link
        ),
    )


@cb_handler("reject_kyc")
async def cb_reject_kyc_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    user_id = int(data.split("|")[1])
    driver_user = await database.User.get(user_id=user_id)
    driver = await driver_user.get_driver()
    driver.pending = False
    driver.confirmed = False
    await driver.save()
    await event.answer("✅")
    await event.edit(buttons=None)
    await event.reply("Rejected ❌")
    await event.client.send_message(
        driver_user.user_id,
        driver_user.loc.drivers_kyc_application_rejected_text,
    )


@cb_handler("begin_payment")
async def cb_begin_payment_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    has_refs_for_50_off = await database.ReferralPoint.can_redeem_x_points(
        user, constants.Constants.referrals_50_percent_off_driver_sub
    )
    has_refs_for_100_off = await database.ReferralPoint.can_redeem_x_points(
        user, constants.Constants.referrals_100_percent_off_driver_sub
    )
    buttons = [[user.loc.buy_with_upi_button]]
    if has_refs_for_50_off:
        buttons.append([user.loc.buy_with_50_percent_off_button])
    if has_refs_for_100_off:
        buttons.append([user.loc.buy_with_100_percent_off_button])
    await event.edit(user.loc.payment_description, buttons=buttons)


@cb_handler("buy_with_upi")
async def cb_buy_with_upi_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    discount = 0
    if "|" in data:
        discount = int(data.split("|")[1])
    discount_mult = 1 - (discount / 100)
    after_discount = int(constants.Constants.driver_subscription_cost * discount_mult)
    asyncio.create_task(event.delete())
    asyncio.create_task(event.answer(user.loc.please_wait_text))
    with tempfile.TemporaryFile(suffix=".png") as f:
        uri = bot_utils.build_url(
            "upi://pay",
            {
                "pa": shared.config.upi_id,
                "pn": shared.config.upi_name,
                "am": after_discount,
                "cu": "INR",
                "tn": f"Subscription-{user.user_id}",
            },
        )
        bot_utils.write_qr_code(uri, f)
        f.seek(0)
        uploaded = await shared.drivers_bot.upload_file(
            f,
            file_name="qr.png",
        )
        await shared.drivers_bot.send_file(
            user.user_id,
            caption=user.loc.drivers_payment_subscription_text.format(
                AMOUNT=after_discount
            ),
            file=uploaded,
            attributes=[types.DocumentAttributeFilename("qr.png")],
            buttons=Button.inline(
                user.loc.drivers_payed_btntext,
                data=f"payed|{discount}|{after_discount}",
            ),
        )


@cb_handler("payed")
async def cb_payed_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    asyncio.create_task(
        bot_utils.send_user_to_privacy_share_group(event.client, event.get_sender())
    )
    discount, after_discount = (int(x) for x in data.split("|")[1:])

    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = UserPayload.subscription_payment
    state.value = {"discount": discount, "after_discount": after_discount}
    await state.save()
    await event.respond(user.loc.drivers_please_provide_payment_proof_text)


@cb_handler("accept_subscription_payment")
async def cb_accept_subscription_payment_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    user_id, message_id, discount = (int(x) for x in data.split("|")[1:])
    target_user = await database.User.get(user_id=user_id)
    target_driver = await target_user.get_driver()
    if discount == 50:
        await database.ReferralPoint.redeem_x_points(
            target_user, constants.Constants.referrals_50_percent_off_driver_sub
        )
    await event.answer(user.loc.please_wait_text)
    await target_driver.set_subscribed()
    asyncio.create_task(event.edit(buttons=None))
    await event.reply("✅ Payment accepted")
    await event.client.send_message(
        target_user.user_id,
        target_user.loc.drivers_payment_proof_verified_text.format(
            group_link=shared.config.driver_group_invite_link
        ),
        reply_to=message_id,
    )


@cb_handler("reject_subscription_payment")
async def cb_reject_subscription_payment_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    user_id, message_id = (int(x) for x in data.split("|")[1:])
    await event.answer(user.loc.please_wait_text)
    target_user = await database.User.get(user_id=user_id)
    asyncio.create_task(event.edit(buttons=None))
    await event.reply("❌ Payment rejected")
    await event.client.send_message(
        target_user.user_id,
        target_user.loc.drivers_payment_proof_rejected_text,
        reply_to=message_id,
    )


@cb_handler("buy_with_100_percent_off")
async def cb_buy_with_100_percent_off_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    # just process as if owner allowed payment
    await database.ReferralPoint.redeem_x_points(
        user, constants.Constants.referrals_100_percent_off_driver_sub
    )
    target_driver = await user.get_driver()
    await target_driver.set_subscribed()
    await event.edit(
        user.loc.drivers_payment_proof_verified_text.format(
            group_link=shared.config.driver_group_invite_link
        ),
    )


accept_ride_lock = asyncio.Lock()


@cb_handler("accept_ride")
async def cb_accept_ride_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    ride_id = int(data.split("|")[1])
    driver = await user.get_driver()
    if not driver.is_subscribed:
        await event.answer(user.loc.drivers_please_pay_subscription_text, alert=True)
        return
    async with accept_ride_lock:
        ride = await database.Ride.get(id=ride_id)
        # ride_to_send = ride
        # rides = await database.Ride.filter(group_message_id=ride.group_message_id)
        if ride.status != database.RideStatus.SENT_TO_DRIVERS:
            await event.answer(user.loc.drivers_ride_already_accepted_text)
            return
        #todo: code modified
        ride.status = database.RideStatus.WAITING_UPDATION
        await ride.save()
        ride.driver = driver
        # for ride in rides:
        if driver.is_vendor:
            buttons = [[Button.inline("Update driver", data=f"update_ride|{ride.driver_id}|{ride.id}")]]
        else:
            buttons = None
            ride.status = database.RideStatus.ACCEPTED_BY_DRIVER
            return_ride = await database.Ride.filter(first_ride_id=ride.id)
            for i in return_ride:
                i.group_message_id = ride.group_message_id
                i.driver_id = ride.driver_id
                i.status = database.RideStatus.ACCEPTED_BY_DRIVER
                await i.save()
        await ride.save()
    try:
        await shared.drivers_bot.send_message(
            user.user_id,
            user.loc.drivers_you_have_successfully_accepted_the_ride_text.format(
                user_details=bot_utils.get_max_user_info(
                    await shared.riders_bot.get_entity(ride.user_id)
                ),
                drive_details=await ride.text_for_driver(user),
            ),buttons = buttons
        )

    except Exception as e:
        logger.exception(e)
        ride.status = database.RideStatus.SENT_TO_DRIVERS
        ride.driver = None
        await ride.save()
        await event.answer(user.loc.drivers_i_could_not_message_you_text)
        return
    asyncio.create_task(database.ReferralPoint.mark_if_needed(ride))
    await event.delete()
    # todo : new code added
    if ride.driver.is_vendor:
        return
    m = await shared.riders_bot.send_message(
        ride.user_id,
        user.loc.riders_user_drive_details_text.format(
            driver_details=bot_utils.get_max_user_info(
                await shared.drivers_bot.get_entity(user.user_id)
            ),
            id=ride.id,
            driver_phone_number=driver.phone,
            driver_full_name=driver.full_name,
            vehicle_name=driver.vehicle_name,
            vehicle_plate_number=driver.vehicle_number,
        ),
    )
    await m.reply(file=driver.car_photo)


# todo : new code added
@cb_handler("update_ride")
async def cb_update_ride_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    data = data.split('|')

    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = UserPayload.update_ride_driver
    first_question_key, first_question = list(add_new_temp_driver.items())[0]
    state.value = {
        "step": first_question_key,
        "data": {},
        "vendor_id": int(data[-2]),
        "ride_id": int(data[-1])
    }
    await state.save()
    await event.respond(user.loc.ride_step_full_name)


@cb_handler("ban")
async def cb_ban_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    user_to_ban = await database.User.get(user_id=int(data.split("|")[1]))
    user_to_ban.blocked = not user_to_ban.blocked
    await user_to_ban.save()
    rides_by_user = await database.Ride.filter(user_id=user_to_ban.user_id)
    rides_by_state = {}
    for ride in rides_by_user:
        if ride.status not in rides_by_state:
            rides_by_state[ride.status] = 0
        rides_by_state[ride.status] += 1
    rides_by_state = "\n".join([f"`{k}`: {v}" for k, v in rides_by_state.items()])
    if rides_by_state:
        rides_by_state = "\nRides by state:\n" + rides_by_state
    else:
        rides_by_state = ""
    referrer = await database.ReferralPoint.get_or_none(referred=user_to_ban)
    referrer_text = ""
    if referrer:
        referrer_text = f"\nReferred by: {referrer.referer_id}\n"
    referral_count = await database.ReferralPoint.filter(referer=user_to_ban).count()
    redeemable_amount = await database.ReferralPoint.filter(
        referer=user_to_ban, ride_id__isnull=False, point_used=False
    ).count()
    driver = await database.Driver.get_or_none(user_id=user_to_ban.user_id)
    driver_text = "Driver id: no\n"
    if driver:
        driver_text = f"Driver id: `{driver.id}`"
    await event.edit(
        f"[User](tg://user?id={user_to_ban.user_id}) {user_to_ban.user_id}:\n"
        f"First name: {user_to_ban.first_name}\n"
        f"Last name: {user_to_ban.last_name or '❌'}\n"
        f"Username: {('@' + user_to_ban.username) if user_to_ban.username else '❌'}\n"
        f"Language code: {user_to_ban.lang_code}\n"
        + rides_by_state
        + referrer_text
        + f"\nReferral count: {referral_count}\nRedeemable referral amount: {redeemable_amount}\n"
          f"Banned: {'yes' if user_to_ban.blocked else 'no'}\n" + driver_text,
        buttons=Button.inline(
            "Ban" if not user_to_ban.blocked else "Unban", f"ban|{user_to_ban.user_id}"
        ),
    )


@cb_handler("back_to_categories")
async def cb_back_to_categories_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    all_categories = await database.CabCategory.all()
    buttons = []
    for category in all_categories:
        buttons.append(
            [
                Button.inline(
                    category.name,
                    data=f"lookup_category|{category.id}",
                )
            ]
        )
    buttons.append([Button.inline("Add new category", data="add_category")])
    await event.edit(
        "Click on a category to manage it",
        buttons=buttons,
    )


@cb_handler("lookup_category")
async def cb_lookup_category_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    category_id = int(data.split("|")[1])
    category = await database.CabCategory.get(id=category_id)
    if "toggle" in data:
        category.enabled = not category.enabled
        await category.save()
    await event.edit(
        f"Category id: {category.id}\n"
        f"Name: {category.name}\n"
        f"Cost multiplier: {category.cost_multiplier}\n"
        f"Enabled: {category.enabled}\n",
        buttons=[
            [Button.inline("Edit name", data=f"edit_category_name|{category.id}")],
            [
                Button.inline(
                    "Edit cost multiplier",
                    data=f"edit_category_cost_multiplier|{category.id}",
                )
            ],
            [
                Button.inline(
                    "Toggle enabled", data=f"lookup_category|{category.id}|toggle"
                )
            ],
            [Button.inline("Back", data="back_to_categories")],
        ],
    )


@cb_handler("edit_category_name")
async def cb_edit_category_name_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    category_id = int(data.split("|")[1])
    category = await database.CabCategory.get(id=category_id)
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = UserPayload.edit_category_name
    state.value = {"category_id": category.id}
    await state.save()
    await event.edit("Send me the new name for this category")


@cb_handler("edit_category_cost_multiplier")
async def cb_edit_category_cost_multiplier_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    category_id = int(data.split("|")[1])
    category = await database.CabCategory.get(id=category_id)
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = UserPayload.edit_category_cost_multiplier
    state.value = {"category_id": category.id}
    await state.save()
    await event.edit("Send me the new cost multiplier for this category")


@cb_handler("add_category")
async def cb_add_category_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.payload = UserPayload.add_category_name
    await state.save()
    await event.edit("Send me the name of the new category")


@cb_handler("no_feedback")
async def cb_no_feedback_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    await event.edit(buttons=None)


@cb_handler("feedback")
async def cb_feedback_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    await event.edit(buttons=None)
    ride_id = int(data.split("|")[1])
    await event.reply(
        user.loc.please_select_rating_text,
        buttons=[
            [
                Button.inline("⭐️", data=f"feedback_rating|{ride_id}|1"),
                Button.inline("⭐️⭐️", data=f"feedback_rating|{ride_id}|2"),
            ],
            [
                Button.inline("⭐️⭐️⭐️", data=f"feedback_rating|{ride_id}|3"),
                Button.inline("⭐️⭐️⭐️⭐️", data=f"feedback_rating|{ride_id}|4"),
            ],
            [Button.inline("⭐️⭐️⭐️⭐️⭐️", data=f"feedback_rating|{ride_id}|5")],
        ],
    )


@cb_handler("feedback_rating")
async def cb_feedback_rating_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    ride_id = int(data.split("|")[1])
    rating = int(data.split("|")[2])
    state = await user.get_state(await event.client.get_peer_id("me"))
    state.value["feedback_rating"] = rating
    state.value["feedback_ride_id"] = ride_id
    state.value["feedback_delete_msg"] = event.message_id
    state.payload = UserPayload.feedback_comment
    await state.save()
    await event.edit(
        user.loc.please_send_comment_text,
        buttons=Button.inline(
            user.loc.skip_btntext, data=f"skip_feedback_comment|{ride_id}|{rating}"
        ),
    )


@cb_handler("skip_feedback_comment")
async def cb_skip_feedback_comment_handler(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    ride_id = int(data.split("|")[1])
    ride = await database.Ride.get(id=ride_id)

    rating = int(data.split("|")[2])
    await database.Review.create(
        stars=rating,
        text="",
        from_user=user,
        to_user=await ride.user,
        ride=ride,
        by_driver=True,
    )
    await event.edit(user.loc.thanks_for_feedback_text, buttons=None)


# todo : New code added
@cb_handler("vendor_confirmation")
async def cb_vendor_confirmation(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    asyncio.create_task(
        bot_utils.send_user_to_privacy_share_group(event.client, event.get_sender())
    )
    driver = await user.get_driver()
    await event.edit(user.loc.please_wait_text)
    sender_entity = await event.client.get_entity(event.sender_id)
    full_sender_entity = await event.client(
        functions.users.GetFullUserRequest(sender_entity)
    )
    from_info = bot_utils.get_max_user_info(sender_entity, full_sender_entity)

    client: TelegramClient = event.client
    text_to_owner = f"""
Driver request : Upgrade to vendor
From:
{from_info}
Full name: {driver.full_name}
Vehicle Number: {driver.vehicle_number}
Phone Number: {driver.phone}
Vehicle Name: {driver.vehicle_name}
    """
    await client.send_message(
        shared.config.owner_id,
        text_to_owner,
        buttons=[
            [Button.inline("Approve ✅", data=f"upgrade_to_vendor|{user.user_id}|1")],
            [Button.inline("Reject ❌", data=f"upgrade_to_vendor|{user.user_id}|0")],
        ],
    )


# todo : New code added
@cb_handler("upgrade_to_vendor")
async def cb_accept_or_reject_vendor_upgrade(
        event: events.CallbackQuery.Event, data: str, user: database.User
):
    data = data.split('|')
    user_id = int(data[1])
    driver_user = await database.User.get(user_id=user_id)
    driver = await driver_user.get_driver()
    approved = int(data[2])
    if approved:
        driver.is_vendor = True
        await driver.save()
        await event.edit("Successfully upgraded")
        await event.client.send_message(
            driver_user.user_id,
            "Your have been successfully upgraded to a vendor"
        )
    else:
        await event.edit("Upgrade rejected")
        await event.client.send_message(
            driver_user.user_id,
            "Your upgrade request has been rejected. Please contact the owner for help"
        )


async def cb_main_handler(event: events.CallbackQuery.Event):
    global callback_data_binds
    user, _ = await database.User.get_or_create(user_id=event.sender_id)
    asyncio.create_task(user.mb_update_data(event.get_sender()))
    if user.blocked:
        await event.respond(user.loc.you_are_blocked)
        raise events.StopPropagation
    data = event.data.decode("utf-8")
    data_payload = data.split("|")[0]

    # I want to patch event.edit to auto-do event.send_message on "errors.rpcerrorlist.MessageIdInvalidError", because
    # this error occurs when the message is too old to be edited, and I want to send a new message instead of editing.
    # it is easier to patch the event.edit function than to implement it in the code

    original_edit = event.edit

    async def edit_wrapper(*args, **kwargs):
        try:
            await original_edit(*args, **kwargs)
        except rpcerrorlist.MessageIdInvalidError:
            await event.respond(*args, **kwargs)

    event.edit = edit_wrapper

    if data_payload in callback_data_binds:
        try:
            logger.debug(f"Call query [u {user.user_id}]: {data}")
            await callback_data_binds[data_payload]["f"](event, data, user)
        except events.StopPropagation:
            pass
        except Exception as e:
            logger.exception(e)
            # noinspection PyProtectedMember
            if event._answered:
                await event.reply(user.loc.an_error_occurred)
            else:
                await event.answer(user.loc.an_error_occurred)
    else:
        await event.answer(user.loc.an_error_occurred)
        logger.error(f"Unknown callback query: {data}")


async def init_cb(bot: TelegramClient, parent_logger=None):
    global logger
    if parent_logger:
        logger = parent_logger.getChild("callbacks")
    bot.add_event_handler(cb_main_handler, events.CallbackQuery())
    logger.info("Set up callback handler")
