"""

The locales will be organized with a class for each language.
EN will always be the parent as fallback, in case a translation is missing.
Terminology (var name endings):
    _text - used as text within sending/editing message
    _btn - a single button without being nested within a list. May be used by itself or to generate some menus
    _btntext - a text for button, when callback data is dynamic
    _buttons - a full list of buttons to be used in a message
"""

from .. import constants
from telethon import Button


class En:  # English
    # ====== general ===================================================================================================
    an_error_occurred = "❗ An error occurred"
    unknown_command = "❓ Unknown command"
    unknown_payload = "❓ Unknown payload"
    unknown_callback_data = "❓ Unknown callback data"
    you_are_blocked = "⛔ You are blocked"

    back_btntext = "🔙 Back"
    prev_step_btntext = "⬅️ Previous step"
    cancel_btntext = "❌ Cancel"
    finish_btntext = "✅ Finish"
    please_wait_text = "⌛ Please wait..."
    skip_btntext = "⏭ Skip"

    please_select_language_text = """
🌐 Please select your language:
कृपया अपनी भाषा चुनें:
ದಯವಿಟ್ಟು ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:
"""
    select_language_buttons = [
        Button.inline("🇬🇧 English", data="lang|en"),
        Button.inline("🇮🇳 हिन्दी", data="lang|hi"),
        Button.inline("🇮🇳 ಕನ್ನಡ", data="lang|kn"),
    ]

    # ====== drivers bot ===============================================================================================
    drivers_referrals_info_text = f"""
👥 Referrals
🔗 Your referral link (for riders): {{referral_link}}
👥 Referral count: {{referral_count}}
👥💰 Redeemable amount: {{redeemable_amount}}

You can redeem {constants.Constants.referrals_50_percent_off_driver_sub} referrals for a 50% discount on your subscription.
You can redeem {constants.Constants.referrals_100_percent_off_driver_sub} referrals for a free subscription.
"""
    drivers_your_application_is_pending_text = """
⏳ Your application is pending. Please wait for the admin to review it.
"""
    drivers_you_are_already_a_driver_has_sub_text = """
🚗 You are a driver!
Your subscription is active until {sub_end_date}.
Invite link: {invite_link}
"""
    drivers_you_are_already_a_driver_no_sub_text = """
🚗 You are a driver!
You don't have an active subscription, so you can't participate in rides.
"""
    drivers_please_complete_the_registration_text = """
👋 Welcome! In order to become a driver, you need to complete the registration form.
Press the button below to start.
"""
    drivers_start_registration_button = Button.inline(
        "💬 Start registration", data="start_registration"
    )

    # KYC questions
    kyc_full_name = "👤 Please enter your full name"
    kyc_vehicle_number = "🚗 Please enter your vehicle number"
    kyc_phone_number = "📞 Please enter your phone number"
    kyc_vehicle_name = "🚗 Please enter your vehicle name"
    kyc_aadhar_card_photo = "📷 Please send a photo of your Aadhar card"
    kyc_car_photo = "📷 Please send a photo of your car"

    drivers_answer_incorrect_format_text = (
        "❌ Your answer is in incorrect format. Please try again."
    )
    drivers_image_too_big_text = "❗ The image is too big. Please send a smaller one."

    drivers_please_select_categories_text = """
🚦 Please select the categories you want to drive in:
"""
    drivers_please_wait_downloading_text = "⌛ Please wait, downloading..."
    drivers_thank_you_for_submission_text = """
✅ Thank you for your submission!
Your application will be reviewed by the admin.
"""
    drivers_kyc_application_approved_no_sub_text = """
✅ Your application has been approved!
You can now proceed to the next step.
Click on button below to pay for your subscription.
"""

    drivers_begin_payment_prolong_button = Button.inline(
        "💳 Begin payment", data="begin_payment"
    )
    drivers_begin_payment_button = Button.inline(
        "💳 Begin payment", data="begin_payment"
    )
    drivers_kyc_application_approved_has_sub_text = """
✅ Your application has been approved!
Group link: {group_link}
"""
    drivers_kyc_application_rejected_text = """
❌ Your application has been rejected.
Please contact the admin for more information.
"""
    payment_description = f"""
💳 Payment for 1 month of subscription costs ~~₹1999~~ ₹{constants.Constants.driver_subscription_cost}.
You can pay using any UPI app.
Referrals discount:
{constants.Constants.referrals_50_percent_off_driver_sub} referrals - 50% off
{constants.Constants.referrals_100_percent_off_driver_sub} referrals - 100% off 
"""
    buy_with_upi_button = Button.inline("Buy with UPI", "buy_with_upi")
    buy_with_50_percent_off_button = Button.inline(
        "💰👥 Buy with 50% off", "buy_with_upi|50"
    )
    buy_with_100_percent_off_button = Button.inline(
        "💯 Buy with 100% off", "buy_with_100_percent_off"
    )
    drivers_payment_subscription_text = """
💳 In order to become a driver, you need to pay {AMOUNT} for your subscription.
I've attached QR code for your convenience.
"""
    drivers_payed_btntext = "✅ PAID"

    drivers_please_provide_payment_proof_text = """
📷 Please send a photo of your payment proof. After cross-checking, your application will be approved!
"""
    drivers_please_send_a_valid_image_text = "❌ Please send a valid image."
    drivers_payment_proof_sent_text = (
        "✅ Your payment proof has been sent to the admin. Please wait for approval."
    )
    drivers_payment_proof_verified_text = """
✅ Your payment proof has been verified! Now you have access to the driver's group. Welcome to PLANCAB!
Invite link: {group_link}
"""
    drivers_payment_proof_rejected_text = """
❌ Your payment proof has been rejected.
Please contact the admin for more information.
"""

    drivers_you_were_not_let_in_group_no_sub_text = """
❌ You were not let in the group.
You don't have an active subscription, so you can't participate in rides.
Send /start to proceed with registration.
"""
    drivers_you_were_let_in_group_has_sub_text = """
✅ You were let in the group! Welcome!
"""
    drivers_you_were_kicked_group_no_sub_text = """
❌ You were kicked from the group, because you don't have an active subscription.
Send /start to proceed with registration.
"""
    drivers_subscription_24_hours_left_notification_text = """
⏳ Your subscription will expire in 24 hours.
You can renew it by clicking on the button below.
"""

    drivers_subscription_1_hour_left_notification_text = """
⏳ Your subscription will expire in 1 hour.
You can renew it by clicking on the button below.
"""

    drivers_ride_already_accepted_text = """
❌ Sorry, this ride has already been accepted by another driver.
"""
    update_driver_details = """
Update driver details
"""

    drivers_you_have_successfully_accepted_the_ride_text = """
✅ You have successfully accepted the ride!
User's telegram details:
{user_details}

Drive details:
{drive_details}
"""
    drivers_i_could_not_message_you_text = """
❌ I could not message you.
Please make sure you have started a conversation with the bot.
"""
    drivers_ride_details = """
📜 Ride #{id}
📍 From: `{text_from}` [link]({google_maps_from_url})
🏁 To: `{text_to}` [link]({google_maps_to_url})
🚕 Category: {category}
🛣 Distance: {distance} km
⌛️Duration: {duration}
💲 Cost: {cost}
🕐 Pickup time: {pickup_time}
📲 Phone number: {phone_number}
👤 Full name: {full_name}
"""
    drivers_please_pay_subscription_text = """
💳 Your subscription has expired.
Please pay for your subscription to continue using the bot.
"""
    confirm_vendor_upgrade = "Are you sure you want to upgrade to a vendor?"  # todo : change in other languages
    you_are_already_vendor = "You are already a vendor"  # todo : change in other languages
    drivers_planned_drive_alert_text = """
Dear Driver, your ride assignment is in {time_left}. Here are the details of your ride:

{ride_info}
"""

    # ====== riders bot ================================================================================================
    riders_referrals_info_text = f"""
👥 Referrals
🔗 Your referral link (for riders): {{referral_link}}
👥 Referral count: {{referral_count}}
👥💰 Redeemable amount: {{redeemable_amount}}

You can redeem {constants.Constants.referrals_for_free_ride} referrals for a free ride.
"""
    riders_welcome_text = """
👋 {name} Welcome to PlanCab - Democratizing Scheduled Commute.
Quick - Saves Money - Awesome!

Before proceeding please update your details once by clicking on /info .
"""
    # Let's book your ride now!
    # 🚖 Press the button below to start booking, or type /order.

    help = "Press on /order or /start to leave the booking process in middle and start booking again.\nFor more help " \
           "contact @PlanCab "
    description = ["\nOne Time Booking to any location.\n",
                   "\nTo & Fro booking : Book for Departure and Arrival and get cab assurance & 5% off !\n",
                   "\nAwww...For commutes with your furry friends! Get an All-Inclusive fare with our Pet Friendly "
                   "Drivers !\n",
                   "\nFor your InterCity Requirements.\n",
                   "\nFixed Driver for Fixed Duration : Simple!\nSelect Duration - Select Days - Pickup and Dropoff "
                   "Time - Book.\n ",
                   "\nHire cab on basis of hours selected."]

    rider_enter_droptime_for_commute = "Enter details for **Return Journey**:"
    rider_enter_picktime_for_commute = "Enter details for **First Journey**"
    riders_please_select_booking_type_text = "Choose Booking Type"
    riders_booking_type_btns = [
        [Button.inline("➡️One-Way", data="cabcategory|0"), Button.inline("🔃 Round-Trip", data="cabcategory|1")],
        [Button.inline("🐕‍🦺 Pet Friendly Cab", data='cabcategory|5'),
         Button.inline("🏞  Outstation", data='cabcategory|4')],
        [Button.inline("🏢 Office Commute", data="cabcategory|2"),
         Button.inline("🏙️ Intra-City", data="cabcategory|3")], [Button.inline(cancel_btntext, data="start|clear")]]
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    prev_question_button = [Button.inline(
        prev_step_btntext,
        data=f"order_goto_step|"
    )]
    cancel_btn = [Button.inline(cancel_btntext, data="start|clear")]

    hours_buttons_for_intracity = [
        [Button.inline('3', data='intracity|hours|3'), Button.inline('4', data='intracity|hours|4'),
         Button.inline('5', data='intracity|hours|5'), Button.inline('6', data='intracity|hours|6')],
        [Button.inline('7', data='intracity|hours|7'), Button.inline('8', data='intracity|hours|8'),
         Button.inline('9', data='intracity|hours|9'), Button.inline('10', data='intracity|hours|10')],
        [Button.inline('11', data='intracity|hours|11'), Button.inline('12', data='intracity|hours|12'),
         Button.inline('13', data='intracity|hours|13'), Button.inline('14', data='intracity|hours|14')],
        cancel_btn
        ]
    enter_no_of_hours = "Select number of hours you want to rent the cab for : "
    riders_enter_commute_days = "Enter the duration : "
    riders_start_order_button = Button.inline("🚖 Start Booking", data="start_order")
    ride_step_date = """
📆 Please select or type the date of your ride. 
Format:
dd.mm.yyyy
📅 Current date: `{date_now}`
"""
    ride_step_time = """
⏰ Please select the time of your ride.
Format:
hh:mm
🕑 Current time: `{time_now}`
"""
    ride_step_full_name = "👤 Please enter your full name"
    ride_step_phone_number = "📞 Please enter your phone number"
    ride_step_from = """
🚩 Now TYPE YOUR PICKUP LOCATION, and let our system capture it.

__if this doesn't work click on the paperclip icon (📎) and then on the location icon (📍) in the bottom left corner of the screen__
"""
    ride_step_to = """
🏁 Now TYPE YOUR DROP LOCATION, and let our system capture it.

__if this doesn't work click on the paperclip icon (📎) and then on the location icon (📍) in the bottom left corner of the screen__
"""
    riders_please_select_category_text = """
Viola! Once accepted, Pay directly to the driver!

🚦 Please select the car category you want to ride in:
"""
    riders_answer_incorrect_format_text = """
🤔 Your answer is in incorrect format. Please refer to the instructions and try again.
"""
    riders_please_provide_date_in_future_text = """
🤔 Please provide current date or a date in the future.
"""
    riders_please_provide_time_in_future_text = """
🤔 Please provide current time or a time in the future.
"""
    riders_no_route_found_text = """
❌ No route found. Please click "previous" button and enter a different address.
"""
    place_not_found_please_specify_better_text = """
❌ Place not found. Please make sure you entered the address correctly.
"""
    riders_location_not_found_text = """
❌ Location not found. Please click "previous" button and enter a different address.
"""

    riders_ride_data_preview_text = (
            """
📝 Please check your data:

🚖 Category: {category}

📆 Departure: {datetime}

👤 Name: {full_name}
📞 Phone number: {phone_number}

🛣 Distance: {distance} km
⏳ Duration: {duration}

💵 Price: ₹{price}

💳 Price for reservation: ~~₹99~~ ₹"""
            + str(constants.Constants.ride_order_cost)
    )
    riders_confirm_order_btntext = "✅ Confirm order"
    riders_please_pay_for_reservation_text = f"""
💳 You need to pay ₹{constants.Constants.ride_order_cost} for reservation, this is the platform fee that helps us run this. You can pay the ride fare directly to the driver at the end of the ride. :)
Click on the button below to proceed.

You can redeem {constants.Constants.referrals_for_free_ride} referrals for a free ride.
"""

    riders_you_can_pay_with_referral_add_text = """
👥 You have enough referral points to pay for the reservation ({required}).
Click on the button below to proceed.
"""
    riders_pay_btntext = "💳 Pay"
    riders_pay_with_referral_btntext = "💳 Pay with referral points"
    riders_here_is_payment_qr_text = """
💳 Here is the QR code for your payment.
Click "Paid" button after you pay.
"""
    riders_payed_btntext = "✅ PAID"
    riders_please_send_screen_of_payment_text = """
📷 Please send a screenshot of your payment.
"""
    riders_please_send_a_valid_image_text = "❌ Please send a valid image."
    riders_thanks_for_payment_text = """
✅ Thank you for your payment!
After confirmation, order will be sent to the drivers.
"""
    riders_payment_rejected_text = """
❌ Your payment has been rejected.
Please contact the admin for more information.
"""
    riders_payment_accepted_text = """
✅ Your payment has been accepted! Order id: #{drive_id}
Order has been sent to the drivers.
You will be notified when a driver accepts your order.
"""
    riders_user_drive_details_text = """
🚖 Your order #{id} has been accepted by a driver!
Driver's telegram details:
{driver_details}

📲 Phone number: {driver_phone_number}
👤 Full name: {driver_full_name}
🚖 Vehicle name: {vehicle_name}
🔢 Vehicle reg. plate number: {vehicle_plate_number}
Have a nice trip!
"""
    riders_ride_details_text = """
🚖 Ride #{id} details:

⚫ Category: {category}
📍 [from]({google_maps_from_url})
🏁 [to]({google_maps_to_url})
📆 Departure: {departure}
👤 Driver's Name: {driver_full_name}
📞 Driver's Phone number: {driver_phone_number}
🚖 Vehicle name: {driver_vehicle_name}
🔢 Vehicle number: {driver_vehicle_number}
🛣 Distance: {distance} km
⏳ Duration: {duration}
💵 Price: ₹{cost}
"""
    please_validate_departure_place_text = f"""
🤔 Check your Pickup location.

Pickup: {{departure}}


If it's wrong, press '{prev_step_btntext}' button and enter a different address.
"""
    please_validate_destination_place_text = f"""
🤔 Check your destination place.

Destination: {{destination}}


To change it, press '{prev_step_btntext}' button and enter a different address.
Proceed to the next step if it is right.
"""
    drive_should_have_started_mb_alert_text = """
🚖 Drive #{id} should have started!
If you find yourself in danger, please call the police and press button below to send alert to the admins. 
"""
    drive_should_have_started_mb_alert_btn_text = "🆘 Send alert"
    drive_should_have_started_mb_alert_sent_text = "✅ Alert sent!"

    did_you_have_a_ride = """
🚖 Hi! Did you complete the ride with PlanCab #{id}?

Ride details:
📍 [from]({google_maps_from_url})
🏁 [to]({google_maps_to_url})
📆 Departure: {departure}
👤 Driver's Name: {driver_full_name}
👤 Rider's Name: {rider_full_name}
"""
    yes_btntext = "✅ Yes"
    no_btntext = "❌ No"
    please_select_rating_text = """
🤔 Please select a rating.
"""
    please_send_comment_text = f"""
🤔 Please send a comment.
You can also press '{skip_btntext}' button.
"""
    thanks_for_feedback_text = """
✅ Thank you for your feedback!
"""
    riders_planned_drive_alert_text = """
Dear Rider, your ride is in {time_left}. Here are the details of your ride:

{ride_info}
"""


