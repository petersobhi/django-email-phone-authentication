from djexmo import send_message


def send_verification_sms(phone_number, passcode):
    send_message(to=str(phone_number),
                 text='Your activation code for ForFilm is: ' + passcode + '  ')
