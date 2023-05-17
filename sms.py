import vonage


def send_sms_vonage(to_phone_number, body):
    client = vonage.Client(key='e96a6627', secret='FjUsE1elQrobT0Hz')
    sms = vonage.Sms(client)

    response_data = sms.send_message(
        {
            "from": "Vonage APIs",
            "to": to_phone_number,
            "text": body
        }
    )

    if response_data["messages"][0]["status"] == "0":
        print("Message sent successfully.")
    else:
        print(f"Error: {response_data['messages'][0]['error-text']}")