class Hi:
    # ====== general ===================================================================================================
    an_error_occurred = "❗ एक त्रुटि हुई"
    unknown_command = "❓ अज्ञात आदेश"
    unknown_payload = "❓ अज्ञात पेलोड"
    unknown_callback_data = "❓ अज्ञात कॉलबैक डाटा"
    you_are_blocked = "⛔ आप ब्लॉक हैं"

    back_btntext = "🔙 पीछे"
    prev_step_btntext = "⬅️ पिछला कदम"
    cancel_btntext = "❌ रद्द करें"
    finish_btntext = "✅ समाप्त"
    please_wait_text = "⌛ कृपया प्रतीक्षा करें..."
    skip_btntext = "⏭ छोड़ें"
    please_select_language_text = """
🌐 Please select your language:
कृपया अपनी भाषा चुनें:
ದಯವಿಟ್ಟು ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:
"""
    select_language_buttons = [
        Button.inline("🇬🇧 English", data="lang|en"),
        Button.inline("🇮🇳 हिन्दी", data="lang|hi"),
        Button.inline("🇮🇳 ಕನ್ನಡ", data="lang|kn"),

    ]

    # ====== drivers bot ===============================================================================================
    drivers_referrals_info_text = f"""
👥 संदर्भ
🔗 आपका संदर्भ लिंक (सवारों के लिए): {{referral_link}}
👥 संदर्भ गिनती: {{referral_count}}
👥💰 परिवर्तनीय राशि: {{redeemable_amount}}

आप {constants.Constants.referrals_50_percent_off_driver_sub} संदर्भ अपने सदस्यता पर 50% छूट के लिए परिवर्तित कर सकते हैं।
आप {constants.Constants.referrals_100_percent_off_driver_sub} संदर्भ एक मुफ्त सदस्यता के लिए परिवर्तित कर सकते हैं।
"""
    drivers_your_application_is_pending_text = """
⏳ आपका आवेदन लंबित है। कृपया प्रशासनिक समीक्षा की प्रतीक्षा करें।
"""
    drivers_you_are_already_a_driver_has_sub_text = """
🚗 आप एक ड्राइवर हैं!
आपकी सदस्यता {sub_end_date} तक सक्रिय है।
आमंत्रण लिंक: {invite_link}
"""
    drivers_you_are_already_a_driver_no_sub_text = """
🚗 आप एक ड्राइवर हैं!
आपकी कोई सक्रिय सदस्यता नहीं है, इसलिए आप सवारियों में भाग नहीं ले सकते।
"""
    drivers_please_complete_the_registration_text = """
👋 स्वागत है! ड्राइवर बनने के लिए, आपको पंजीकरण फॉर्म पूरा करना होगा।
नीचे दिए गए बटन पर क्लिक करके शुरू करें।
"""
    drivers_start_registration_button = Button.inline(
        "💬 पंजीकरण शुरू करें", data="start_registration"
    )

    # KYC questions
    kyc_full_name = "👤 कृपया अपना पूरा नाम दर्ज करें"
    kyc_vehicle_number = "🚗 कृपया अपना वाहन नंबर दर्ज करें"
    kyc_phone_number = "📞 कृपया अपना फ़ोन नंबर दर्ज करें"
    kyc_vehicle_name = "🚗 कृपया अपना वाहन का नाम दर्ज करें"
    kyc_aadhar_card_photo = "📷 कृपया अपने आधार कार्ड की फ़ोटो भेजें"
    kyc_car_photo = "📷 कृपया अपने वाहन की फ़ोटो भेजें"

    drivers_answer_incorrect_format_text = (
        "❌ आपका उत्तर गलत प्रारूप में है। कृपया पुनः प्रयास करें।"
    )
    drivers_image_too_big_text = "❗ छवि बहुत बड़ी है। कृपया एक छोटी छवि भेजें।"

    drivers_please_select_categories_text = """
🚦 कृपया वे श्रेणियां चुनें जिनमें आप ड्राइव करना चाहते हैं:
"""
    drivers_please_wait_downloading_text = (
        "⌛ कृपया प्रतीक्षा करें, डाउनलोड हो रहा है..."
    )
    drivers_thank_you_for_submission_text = """
✅ आपके सबमिशन के लिए धन्यवाद!
आपका आवेदन प्रशासक द्वारा समीक्षित किया जाएगा।
"""
    drivers_kyc_application_approved_no_sub_text = """
✅ आपका आवेदन मंजूर कर दिया गया है!
अगला कदम आगे बढ़ने के लिए जाएं।
अपनी सदस्यता के लिए भुगतान करने के लिए नीचे दिए गए बटन पर क्लिक करें।
"""
    drivers_begin_payment_prolong_button = Button.inline(
        "💳 भुगतान शुरू करें", data="begin_payment"
    )
    drivers_begin_payment_button = Button.inline(
        "💳 भुगतान शुरू करें", data="begin_payment"
    )
    drivers_kyc_application_approved_has_sub_text = """
✅ आपका आवेदन मंजूर कर दिया गया है!
समूह लिंक: {group_link}
"""
    drivers_kyc_application_rejected_text = """
❌ आपका आवेदन अस्वीकृत कर दिया गया है।
अधिक जानकारी के लिए कृपया प्रशासक से संपर्क करें।
"""
    payment_description = f"""
💳 1 महीने की सदस्यता के लिए भुगतान की लागत ~~₹1999~~ ₹{constants.Constants.driver_subscription_cost} है।
आप किसी भी UPI ऐप का उपयोग करके भुगतान कर सकते हैं।
संदर्भ छूट:
{constants.Constants.referrals_50_percent_off_driver_sub} संदर्भ - 50% छूट
{constants.Constants.referrals_100_percent_off_driver_sub} संदर्भ - 100% छूट
"""
    buy_with_upi_button = Button.inline("UPI के साथ खरीदें", "buy_with_upi")
    buy_with_50_percent_off_button = Button.inline(
        "💰👥 50% छूट के साथ खरीदें", "buy_with_upi|50"
    )
    buy_with_100_percent_off_button = Button.inline(
        "💯 100% छूट के साथ खरीदें", "buy_with_100_percent_off"
    )
    drivers_payment_subscription_text = """
💳 ड्राइवर बनने के लिए, आपको अपनी सदस्यता के लिए {AMOUNT} भुगतान करना होगा।
आपकी सुविधा के लिए मैंने QR कोड संलग्न किया है।
"""
    drivers_payed_btntext = "✅ भुगतान किया"

    drivers_please_provide_payment_proof_text = """
📷 कृपया अपने भुगतान के प्रमाण की फ़ोटो भेजें। सत्यापन के बाद, आपका आवेदन मंजूर होगा!
"""
    drivers_please_send_a_valid_image_text = "❌ Please send a valid image."
    drivers_payment_proof_sent_text = "✅ आपका भुगतान प्रमाण प्रशासन को भेज दिया गया है। कृपया मंजूरी के लिए प्रतीक्षा करें।"
    drivers_payment_proof_verified_text = """
✅ आपका भुगतान प्रमाण सत्यापित किया गया है! अब आपके पास ड्राइवर्स समूह तक पहुंच है।
आमंत्रण लिंक: {group_link}
"""
    drivers_payment_proof_rejected_text = """
❌ आपका भुगतान प्रमाण अस्वीकृत कर दिया गया है।
अधिक जानकारी के लिए कृपया प्रशासन से संपर्क करें।
"""

    drivers_you_were_not_let_in_group_no_sub_text = """
❌ आपको समूह में शामिल नहीं किया गया है।
आपका सक्रिय सदस्यता नहीं है, इसलिए आप यात्राओं में भाग नहीं ले सकते हैं।
पंजीकरण जारी रखने के लिए /start भेजें।
"""
    drivers_you_were_let_in_group_has_sub_text = """
✅ आपको समूह में शामिल किया गया है! स्वागत करते हैं!
"""
    drivers_you_were_kicked_group_no_sub_text = """
❌ आपको समूह से निकाल दिया गया है, क्योंकि आपकी सक्रिय सदस्यता नहीं है।
पंजीकरण जारी रखने के लिए /start भेजें।
"""
    drivers_subscription_24_hours_left_notification_text = """
⏳ आपकी सदस्यता 24 घंटे में समाप्त हो जाएगी।
आप इसे नवीकृत कर सकते हैं नीचे दिए गए बटन पर क्लिक करके।
"""

    drivers_subscription_1_hour_left_notification_text = """
⏳ आपकी सदस्यता 1 घंटे में समाप्त हो जाएगी।
आप इसे नवीकृत कर सकते हैं नीचे दिए गए बटन पर क्लिक करके।
"""

    drivers_ride_already_accepted_text = """
❌ क्षमा करें, यह सवारी पहले से ही किसी अन्य ड्राइवर द्वारा स्वीकृत की गई है।
"""
    update_driver_details = """
Update driver details
    """
    drivers_you_have_successfully_accepted_the_ride_text = """
✅ आपने सवारी को सफलतापूर्वक स्वीकार कर लिया है!
उपयोगकर्ता का टेलीग्राम विवरण:
{user_details}

चालना विवरण:
{drive_details}
"""
    drivers_i_could_not_message_you_text = """
❌ मैं आपको संदेश नहीं भेज सका।
कृपया सुनिश्चित करें कि आपने बॉट के साथ एक चर्चा शुरू की है।
"""
    drivers_ride_details = """
📜 सवारी #{id}
📍 से: `{text_from}` [लिंक]({google_maps_from_url})
🏁 तक: `{text_to}` [लिंक]({google_maps_to_url})
🚕 श्रेणी: {category}
🛣 दूरी: {distance} किलोमीटर
⌛️ अवधि: {duration}
💲 लागत: {cost}
🕐 पिकअप समय: {pickup_time}
📲 फ़ोन नंबर: {phone_number}
👤 पूरा नाम: {full_name}
"""
    drivers_please_pay_subscription_text = """
💳 आपकी सदस्यता समाप्त हो गई है।
बॉट का उपयोग जारी रखने के लिए कृपया अपनी सदस्यता का भुगतान करें।
"""
    confirm_vendor_upgrade = "Are you sure you want to upgrade to a vendor?"  # todo : change in other languages
    you_are_already_vendor = "You are already a vendor"  # todo : change in other languages
    drivers_planned_drive_alert_text = """
प्रिय ड्राइवर, आपका सफ़र आवंटन {time_left} में है। यहां आपके सफ़र का विवरण है:

{ride_info}
"""

    # ====== riders bot ================================================================================================
    riders_referrals_info_text = f"""
👥 संदर्भ
🔗 आपका संदर्भ लिंक (राइडर्स के लिए): {{referral_link}}
👥 संदर्भ गणना: {{referral_count}}
👥💰 रिडीमेबल राशि: {{redeemable_amount}}

आप {constants.Constants.referrals_for_free_ride} संदर्भों को एक मुफ्त सवारी के लिए रिडीम कर सकते हैं।
"""
    riders_welcome_text = """
👋 {name} स्वागत करते हैं! यह बॉट आपकी सवारी खोजने में मदद करेगा।

Before proceeding please update your details once by clicking on /info.

"""
    description = ["\nOne Time Booking to any location.\n",
                   "\nTo & Fro booking : Book for Departure and Arrival and get cab assurance & 5% off !\n",
                   "\nAwww...For commutes with your furry friends! Get an All-Inclusive fare with our Pet Friendly "
                   "Drivers !\n",
                   "\nFor your InterCity Requirements.\n",
                   "\nFixed Driver for Fixed Duration : Simple!\nSelect Duration - Select Days - Pickup and Dropoff "
                   "Time - Book.\n ",
                   "\nHire cab on basis of hours selected."]

    help = "Press on /order or /start to leave the booking process in middle and start booking again.\nFor more help contact @username"
    rider_enter_droptime_for_commute = "ड्रॉप समय दर्ज करें:"
    rider_enter_picktime_for_commute = "विवरण दर्ज करें **पहली यात्रा**"

    riders_please_select_booking_type_text = "बुकिंग प्रकार चुनें:"
    riders_booking_type_btns = [
        [Button.inline("➡️एक तरफा", data="cabcategory|0"),
         Button.inline("🔃 राउंड-ट्रिप", data="cabcategory|1")],
        [Button.inline("🏢 कार्यालय", data="cabcategory|2"),
         Button.inline("🏞  आउटस्टेशन ", "outstation")],
        [Button.inline("🐕‍🦺 Pet Friendly Cab")],
        [Button.inline(cancel_btntext, data="start|clear")]
    ]
    days = ['सोम', 'मंगल', 'बुध', 'गुरु', 'शुक्र', 'शनि', 'रवि']
    riders_enter_commute_days = "आप कितने दिनों के लिए चाहते हैं: "
    prev_question_button = [Button.inline(
        prev_step_btntext,
        data=f"order_goto_step|"
    )]
    cancel_btn = [Button.inline(cancel_btntext, data="start|clear")]

    hours_buttons_for_intracity = hours_buttons_for_intracity = [
        [Button.inline('3', data='intracity|hours|3'), Button.inline('4', data='intracity|hours|4'),
         Button.inline('5', data='intracity|hours|5'), Button.inline('6', data='intracity|hours|6')],
        [Button.inline('7', data='intracity|hours|7'), Button.inline('8', data='intracity|hours|8'),
         Button.inline('9', data='intracity|hours|9'), Button.inline('10', data='intracity|hours|10')],
        [Button.inline('11', data='intracity|hours|11'), Button.inline('12', data='intracity|hours|12'),
         Button.inline('13', data='intracity|hours|13'), Button.inline('14', data='intracity|hours|14')],
        cancel_btn
        ]
    enter_no_of_hours = "Select number of hours you want to rent the cab for : "
    riders_start_order_button = Button.inline("🚖 सवारी आरंभ करें", data="start_order")
    ride_step_date = """
📆 कृपया अपनी सवारी की तारीख का चयन करें या टाइप करें। 
फॉर्मेट:
दिन.माह.वर्ष
📅 वर्तमान तारीख: `{date_now}`
"""
    ride_step_time = """
⏰ कृपया अपनी सवारी का समय चुनें।
फॉर्मेट:
घंटे:मिनट
🕑 वर्तमान समय: `{time_now}`
"""
    ride_step_full_name = "👤 कृपया अपना पूरा नाम दर्ज करें"
    ride_step_phone_number = "📞 कृपया अपना फोन नंबर दर्ज करें"
    ride_step_from = """
🚩 कृपया अपनी शुरुआती बिंदु की भू-स्थानांकित करें (या इसे मैन्युअल रूप से टाइप करें)
__स्क्रीन के नीचे बाएं कोने में कागज की क्लिप आइकन (📎) पर क्लिक करें और फिर स्थानांकित का आइकन (📍) पर क्लिक करें__
"""
    ride_step_to = """
🏁 कृपया अपने गंतव्य स्थान की भू-स्थानांकित करें (या इसे मैन्युअल रूप से टाइप करें)
__स्क्रीन के नीचे बाएं कोने में कागज की क्लिप आइकन (📎) पर क्लिक करें और फिर स्थानांकित का आइकन (📍) पर क्लिक करें__
"""
    riders_please_select_category_text = """
🚦 कृपया उस श्रेणी का चयन करें जिसमें आप सवारी करना चाहते हैं:
"""
    riders_answer_incorrect_format_text = """
🤔 आपका जवाब गलत प्रारूप में है। कृपया निर्देशों का पालन करें और पुनः प्रयास करें।
"""
    riders_please_provide_date_in_future_text = """
🤔 कृपया वर्तमान तारीख या भविष्य की तारीख प्रदान करें।
"""
    riders_please_provide_time_in_future_text = """
🤔 कृपया वर्तमान समय या भविष्य का समय प्रदान करें।
"""
    riders_no_route_found_text = """
❌ कोई मार्ग नहीं मिला। कृपया "पिछला" बटन दबाएं और एक अलग पता दर्ज करें।
"""
    place_not_found_please_specify_better_text = """
❌ स्थान नहीं मिला। कृपया सुनिश्चित करें कि आपने सही पता दर्ज किया है।
"""
    riders_location_not_found_text = """
❌ स्थान नहीं मिला। कृपया "पिछला" बटन दबाएं और एक अलग पता दर्ज करें।
"""

    riders_ride_data_preview_text = (
            """
📝 कृपया अपना डेटा जांचें:

🚖 श्रेणी: {category}

📆 रवाना होने की तारीख: {datetime}
👤 नाम: {full_name}
📞 फोन नंबर: {phone_number}

🛣 दूरी: {distance} किलोमीटर
⏳ अवधि: {duration}

💵 मूल्य: ₹{price}

💳 आरक्षण के लिए मूल्य: ~~₹99~~ ₹"""
            + str(constants.Constants.ride_order_cost)
    )
    riders_confirm_order_btntext = "✅ ऑर्डर की पुष्टि करें"
    riders_please_pay_for_reservation_text = f"""
💳 आपको आरक्षण के लिए ₹`{constants.Constants.ride_order_cost}` भुगतान करना होगा।
आगे बढ़ने के लिए नीचे दिए गए बटन पर क्लिक करें।

आप {constants.Constants.referrals_for_free_ride} संदर्भों को एक मुफ्त सवारी के लिए रिडीम कर सकते हैं।
"""
    riders_you_can_pay_with_referral_add_text = """
👥 आपके पास प्रत्यायन करने के लिए पर्याप्त संदर्भ अंक हैं ({required})।
आगे बढ़ने के लिए नीचे दिए गए बटन पर क्लिक करें।
"""
    riders_pay_btntext = "💳 भुगतान करें"
    riders_pay_with_referral_btntext = "💳 संदर्भ अंकों के साथ भुगतान करें"
    riders_here_is_payment_qr_text = """
💳 यहाँ आपके भुगतान के लिए QR कोड है।
भुगतान करने के बाद "भुगतान किया गया" बटन पर क्लिक करें।
"""
    riders_payed_btntext = "✅ भुगतान हुआ"
    riders_please_send_screen_of_payment_text = """
📷 कृपया अपने भुगतान की स्क्रीनशॉट भेजें।
"""
    riders_please_send_a_valid_image_text = "❌ कृपया एक मान्य छवि भेजें।"
    riders_thanks_for_payment_text = """
✅ भुगतान करने के लिए धन्यवाद!
पुष्टि के बाद, आर्डर ड्राइवर्स को भेजा जाएगा।
"""
    riders_payment_rejected_text = """
❌ आपका भुगतान अस्वीकृत कर दिया गया है।
अधिक जानकारी के लिए कृपया प्रशासन से संपर्क करें।
"""
    riders_payment_accepted_text = """
✅ आपका भुगतान स्वीकार किया गया है! आर्डर आईडी: #{drive_id}
आर्डर ड्राइवर्स को भेजा गया है।
जब कोई ड्राइवर आपका ऑर्डर स्वीकार करेगा तो आपको सूचित किया जाएगा"""
    riders_user_drive_details_text = """
🚖 ड्राइवर द्वारा आपके आर्डर #{id} को स्वीकार किया गया है!
ड्राइवर का टेलीग्राम विवरण:
{driver_details}

📲 फोन नंबर: {driver_phone_number}
👤 पूरा नाम: {driver_full_name}
🚖 वाहन का नाम: {vehicle_name}
🔢 वाहन पंजीकरण संख्या: {vehicle_plate_number}
अच्छी यात्रा करें!
"""
    riders_ride_details_text = """
    🚖 राइड #{id} विवरण:

⚫ श्रेणी: {category}
📍 [से]({google_maps_from_url})
🏁 [तक]({google_maps_to_url})
📆 प्रस्थान: {departure}
👤 ड्राइवर का नाम: {driver_full_name}
📞 ड्राइवर का फोन नंबर: {driver_phone_number}
🚖 वाहन का नाम: {driver_vehicle_name}
🔢 वाहन नंबर: {driver_vehicle_number}
🛣 दूरी: {distance} किलोमीटर
⏳ अवधि: {duration}
💵 कीमत: ₹{cost}
"""
    please_validate_departure_place_text = f"""
🤔 कृपया अपनी प्रस्थान स्थान की पुष्टि करें।
आपने चुना है: {{departure}}
यदि यह गलत है, तो '{prev_step_btntext}' बटन दबाएं और एक अलग पता दर्ज करें।
"""
    please_validate_destination_place_text = f"""
🤔 कृपया अपने गंतव्य स्थान की पुष्टि करें।
आपने चुना है: {{destination}}
यदि यह गलत है, तो '{prev_step_btntext}' बटन दबाएं और एक अलग पता दर्ज करें।
"""
    drive_should_have_started_mb_alert_text = """
🚖 ड्राइव शुरू हो जानी चाहिए थी! (#{id})
यदि आप खुद को खतरे में पाते हैं, कृपया पुलिस को कॉल करें और निम्नलिखित बटन दबाकर प्रशासकों को चेतावनी भेजें।
"""
    drive_should_have_started_mb_alert_btn_text = "🆘 चेतावनी भेजें"
    drive_should_have_started_mb_alert_sent_text = "✅ चेतावनी भेजी गई!"

    did_you_have_a_ride = """
🚖 नमस्ते! क्या आपने सवारी सवारी #{id} की थी?

सवारी विवरण:
📍 [से]({google_maps_from_url})
🏁 [तक]({google_maps_to_url})
📆 प्रस्थान: {departure}
👤 ड्राइवर का नाम: {driver_full_name}
👤 राइडर का नाम: {rider_full_name}
"""
    yes_btntext = "✅ हाँ"
    no_btntext = "❌ नहीं"
    please_select_rating_text = """
🤔 कृपया एक रेटिंग चुनें।
"""
    please_send_comment_text = f"""
🤔 कृपया एक टिप्पणी भेजें।
आप '{skip_btntext}' बटन भी दबा सकते हैं।
"""
    thanks_for_feedback_text = """
✅ आपकी प्रतिक्रिया के लिए धन्यवाद!
"""
    riders_planned_drive_alert_text = """
"प्रिय राइडर, आपका सफ़र आवंटन {time_left} में है। यहां आपके सफ़र का विवरण है:

{ride_info}
"""


