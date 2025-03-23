import random
from datetime import datetime
from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
    api_url="http://localhost:9001", # use local inference server
    api_key="07MTHAw4YHEU2802oGx7"
)

# Define possible shapes, colors, and time slots
SHAPES = ['Square', 'Circle', 'Triangle']
COLORS = ['Red', 'Brown', 'Green']
TIMES = ['10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM']

# Store past tickets (only keep last 7 days)
past_tickets = {}
previous_day_schedule = set()


def generate_daily_schedule():
    """Generate a daily schedule ensuring no repetition from the previous day."""
    available_combinations = [(color, shape) for color in COLORS for shape in SHAPES]
    random.shuffle(available_combinations)
    schedule = {}

    for time in TIMES:
        for color, shape in available_combinations:
            if (color, shape) not in previous_day_schedule:
                schedule[time] = (color, shape)
                previous_day_schedule.add((color, shape))
                break

    return schedule


def update_ticket_log():
    """Updates the daily ticket system and maintains past records for 7 days."""
    today = datetime.now().date()

    # Remove entries older than 7 days
    past_keys = list(past_tickets.keys())
    for date in past_keys:
        if (today - date).days > 7:
            del past_tickets[date]

    # Generate a new daily schedule
    ticket_schedule = generate_daily_schedule()
    past_tickets[today] = ticket_schedule

    print("Today's Ticket System:")
    for time, (col, shp) in ticket_schedule.items():
        print(f"Time: {time}, Color: {col}, Shape: {shp}")


def validate_ticket(detected_shape, detected_color):
    """Validates a detected ticket against today's issued schedule."""
    today = datetime.now().date()
    if today in past_tickets:
        ticket_schedule = past_tickets[today]
        return any(detected_shape == shp and detected_color == col for col, shp in ticket_schedule.values())
    return False


# Run daily ticket update
update_ticket_log()

result = client.run_workflow(
    workspace_name="drone-dwnqy",
    workflow_id="custom-workflow-4",
    images={
        "image": "brown-circle.png"
    }
)
# Extract the shape from the model_predictions
shape_prediction = result[0]['model_predictions']['predictions'][0]['class']
detected_shape = shape_prediction.capitalize()  # Ensure the shape is capitalized

# Extract the color from model_1_predictions
color_prediction = result[0]['model_1_predictions'][0]['predictions'][0]['class']
detected_color = color_prediction.capitalize()  # Ensure the color is capitalized
print("ticket detected - ", detected_color, detected_shape)

# Simulated detected ticket from the drone feed
detected_ticket = (detected_shape, detected_color)  # Example ticket
if validate_ticket(*detected_ticket):
    print("Ticket is valid!")
else:
    print("Ticket is invalid!")
