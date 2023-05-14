import os
from fastapi import FastAPI, HTTPException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, SendAt, To

app = FastAPI()

@app.post("/send_mail")
async def send_mail_handler(payload: dict):
    os.environ['TO_SEND_MAIL'] = payload['sg_token']

    def create_message(recipient):
        personalized_body = payload['body'].replace("{receiver_name}", recipient['name'])
        personalized_body = payload['body'].replace("{receiver_city}", recipient['city'])
        print(personalized_body)
        message = Mail(
            from_email=payload['from'],
            to_emails=To(email=recipient['email'], name=recipient['name']),
            subject=payload['subject'],
            html_content=personalized_body)
        if 'send_at' in payload:
            message.send_at = SendAt(payload['send_at'])
            print(message)
        return message

    try:
        sg = SendGridAPIClient(os.environ['TO_SEND_MAIL'])
        for recipient in payload['to']:
            message = create_message(recipient)
            response = sg.send(message)
            if response.status_code != 202:
                raise HTTPException(status_code=response.status_code, detail=response.body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "Emails sent successfully!"}