class Kn:  # Kannada
    # ====== ಸಾಮಾನ್ಯ ===================================================================================================
    an_error_occurred = "❗ ತಪ್ಪು ನಡೆದುದು"
    unknown_command = "❓ ಗೊತ್ತಿಲ್ಲದ ಆದೇಶ"
    unknown_payload = "❓ ಗೊತ್ತಿಲ್ಲದ ಪೇಯ್ಲೋಡ್"
    unknown_callback_data = "❓ ಗೊತ್ತಿಲ್ಲದ ಕಾಲ್‌ಬ್ಯಾಕ್ ಡೇಟಾ"
    you_are_blocked = "⛔ ನೀವು ಮದ್ದುಗೆಡೆಯಾಗಿದ್ದೀರಿ"

    back_btntext = "🔙 ಹಿಂದಿನದಕ್ಕೆ"
    prev_step_btntext = "⬅️ ಮುನ್ನಡೆಯ ಹಂತ"
    cancel_btntext = "❌ ರದ್ದುಗೊಳಿಸು"
    finish_btntext = "✅ ಮುಗಿಸು"
    please_wait_text = "⌛ ದಯವಿಟ್ಟು ನಿರೀಕ್ಷಿಸಿ..."
    skip_btntext = "⏭ ಸ್ಕಿಪ್ ಮಾಡಿ"

    please_select_language_text = """
🌐 Please select your language:
कृपया अपनी भाषा चुनें:
ದಯವಿಟ್ಟು ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:
"""
    select_language_buttons = [
        Button.inline("🇬🇧 English", data="lang|en"),
        Button.inline("🇮🇳 हिन्दी", data="lang|hi"),
        Button.inline("🇮🇳 ಕನ್ನಡ", data="lang|kn"),
    ]

    # ====== ಡ್ರೈವರ್ಸ್ ಬಾಟ್ ===============================================================================================================
    drivers_referrals_info_text = f"""
👥 ಪರಿಚಯಿಕೆಗಳು
🔗 ನಿಮ್ಮ ಪರಿಚಯಪತ್ರ ಲಿಂಕ (ರೈಡರ್‌ಗಳಿಗೆ): {{referral_link}}
👥 ಪರಿಚಯಪತ್ರ ಸಂಖ್ಯೆ: {{referral_count}}
👥💰 ವಿಮೆಯಬಹುದಾದ ಮೊತ್ತ: {{redeemable_amount}}

ನೀವು ನಿಯಮಿತಪಡಿಸುವುದಕ್ಕೆ {constants.Constants.referrals_50_percent_off_driver_sub} ಪರಿಚಯಪತ್ರಗಳನ್ನು ಪಡೆದು ಮೊದಲು 50% ಡಿಸ್ಕೌಂಟ್ ಪಡೆಯಲು ಬಹುದಾಗಿದೆ.
ನೀವು {constants.Constants.referrals_100_percent_off_driver_sub} ಪರಿಚಯಪತ್ರಗಳನ್ನು ಪಡೆದು ಉಚಿತ ವಾಣಿಜ್ಯವನ್ನು ಪಡೆಯಬಹುದಾಗಿದೆ.
"""
    drivers_your_application_is_pending_text = """
⏳ ನಿಮ್ಮ ಅರ್ಜನೆ ಮುಂದುವರಿಯುತ್ತಿದೆ. ಅದನ್ನು ಪರಿಶೀಲಿಸಲು ನಿರೀಕ್ಷಿಸಿ.
"""
    drivers_you_are_already_a_driver_has_sub_text = """
🚗 ನೀವು ಡ್ರೈವರ್ ಆಗಿದ್ದೀರಿ!
ನಿಮ್ಮ ಚಂದಾ ವಾಯಿತು {sub_end_date} ರವರೆಗೆ.
ಆಹ್ವಾನ ಲಿಂಕ: {invite_link}
"""
    drivers_you_are_already_a_driver_no_sub_text = """
🚗 ನೀವು ಡ್ರೈವರ್ ಆಗಿದ್ದೀರಿ!
ನಿಮಗೆ ಚಾಲನೆಗೆ ಪ್ರವೇಶ ಮಾಡಲು ಯಾವ ಚಾಲನೆ ನಿಲ್ಲು ಇಲ್ಲ.
"""
    drivers_please_complete_the_registration_text = """
👋 ಸ್ವಾಗತ! ಡ್ರೈವರ್ ಆಗಲು, ನೀವು ನೋಂದಣಿ ಪೂರ್ಣಗೊಳಿಸಬೇಕು.
ಪ್ರಾರಂಭಿಸಲು ಕೆಳಗಿನ ಬಟನ್‌ನೊಂದಿಗೆ ಒತ್ತಿರಿ.
"""
    drivers_start_registration_button = Button.inline(
        "💬 ನೋಂದಣಿ ಪ್ರಾರಂಭಿಸಿ", data="start_registration"
    )

    # KYC ಪ್ರಶ್ನೆಗಳು
    kyc_full_name = "👤 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರನ್ನು ನಮೂದಿಸಿ"
    kyc_vehicle_number = "🚗 ದಯವಿಟ್ಟು ನಿಮ್ಮ ವಾಹನದ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ"
    kyc_phone_number = "📞 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಫೋನ್ ನಂಬರನ್ನು ನಮೂದಿಸಿ"
    kyc_vehicle_name = "🚗 ದಯವಿಟ್ಟು ನಿಮ್ಮ ವಾಹನದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ"
    kyc_aadhar_card_photo = "📷 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಆಧಾರ್ ಕಾರ್ಡ್‌ನ ಫೋಟೊವನ್ನು ಕಳುಹಿಸಿ"
    kyc_car_photo = "📷 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಕಾರ್ ಫೋಟೊವನ್ನು ಕಳುಹಿಸಿ"

    drivers_answer_incorrect_format_text = (
        "❌ ನಿಮ್ಮ ಉತ್ತರವು ತಪ್ಪಾಗಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ."
    )
    drivers_image_too_big_text = (
        "❗ ಚಿತ್ರ ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ. ಕಿರುಗಿಸಿ ಒಂದು ಚಿಕ್ಕ ಚಿತ್ರ ಕಳುಹಿಸಿ."
    )

    drivers_please_select_categories_text = """
🚦 ನೀವು ಡ್ರೈವ್ ಮಾಡಲು ಬಯಸುವ ವರ್ಗಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ:
"""
    drivers_please_wait_downloading_text = (
        "⌛ ದಯವಿಟ್ಟು ನಿರೀಕ್ಷಿಸಿ, ಡೌನ್‌ಲೋಡ್ ಆಗುತ್ತಿದೆ..."
    )
    drivers_thank_you_for_submission_text = """
✅ ನಿಮ್ಮ ಸಲ್ಲಿಸುವುದಕ್ಕೆ ಧನ್ಯವಾದಗಳು!
ನಿರೀಕ್ಷಿಸುವ ನಿರ್ವಹಣೆಗೆ ಅದ್ಮಿನ್ ಪರಿಶೀಲಿಸುವರು.
"""

    drivers_kyc_application_approved_no_sub_text = """
✅ ನಿಮ್ಮ ಅರ್ಜಿ ಅನುಮೋದಿತವಾಗಿದೆ!
ನೀವು ಈಗ ಮುಂದಿನ ಹೆಜ್ಜೆಗೆ ಮುಂದುವರಿಯಬಹುದು.
ನಿಮ್ಮ ಚಂದಾದಾರಿಕೆಗೆ ಪಾವತಿಯನ್ನು ಪಾಲಿಸಲು ಕೆಳಗಿನ ಬಟನ್ ಕ್ಲಿಕ್ ಮಾಡಿ.
"""
    drivers_begin_payment_prolong_button = Button.inline(
        "💳 ಪಾವತಿ", data="begin_payment"
    )
    drivers_begin_payment_button = Button.inline("💳 ಪಾವತಿ", data="begin_payment")
    drivers_kyc_application_approved_has_sub_text = """
✅ ನಿಮ್ಮ ಅರ್ಜಿ ಅನುಮೋದಿತವಾಗಿದೆ!
ಗುಂಪು ಲಿಂಕ್: {group_link}
"""

    drivers_kyc_application_rejected_text = """
❌ ನಿಮ್ಮ ಅರ್ಜಿ ನಿರಾಕರಿಸಲಾಗಿದೆ.
ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ದೂರಸಂಚಾರ ಮೂಲಕ ನಿರ್ವಹಿಸಿ.
"""

    payment_description = f"""
💳 1 ತಿಂಗಳ ಚುಕ್ತಿಗೆ ~~₹1999~~ ₹{constants.Constants.driver_subscription_cost} ವೆಚ್ಚದ ಪಾವತಿ.
ನೀವು ಯಾವುದೇ UPI ಆ್ಯಪ್‌ನ್ನು ಬಳಸಿ ಪಾವತಿ ಮಾಡಬಹುದು.
ರೆಫರಲ್ ಡಿಸ್ಕೌಂಟ್:
{constants.Constants.referrals_50_percent_off_driver_sub} ರೆಫರಲ್‌ಗಳು - 50% ಡಿಸ್ಕೌಂಟ್
{constants.Constants.referrals_100_percent_off_driver_sub} ರೆಫರಲ್‌ಗಳು - 100% ಡಿಸ್ಕೌಂಟ್ 
"""
    buy_with_upi_button = Button.inline("UPI ನೊಂದಿಗೆ ಖರೀದಿಸಿ", "buy_with_upi")
    buy_with_50_percent_off_button = Button.inline(
        "💰👥 50% ಡಿಸ್ಕೌಂಟ್ ನೊಂದಿಗೆ ಖರೀದಿಸಿ", "buy_with_upi|50"
    )
    buy_with_100_percent_off_button = Button.inline(
        "💯 100% ಡಿಸ್ಕೌಂಟ್ ನೊಂದಿಗೆ ಖರೀದಿಸಿ", "buy_with_100_percent_off"
    )
    drivers_payment_subscription_text = """
💳 ಒಬ್ಬ ಡ್ರೈವರ್ ಆಗಲು, ನೀವು ನಿಮ್ಮ ಚುಕ್ತಿಗೆ {AMOUNT} ಪಾವತಿ ಪಾಲಿಕೆ ಮಾಡಬೇಕು.
ನಿಮಗೆ ಸೌಲಭ್ಯಕ್ಕಾಗಿ ನನ್ನಲ್ಲಿರುವ QR ಕೋಡ್‌ನೊಂದಿಗೆ ಅನ್ನುವುದು.
"""
    drivers_payed_btntext = "✅ ಪಾವತಿ ಮಾಡಲಾಗಿದೆ"

    drivers_please_provide_payment_proof_text = """
📷 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪಾವತಿ ಪ್ರೂಫ್ ಫೋಟೊ ಕಳುಹಿಸಿ. ಪರಿಶೀಲಿಸಿದ ನಂತರ, ನಿಮ್ಮ ಅರ್ಜಿಯನ್ನು ಅನುಮೋದಿಸಲಾಗುವುದು!
"""
    drivers_please_send_a_valid_image_text = "❌ ದಯವಿಟ್ಟು ಒಂದು ಮಾನ್ಯ ಚಿತ್ರವನ್ನು ಕಳುಹಿಸಿ."
    drivers_payment_proof_sent_text = (
        "✅ ನಿಮ್ಮ ಪಾವತಿ ಪ್ರೂಫ್ ಅಡಿಯಲ್ಲಿ ಅಡಿಯಲ್ಲಿ ಕಳುಹಿಸಲಾಗಿದೆ. ಅನುಮೋದನೆಯನ್ನು ನಿರೀಕ್ಷಿಸಿ."
    )
    drivers_payment_proof_verified_text = """
✅ ನಿಮ್ಮ ಪಾವತಿ ಪ್ರೂಫ್ ಪರಿಶೀಲಿಸಲಾಗಿದೆ! ಈಗ ನಿಮಗೆ ಡ್ರೈವರ್ ಗುಂಪಿಗೆ ಪ್ರವೇಶವಿದೆ.
ಆಹ್ವಾನ ಲಿಂಕ್: {group_link}
"""
    drivers_payment_proof_rejected_text = """
❌ ನಿಮ್ಮ ಪಾವತಿ ಪ್ರೂಫ್ ನಿರಾಕರಿಸಲಾಗಿದೆ.
ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ದಯವಿಟ್ಟು ನಿರೀಕ್ಷಿಸಲು ನಿರ್ವಾಹಕರಿಗೆ ಸಂಪರ್ಕಿಸಿ.
"""

    drivers_you_were_not_let_in_group_no_sub_text = """
❌ ನೀವು ಗುಂಪಿಗೆ ಪ್ರವೇಶಿಸಲು ಅನುಮತಿ ಕೊಡಲಾಗಿಲ್ಲ.
ನಿಮಗೆ ಸಕ್ರಿಯ ಚುಕ್ತಿಯಿಲ್ಲ, ಆದ್ದರಿಂದ ಸವಾರಿಗೆ ಪಾಲಿಪರಿಗೆ ಭಾಗಿಯಾಗಲು ಸಾಧ್ಯವಿಲ್ಲ.
ನೋಡುವುದಕ್ಕಾಗಿ /start ಕಳುಹಿಸಿ.
"""
    drivers_you_were_let_in_group_has_sub_text = """
✅ ನೀವು ಗುಂಪಿಗೆ ಪ್ರವೇಶಿಸಲು ಅನುಮತಿ ಕೊಟಲಾಗಿದೆ! ಸ್ವಾಗತ!
"""
    drivers_you_were_kicked_group_no_sub_text = """
❌ ನೀವು ಗುಂಪಿನಿಂದ ತಿರಸ್ಕರಿಸಲ್ಪಟ್ಟಿದ್ದೀರಿ, ಏಕೆಂದರೆ ನಿಮ್ಮಲ್ಲಿ ಚುಕ್ತಿ ಇಲ್ಲ.
/start ಕಳುಹಿಸಲು ಸಾಧ್ಯವಿದೆ.
"""
    drivers_subscription_24_hours_left_notification_text = """
⏳ ನಿಮ್ಮ ಚುಕ್ತಿ 24 ಗಂಟೆಗಳಲ್ಲಿ ಕೊನೆಗೊಳ್ಳುತ್ತದೆ.
ಕೆಳಗಿನ ಬಟನ್ ಮೂಲಕ ಅದನ್ನು ನೀವು ನವೀಕರಿಸಬಹುದು.
"""

    drivers_subscription_1_hour_left_notification_text = """
⏳ ನಿಮ್ಮ ಚುಕ್ತಿ 1 ಗಂಟೆಯಲ್ಲಿ ಕೊನೆಗೊಳ್ಳುತ್ತದೆ.
ಕೆಳಗಿನ ಬಟನ್ ಮೂಲಕ ಅದನ್ನು ನೀವು ನವೀಕರಿಸಬಹುದು.
"""

    drivers_ride_already_accepted_text = """
❌ ಕ್ಷಮಿಸಿ, ಈ ಸವಾರಿ ಈಗಾಗಲೇ ಇನ್ನೊಬ್ಬ ಡ್ರೈವರ್‌ದ್ವಾರ ಸ್ವೀಕರಿಸಲ್ಪಟ್ಟಿದೆ.
"""
    update_driver_details = """
Update driver details
    """
    drivers_you_have_successfully_accepted_the_ride_text = """
✅ ನೀವು ಸವಾರಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಸ್ವೀಕರಿಸಿದ್ದೀರಿ!
ಬಳಕೆದಾರರ ಟೆಲಿಗ್ರಾಮ್ ವಿವರಗಳು:
{user_details}

ಚಲಾನೆ ವಿವರಗಳು:
{drive_details}
"""
    drivers_i_could_not_message_you_text = """
❌ ನಿಮಗೆ ಸಂದೇಶ ಕಳುಹಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.
ದಯವಿಟ್ಟು ನೀವು ಬಾಟ್‌ನೊಂದಿಗೆ ಮಾತನಾಡಲು ಪ್ರಾರಂಭಿಸಿದ್ದೀರೆಂದು ಖಚಿತಪಡಿಸಿ.
"""
    drivers_ride_details = """
📜 ಸವಾರಿ #{id}
📍 ನಿಂದ: `{text_from}` [ಲಿಂಕ್]({google_maps_from_url})
🏁 ಗೆರೆಗು: `{text_to}` [ಲಿಂಕ್]({google_maps_to_url})
🚕 ವರ್ಗ: {category}
🛣 ದೂರತ್ವ: {distance} ಕಿಲೋಮೀಟರುಗಳು
⌛️ ಅವಧಿ: {duration}
💲 ವೆಚ್ಚ: {cost}
🕐 ಪಿಕಪ್ ಸಮಯ: {pickup_time}
📲 ದೂರವಾಣಿ ಸಂಖ್ಯೆ: {phone_number}
👤 ಪೂರ್ಣ ಹೆಸರು: {full_name}
"""
    drivers_please_pay_subscription_text = """
💳 ನಿಮ್ಮ ಚುಕ್ತಿ ಮುಗಿಯಿತು.
ಬಾಟ್ ಬಳಸುವುದಕ್ಕೆ ನಿಮ್ಮ ಚುಕ್ತಿಗೆ ಪಾವತಿ ಪಾಡಿ.
"""
    confirm_vendor_upgrade = "Are you sure you want to upgrade to a vendor?"  # todo : change in other languages
    you_are_already_vendor = "You are already a vendor"  # todo : change in other languages

    drivers_planned_drive_alert_text = """
ಪ್ರಿಯ ಡ್ರೈವರ್, ನಿಮ್ಮ ಸವಾರಿ ನಿಯೋಜನೆ {time_left} ನಲ್ಲಿದೆ. ನಿಮ್ಮ ಸವಾರಿಯ ವಿವರಗಳು ಇಲ್ಲಿವೆ:

{ride_info}
"""

    # ====== riders bot ================================================================================================
    riders_referrals_info_text = f"""
👥 ರೆಫರಲ್‌ಗಳು
🔗 ನಿಮ್ಮ ರೆಫರಲ್ ಲಿಂಕ್ (ರೈಡರ್‌ಗಾಗಿ): {{referral_link}}
👥 ರೆಫರಲ್ ಸಂಖ್ಯೆ: {{referral_count}}
👥💰 ಮನ್ಯೋಗಾನ್ನು: {{redeemable_amount}}

ನೀವು {constants.Constants.referrals_for_free_ride} ರೆಫರಲ್‌ಗಳನ್ನು ಉಚಿತ ಸವಾರಿಗೆ ವಿನಿಯೋಗಿಸಬಹುದು.
"""

    description = ["\nOne Time Booking to any location.\n",
                   "\nTo & Fro booking : Book for Departure and Arrival and get cab assurance & 5% off !\n",
                   "\nAwww...For commutes with your furry friends! Get an All-Inclusive fare with our Pet Friendly Drivers !\n",
                   "\nFor your InterCity Requirements.\n",
                   "\nFixed Driver for Fixed Duration : Simple!\nSelect Duration - Select Days - Pickup and Dropoff Time - Book.\n ",
                   "\nHire cab on basis of hours selected."]
    riders_welcome_text = """
👋 {name} ಸ್ವಾಗತ! ಈ ಬಾಟ್ ನಿಮಗೆ ಒಂದು ಸವಾರಿಯನ್ನು ಹುಡುಕುವುದರ ಜೊತೆಗೆ ನೆರವಾಗುತ್ತದೆ.

Before proceeding please update your details once by clicking on /info.
"""
    help = "Press on /order or /start to leave the booking process in middle and start booking again.\nFor more help contact @username"
    rider_enter_droptime_for_commute = "ಡ್ರಾಪ್ ಸಮಯ ನಮೂದಿಸಿ:"
    rider_enter_picktime_for_commute = "ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ ಮೊದಲ ಪ್ರಯಾಣ"
    riders_please_select_booking_type_text = "ಬುಕಿಂಗ್ ಪ್ರಕಾರ ಆಯ್ಕೆಮಾಡಿ:"
    riders_booking_type_btns = [
        [Button.inline("➡️ಒಂದು ಬಾರಿ", data="cabcategory|0"),
         Button.inline("🔃  ರೌಂಡ್-ಟ್ರಿಪ್", data="cabcategory|1")],
        [Button.inline("🏢 ಕಚೇರಿ", data="cabcategory|2"),
         Button.inline("🏞  ಹೊರಗಡೆಕ್ಕೆ", data="cabcategory|0")],
        [Button.inline("🐕‍🦺 Pet Friendly Cab")],
        [Button.inline(cancel_btntext, data="start|clear")]
    ]
    prev_question_button = [Button.inline(
        prev_step_btntext,
        data=f"order_goto_step|"
    )]
    cancel_btn = [Button.inline(cancel_btntext, data="start|clear")]

    hours_buttons_for_intracity = hours_buttons_for_intracity = [
        [Button.inline('3', data='intracity|hours|3'), Button.inline('4', data='intracity|hours|4'),
         Button.inline('5', data='intracity|hours|5'), Button.inline('6', data='intracity|hours|6')],
        [Button.inline('7', data='intracity|hours|7'), Button.inline('8', data='intracity|hours|8'),
         Button.inline('9', data='intracity|hours|9'), Button.inline('10', data='intracity|hours|10')],
        [Button.inline('11', data='intracity|hours|11'), Button.inline('12', data='intracity|hours|12'),
         Button.inline('13', data='intracity|hours|13'), Button.inline('14', data='intracity|hours|14')],
        cancel_btn
        ]
    days = ['ಸೋಮ', 'ಮಂಗಳ', 'ಬುಧ', 'ಗುರು', 'ಶುಕ್ರ', 'ಶನಿ', 'ಭಾನು']
    riders_enter_commute_days = "ನೀವು ಎಷ್ಟು ದಿನಗಳವರೆಗೆ ಬಯಸುತ್ತೀರಿ: "
    enter_no_of_hours = "Select number of hours you want to rent the cab for : "
    riders_start_order_button = Button.inline("🚖 ಆರ್ಡರ್ ಆರಂಭಿಸಿ", data="start_order")
    ride_step_date = """
📆 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸವಾರಿಯ ದಿನಾಂಕವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ. 
ಫಾರ್ಮ್ಯಾಟ್:
ದಿನ.ತಿಂಗಳು.ವರ್ಷ
📅 ಪ್ರಸ್ತುತ ದಿನಾಂಕ: `{date_now}`
"""
    ride_step_time = """
⏰ ದಯವಿಟ್ಟು ನಿಮ್ಮ ಸವಾರಿಯ ಸಮಯವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ. 
ಫಾರ್ಮ್ಯಾಟ್:
ಗಂಟೆ:ನಿಮಿಷ
🕑 ಪ್ರಸ್ತುತ ಸಮಯ: `{time_now}`
"""
    ride_step_full_name = "👤 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರನ್ನು ನಮೂದಿಸಿ"
    ride_step_phone_number = "📞 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಫೋನ್ ನಂಬರನ್ನು ನಮೂದಿಸಿ"
    ride_step_from = """
🚩 ದಯವಿಟ್ಟು ನೀವು ಹೊರಟುವ ಸ್ಥಳದ ಭೂಮಿಗೆ ಲಿಂಕ್‌ಗಳನ್ನು ಸೇರಿಸಿ (ಅಥವಾ ಕೈಮಾತ್ರದಿಂದ ನಮೂದಿಸಿ)
__ಸ್ಕ್ರೀನ್‌ನ ಕೆಳಭಾಗದ ಬಲಬಾಗಿಯಲ್ಲಿ ಕಾಗದದ ಕೊಂಬು (📎) ಮತ್ತು ಸ್ಥಳದ ಚಿಹ್ನೆ (📍) ಕ್ಲಿಕ್ ಮಾಡಿ__
"""
    ride_step_to = """
🏁 ದಯವಿಟ್ಟು ನೀವು ಬರುವ ಸ್ಥಳದ ಭೂಮಿಗೆ ಲಿಂಕ್‌ಗಳನ್ನು ಸೇರಿಸಿ (ಅಥವಾ ಕೈಮಾತ್ರದಿಂದ ನಮೂದಿಸಿ)
__ಸ್ಕ್ರೀನ್‌ನ ಕೆಳಭಾಗದ ಬಲಬಾಗಿಯಲ್ಲಿ ಕಾಗದದ ಕೊಂಬು (📎) ಮತ್ತು ಸ್ಥಳದ ಚಿಹ್ನೆ (📍) ಕ್ಲಿಕ್ ಮಾಡಿ__
"""
    riders_please_select_category_text = """
🚦 ದಯವಿಟ್ಟು ನೀವು ಸವಾರಿ ಮಾಡಬೇಕಾದ ವರ್ಗವನ್ನು ಆರಿಸಿ:
"""
    riders_answer_incorrect_format_text = """
🤔 ನಿಮ್ಮ ಉತ್ತರ ತಪ್ಪಾಗಿದೆ. ನಿರ್ದೇಶನಗಳನ್ನು ಪರಿಗಣಿಸಿ ಮತ್ತೊಮ್ಮೆ ಪ್ರಯತ್ನಿಸಿ.
"""
    riders_please_provide_date_in_future_text = """
🤔 ಪ್ರಸ್ತುತ ದಿನಾಂಕ ಅಥವಾ ಭವಿಷ್ಯದ ದಿನಾಂಕವನ್ನು ನೀಡಿ.
"""
    riders_please_provide_time_in_future_text = """
🤔 ಪ್ರಸ್ತುತ ಸಮಯ ಅಥವಾ ಭವಿಷ್ಯದ ಸಮಯವನ್ನು ನೀಡಿ.
"""
    riders_no_route_found_text = """
❌ ಯಾವುದೇ ಮಾರ್ಗವನ್ನು ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು "ಹಿಂದಿನ" ಬಟನ್ ಒತ್ತಿರಿ ಮತ್ತು ವಿವಿಧ ವಿಳಾಸವನ್ನು ನಮೂದಿಸಿ.
"""
    place_not_found_please_specify_better_text = """
❌ ಸ್ಥಳ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು ಸರಿಯಾಗಿ ವಿಳಾಸವನ್ನು ನಮೂದಿಸಿದ್ದಾರೆಯೆಂದು ನಿಶ್ಚಯಿಸಿ.
"""
    riders_location_not_found_text = """
❌ ಸ್ಥಳ ಕಂಡುಬಂದಿಲ್ಲ. ದಯವಿಟ್ಟು "ಹಿಂದಿನ" ಬಟನ್ ಒತ್ತಿರಿ ಮತ್ತು ವಿವಿಧ ವಿಳಾಸವನ್ನು ನಮೂದಿಸಿ.
"""

    riders_ride_data_preview_text = (
            """
    📝 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಡೇಟಾವನ್ನು ಪರಿಶೀಲಿಸಿ:
    
    🚖 ವರ್ಗ: {category}
    
    📆 ಪ್ರಾರಂಭ: {datetime}
    👤 ಹೆಸರು: {full_name}
    📞 ಫೋನ್ ನಂಬರ್: {phone_number}
    
    🛣 ದೂರತ್ವ: {distance} ಕಿ.ಮೀ.
    ⏳ ಅವಧಿ: {duration}
    
    💵 ಬೆಲೆ: ₹{price}
    
    💳 ಕೈಗಾರಿಕೆ ಬೆಲೆ: ~~₹99~~ ₹"""
            + str(constants.Constants.ride_order_cost)
    )
    riders_confirm_order_btntext = "✅ ಆರ್ಡರ್ ದೃಢೀಕರಿಸಿ"
    riders_please_pay_for_reservation_text = f"""
💳 ನೀವು ಆರ್ಡರ್ ದೃಢೀಕರಣಕ್ಕಾಗಿ ₹`{constants.Constants.ride_order_cost}`  ಪಾಲಿಸಬೇಕಾಗುತ್ತದೆ.
ಮುಂದುವರಿಯಲು ಕೆಳಗಿನ ಬಟನ್ ಮೇಲೆ ಕ್ಲಿಕ್ ಮಾಡಿ.

ನೀವು {constants.Constants.referrals_for_free_ride} ರೆಫರಲ್‌ಗಳನ್ನು ಉಚಿತ ಸವಾರಿಗೆ ವಿನಿಯೋಗಿಸಬಹುದು.
"""
    riders_you_can_pay_with_referral_add_text = """
👥 ನೀವು ರೆಫರಲ್ ಪಾಯಿಂಟ್‌ಗಳನ್ನು ಉಪಯೋಗಿಸಿ ದೃಢೀಕರಣಕ್ಕೆ ಸಾಲದ ಪಾಲು ({required}) ಪಾವತಿಯನ್ನು ಪಾಲಿಸಬಹುದು.
ಮುಂದುವರಿಯಲು ಕೆಳಗಿನ ಬಟನ್ ಮೇಲೆ ಕ್ಲಿಕ್ ಮಾಡಿ.
"""
    riders_pay_btntext = "💳 ಪಾವತಿ"
    riders_pay_with_referral_btntext = "💳 ರೆಫರಲ್ ಪಾಯಿಂಟ್‌ಗಳನ್ನು ಉಪಯೋಗಿಸಿ ಪಾವತಿ ಪಾಲಿಸಿ"
    riders_here_is_payment_qr_text = """
💳 ಇಲ್ಲಿ ನಿಮ್ಮ ಪಾವತಿಗೆ QR ಕೋಡ್ ಇದೆ.
ಪಾವತಿ ಮಾಡಿದ ನಂತರ "ಪಾವತಿ ಮಾಡಿದ" ಬಟನ್‌ಗೆ ಕ್ಲಿಕ್ ಮಾಡಿ.
"""
    riders_payed_btntext = "✅ ಪಾವತಿ ಮಾಡಿದ"
    riders_please_send_screen_of_payment_text = """
📷 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪಾವತಿಯ ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಕಳುಹಿಸಿ.
"""
    riders_please_send_a_valid_image_text = "❌ ದಯವಿಟ್ಟು ಸಾಲದ ಚಿತ್ರವನ್ನು ಕಳುಹಿಸಿ."
    riders_thanks_for_payment_text = """
✅ ನಿಮ್ಮ ಪಾವತಿಗಾಗಿ ಧನ್ಯವಾದಗಳು!
ದೃಢೀಕರಣದ ನಂತರ, ಆರ್ಡರ್‌ಗಳನ್ನು ಡ್ರೈವರ್‌ಗಳಿಗೆ ಕಳುಹಿಸಲಾಗುತ್ತದೆ.
"""
    riders_payment_rejected_text = """
❌ ನಿಮ್ಮ ಪಾವತಿಯನ್ನು ಖಾರಗಾರಿಕೆಗೆ ತಂದುಕೊಳ್ಳಲಾಗಿದೆ.
ಹೆಚ್ಚಿನ ಮಾಹಿತಿಗಾಗಿ ನಿರ್ವಾಹಕರಿಗೆ ಸಂಪರ್ಕಿಸಿ.
"""
    riders_payment_accepted_text = """
✅ ನಿಮ್ಮ ಪಾವತಿಯನ್ನು ಸ್ವೀಕರಿಸಲಾಗಿದೆ! ಆರ್ಡರ್ ಐಡಿ: #{drive_id}
ಆರ್ಡರ್‌ಗಳನ್ನು ಡ್ರೈವರ್‌ಗಳಿಗೆ ಕಳುಹಿಸಲಾಗಿದೆ.
ಚಾಲಕ ನಿಮ್ಮ ಆದೇಶವನ್ನು ಸ್ವೀಕರಿಸಿದಾಗ ನಿಮಗೆ ಸೂಚಿಸಲಾಗುತ್ತದೆ
"""
    riders_user_drive_details_text = """
🚖 ನಿಮ್ಮ ಆರ್ಡರ್ ಆದ ಡ್ರೈವರ್ #{id} ಅವರ ಸ್ವಾಗತವನ್ನು ಸ್ವೀಕರಿಸಿರಿ!
ಡ್ರೈವರ್ ಟೆಲಿಗ್ರಾಮ್ ವಿವರಗಳು:
{driver_details}

📲 ಫೋನ್ ನಂಬರ್: {driver_phone_number}
👤 ಪೂರ್ಣ ಹೆಸರು: {driver_full_name}
🚖 ವಾಹನ ಹೆಸರು: {vehicle_name}
🔢 ವಾಹನ ನೆಗೆಯ ಸಂಖ್ಯೆ: {vehicle_plate_number}
ಒಳ್ಳೆಯ ಪ್ರಯಾಣವನ್ನು ಮಾಡಿ!
"""
    riders_ride_details_text = """
🚖 ಸವಾರಿ #{id} ವಿವರಗಳು:

⚫ ವರ್ಗ: {category}
📍 [ಯಾವುದಿಂದ]({google_maps_from_url})
🏁 [ಯಾವುದಕ್ಕೆ]({google_maps_to_url})
📆 ಹೊರಟುಹೋಗುವ ದಿನಾಂಕ: {departure}
👤 ಚಾಲಕರ ಹೆಸರು: {driver_full_name}
📞 ಚಾಲಕರ ಫೋನ್ ಸಂಖ್ಯೆ: {driver_phone_number}
🚖 ವಾಹನದ ಹೆಸರು: {driver_vehicle_name}
🔢 ವಾಹನ ಸಂಖ್ಯೆ: {driver_vehicle_number}
🛣 ದೂರವು: {distance} ಕಿಲೋಮೀಟರ್‌ಗಳು
⏳ ಅವಧಿ: {duration}
💵 ಬೆಲೆ: ₹{cost}
"""
    please_validate_departure_place_text = f"""
🤔 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಹೊರಡೆಯಲ್ಲಿರುವ ಸ್ಥಳವನ್ನು ಪರಿಶೀಲಿಸಿ.
ನೀವು ಆಯ್ಕೆ ಮಾಡಿದ್ದೀರಿ: {{departure}}
ಇದು ತಪ್ಪಾಗಿದ್ದರೆ, '{prev_step_btntext}' ಬಟನ್ ಅನ್ನು ಒತ್ತಿಹಾಕಿ ಬೇರೆ ವಿಳಾಸವನ್ನು ನಮೂದಿಸಿ.
"""
    please_validate_destination_place_text = f"""
🤔 ದಯವಿಟ್ಟು ನಿಮ್ಮ ಗಮನಕ್ಕೆ ಬರುವ ಸ್ಥಳವನ್ನು ಪರಿಶೀಲಿಸಿ.
ನೀವು ಆಯ್ಕೆ ಮಾಡಿದ್ದೀರಿ: {{destination}}
ಇದು ತಪ್ಪಾಗಿದ್ದರೆ, '{prev_step_btntext}' ಬಟನ್ ಅನ್ನು ಒತ್ತಿಹಾಕಿ ಬೇರೆ ವಿಳಾಸವನ್ನು ನಮೂದಿಸಿ.
"""
    drive_should_have_started_mb_alert_text = """
🚖 ಡ್ರೈವ್ ಆರಂಭವಾಗಿರುತ್ತಿರಬೇಕು! (#{id})
ನೀವು ಆಪತ್ಕಾಲದಲ್ಲಿ ಇದ್ದರೆ, ದಯವಿಟ್ಟು ಪೊಲೀಸ್‌ಗೆ ಕಾಲ್ ಮಾಡಿ ಮತ್ತು ನಿರ್ವಾಹಕರಿಗೆ ಚೇತರಿಕೆಯನ್ನು ಕಳುಹಿಸಲು ಕೆಳಗಿನ ಬಟನ್‌ನ್ನು ಒತ್ತಿಹಾಕಿ.
"""
    drive_should_have_started_mb_alert_btn_text = "🆘 ಚೇತರಿಕೆ ಕಳುಹಿಸಿ"
    drive_should_have_started_mb_alert_sent_text = "✅ ಚೇತರಿಕೆ ಕಳುಹಿಸಲಾಗಿದೆ!"

    did_you_have_a_ride = """
🚖 ನಮಸ್ಕಾರ! ನೀವು ಸವಾರಿ ಮಾಡಿದ್ದೀರಾ ಅಥವಾ ರೈಡ್ ಮಾಡಿದ್ದೀರಾ #{id}?

ರೈಡ್ ವಿವರಗಳು:
📍 [ಇಂದ]({google_maps_from_url})
🏁 [ನಂತರ]({google_maps_to_url})
📆 ಪ್ರಯಾಣ: {departure}
👤 ಡ್ರೈವರ್ ಹೆಸರು: {driver_full_name}
👤 ರೈಡರ್ ಹೆಸರು: {rider_full_name}
"""
    yes_btntext = "✅ ಹೌದು"
    no_btntext = "❌ ಇಲ್ಲ"
    please_select_rating_text = """
🤔 ದಯವಿಟ್ಟು ರೇಟಿಂಗ್ ಆಯ್ಕೆಮಾಡಿ.
"""
    please_send_comment_text = f"""
🤔 ದಯವಿಟ್ಟು ಟಿಪ್ಪಣಿ ಕಳುಹಿಸಿ.
ನೀವು '{skip_btntext}' ಬಟನ್ ಒತ್ತಿಹಾಕಬಹುದು.
"""
    thanks_for_feedback_text = """
✅ ನಿಮ್ಮ ಪ್ರತಿಕ್ರಿಯೆಗಾಗಿ ಧನ್ಯವಾದಗಳು!
"""
    riders_planned_drive_alert_text = """
ಪ್ರಿಯ ಸವಾರಿ, ನಿಮ್ಮ ಸವಾರಿ ನಿಯೋಜನೆ {time_left} ನಲ್ಲಿದೆ. ನಿಮ್ಮ ಸವಾರಿಯ ವಿವರಗಳು ಇಲ್ಲಿವೆ:

{ride_info}
"""


