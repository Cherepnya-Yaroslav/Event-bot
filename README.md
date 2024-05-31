# Event Bot

This is a Telegram bot for managing events. The bot allows users to view and add events to their favorites, search for events by date, and suggest new events. Admins can moderate suggested events and clear database entries up to a specified date.

## Features

- **Start Menu**: Users can choose to view favorites, search for events, or manage their events.
- **Search Events**: Users can search for events by date or view events for the upcoming week.
- **Favorites**: Users can add events to their favorites and view their favorite events.
- **Suggest Events**: Users can suggest new events, including title, description, and an optional image.
- **Admin Features**: Admins can moderate suggested events, approve or reject them, and clear database entries up to a specified date.

### Prerequisites

- Python 3.7+
- `python-telegram-bot` library
- `python-dotenv` library
- 
### Commands

- `/start`: Display the start menu with options to view favorites, search events, and manage events.
- `/menu`: Display the start menu.
- `/moderate`: Admin command to view and moderate suggested events.
- `/status`: Display the status of user's suggested events.
- `/clear_all_data`: Admin command to clear all data in the database up to a specified date.

### Handlers

- `command_handlers.py`: Handles command-related functions, such as `/start`, `/menu`, and `/clear_all_data`.
- `callback_handlers.py`: Handles button callbacks, such as viewing favorites, searching events, and adding events to favorites.
- `message_handlers.py`: Handles messages, such as text and photo inputs for suggesting events.


