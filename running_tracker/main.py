import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "runs.json"


class Race:
    """Represents a single running race with distance and time. Provides a method to calculate pace."""

    def __init__(self, distance_km: float, time_seconds: int):
        if not isinstance(distance_km, (int, float)):
            raise TypeError("Distance must be numeric.")
        if not isinstance(time_seconds, int):
            raise TypeError("Time must be an integer.")

        if distance_km <= 0:
            raise ValueError("Distance must be greater than zero.")
        if time_seconds <= 0:
            raise ValueError("Time must be greater than zero.")

        self._distance_km = distance_km
        self._time_seconds = time_seconds

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Race:
        """Creates a Race instance from a dictionary containing distance and time."""
        return cls(distance_km=data["distance_km"], time_seconds=data["time_seconds"])

    @property
    def distance_km(self) -> float:
        """Returns the distance of the race in kilometers."""
        return self._distance_km

    @property
    def time_seconds(self) -> int:
        """Returns the time of the race in seconds."""
        return self._time_seconds

    @property
    def pace_seconds_per_km(self) -> float:
        """Calculates and returns the pace of the race in seconds per kilometer."""
        return self._time_seconds / self._distance_km

    def to_dict(self) -> dict[str, float | int]:
        """Converts the Race instance to a dictionary format."""
        return {"distance_km": self._distance_km, "time_seconds": self._time_seconds}


class RunningTracker:
    """Manages a collection of races and provides methods to add races and retrieve them."""
    def __init__(self):
        self._races: list[Race] = []

    def load_races(self, races: list[Race]) -> None:
        self._races = races

    def add_race(self, distance_km: float, time_seconds: int) -> None:
        """Adds a new race to the tracker after validating the input."""
        self._races.append(Race(distance_km, time_seconds))

    def get_all_races(self) -> list[Race]:
        """Returns the list of races currently stored in the tracker."""
        return self._races.copy()

    def get_race(self, index: int) -> Race:
        """Retrieves a specific race by its index after validating the input."""
        if not 0 <= index < len(self._races):
            raise IndexError("Race index out of range.")
        return self._races[index]


class FileManager:
    """Handles loading and saving of race data to and form a JSON file."""
    def load(self) -> list[Race]:
        """Loads races from a JSON file and returns them as a list of Race objects."""
        try:
            with open(FILE_PATH, "r") as f:
                raw_data = json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
        return [Race.from_dict(item) for item in raw_data]

    def save(self, races: list[Race]) -> None:
        """Converts the current list of races to dictionaries and saves them to a JSON file."""
        raw_data = [race.to_dict() for race in races]
        with open(FILE_PATH, "w") as f:
            json.dump(raw_data, f, indent=4)


# CLI Flows
def add_race_flow(tracker: RunningTracker) -> None:
    """Handles the user input flow for adding a new race to the tracker."""
    parsed_time_seconds: int
    while True:
        distance_km = input("Enter distance in kilometers ('Type menu to return to main menu'): ").strip()
        time_seconds = input("Enter time in seconds or MM:SS ('Type menu to return to main menu'): ").strip()
        if distance_km.lower() == "menu" or time_seconds.lower() == "menu":
            print("Returning to main menu.")
            return
        if time_seconds.isdigit():
            parsed_time_seconds = int(time_seconds)
        elif re.match(r"^[0-5]\d:[0-5]\d$", time_seconds):
            minutes, seconds = map(int, time_seconds.split(":"))
            parsed_time_seconds = minutes * 60 + seconds
        else:
            print("Invalid time format. Please enter time as seconds or in MM:SS format.")
            continue
        try:
            tracker.add_race(float(distance_km), parsed_time_seconds)
        except (TypeError, ValueError) as e:
            print(f"{e}")
            continue
        break
    print("Race succesfully added!")


def calculate_pace_flow(tracker: RunningTracker) -> None:
    """Handles the user input flow for calculating the pace of a selected race."""
    if not tracker.get_all_races():
        print("No races available.")
        return
    print_formatted_races(tracker)
    while True:
        user_index = input("Select a race by number to calculate pace ('Type menu to return to main menu'): ").strip()
        if user_index.lower() == "menu":
            print("Returning to main menu.")
            return
        if not user_index.isdigit():
            print("Invalid input. Please enter a valid race number or 'menu'.")
            continue
        try:
            selected_race = tracker.get_race(int(user_index) - 1)
        except (IndexError, TypeError, ValueError) as e:
            print(f"Error selecting race: {e}")
            continue
        formatted_pace = format_seconds_to_time(selected_race.pace_seconds_per_km)
        print(f"Pace: {formatted_pace} min/km")
        break


def print_formatted_races(tracker: RunningTracker) -> None:
    """Prints the list of races in a formatted manner for user selection."""
    raw_races = tracker.get_all_races()
    lines: list[str] = []
    for i, race in enumerate(raw_races, start=1):
        formatted_time = format_seconds_to_time(race.time_seconds)
        lines.append(f"{i}. {race.distance_km}km - {formatted_time}")
    print("\n".join(lines))


def format_seconds_to_time(seconds: int | float) -> str:
    """Formats a given number of seconds into a MM:SS string format."""
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes)}:{seconds:02.0f}"


def load_from_file_flow(tracker: RunningTracker, file_manager: FileManager, race: type[Race]) -> None:
    """Handles the user input flow for loading races from a file."""
    while True:
        confirmation = input("This will overwrite your current data. Do you want to continue? (yes/no): ").strip()
        if confirmation.lower() == "yes":
            loaded_races = file_manager.load()
            tracker.load_races(loaded_races)
            print("Data loaded successfully.")
            break
        elif confirmation.lower() == "no":
            print("Load cancelled. Returning to main menu.")
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


def save_to_file_flow(tracker: RunningTracker, file_manager: FileManager, race: type[Race]) -> None:
    """Handles the user input flow for saving races to a file."""
    while True:
        confirmation = input("This will overwrite your saved data. Do you want to continue? (yes/no): ").strip()
        if confirmation.lower() == "yes":
            file_manager.save(tracker.get_all_races())
            print("Data saved successfully.")
            break
        elif confirmation.lower() == "no":
            print("Save cancelled. Returning to main menu.")
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


ACTIONS = {
    "add race": add_race_flow,
    "calculate pace": calculate_pace_flow
}

FILE_ACTIONS = {
    "load": load_from_file_flow,
    "save": save_to_file_flow
}

tracker = RunningTracker()
file_manager = FileManager()

# Main CLI loop
while True:
    user_action = input("Choose an action (add race/calculate pace/save/load/quit): ").strip().lower()
    if user_action == "quit":
        print("Exiting the program.")
        break
    action = ACTIONS.get(user_action)
    file_action = FILE_ACTIONS.get(user_action)
    if action:
        action(tracker)
    elif file_action:
        file_action(tracker, file_manager, Race)
    else:
        print("Invalid action. Please choose 'add race', 'calculate pace', 'save', 'load', or 'quit'.")