locales = {
    "en": En,
    "hi": Hi,
    "kn": Kn,
}


def validate():
    if len(locales) < 2:
        print("Nothing to validate")
        return
    import re

    regexp = re.compile(r"(?<!\{)\{([^{}]+)}(?!})")

    keys = {x: set(y.__dict__.keys()) for x, y in locales.items()}

    any_errors = False

    # validate formatting

    for locale_a, locale_a_keys in keys.items():
        for locale_b, locale_b_keys in keys.items():
            if locale_a == locale_b:
                continue
            for key in locale_a_keys:
                if key not in locale_b_keys:
                    any_errors = True
                    print(
                        f"Key `{key}` not found in {locale_b}, but found in {locale_a}"
                    )
                    continue
                if not isinstance(getattr(locales[locale_a], key), str):
                    continue
                locale_a_val = getattr(locales[locale_a], key)
                locale_b_val = getattr(locales[locale_b], key)

                all_a_format_keys = set(re.findall(regexp, locale_a_val))
                all_b_format_keys = set(re.findall(regexp, locale_b_val))

                for a_fmt_key in all_a_format_keys:
                    if a_fmt_key not in all_b_format_keys:
                        any_errors = True
                        print(
                            f"Formatting key `{a_fmt_key}` not found in {locale_b}, but found in `{locale_a}.{key}`"
                        )

    if any_errors:
        raise Exception("Errors in locales file.")
