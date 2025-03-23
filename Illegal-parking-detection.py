from inference_sdk import InferenceHTTPClient
import base64
import io
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


client = InferenceHTTPClient(
    api_url="http://localhost:9001", # use local inference server
    api_key="//not mentioned due to privacy reasons//"
)

result = client.run_workflow(
    workspace_name="drone-dwnqy",
    workflow_id="custom-workflow-3",
    images={
        "image": "FootageDrone/DJI_0028.JPG"
    }
)
base64_str = [item['dynamic_crop'] for item in result]
base64_data = base64_str[0][0]
png = base64.b64decode(base64_data)
image = Image.open(io.BytesIO(png))


image.show()
print("Please Check the image for any error")
save_path = "IllegalParkedCar/Output.png"
image.save(save_path)

ocr = [item['google_vision_ocr'] for item in result]
ocr_data = ocr[0][0]

print("Illegally parked vehicle found with License Plate: ", ocr_data)

extracted_text = ocr_data
formatted_text = extracted_text[0].replace("\n", " ").strip()
with open("database.txt", "r") as file:
    database_entries = [line.strip() for line in file.readlines()]

# Check for a match
found = False
for entry in database_entries:
    # Split the entry into license plate, name, and email
    plate, name, email = map(str.strip, entry.split(","))
    if formatted_text == plate:
        print(f"Match found: {formatted_text}")
        print(f"Registered to: {name}")
        print(f"Email: {email}")
        found = True

        # Compose the email
        sender_email = "ticketenforcement@gmail.com"  # Replace with your email
        sender_password = "rrbk eypq uzwq kzcc"  # Replace with your email password
        subject = f"Parking Ticket for {formatted_text}"
        body = f"""
        Dear {name},

        This is to inform you that your vehicle with license plate {formatted_text} was detected as illegally parked.

        Kindly address this matter immediately.

        Regards,
        Parking Authority
        """

        # Create email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        attachment = MIMEApplication(open(save_path, "rb").read())
        attachment.add_header('Content-Disposition', 'attachment', filename="proof.png")
        msg.attach(attachment)

        try:
            # Send email
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Upgrade to secure connection
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, msg.as_string())
            print(f"Email sent successfully to {email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
        break

if not found:
    print(f"No match found for: {formatted_text}")
