import requests
import time
import os
from rich.console import Console

# Configuration constants
TOKEN = "PASTE YOUR TOKEN HERE"
DELAY = 2  # Change the status every DELAY seconds
LOG_CHANGE = True  # Whether to log the status change
CLEAR_TERMINAL = False  # Whether to clear the terminal after a specific interval
CLEAR_INTERVAL = 30  # After how many status changes should the terminal be cleared

FILENAME = "statuses.txt"  # Change to your filename
MODE_SEPARATOR = ";;"  # MESSAGE ;; MODE

console = Console()

BANNER = r"""
 ____  _        _                 ____           _           
/ ___|| |_ __ _| |_ _   _ ___    / ___|   _  ___| | ___ _ __ 
\___ \| __/ _` | __| | | / __|  | |  | | | |/ __| |/ _ \ '__|
 ___) | || (_| | |_| |_| \__ \  | |__| |_| | (__| |  __/ |   
|____/ \__\__,_|\__|\__,_|___/   \____\__, |\___|_|\___|_|   
                                      |___/                                                             
"""


def clear_terminal():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def fetch_user(token):
    """Fetch the Discord username using the provided token."""
    header = {"Authorization": token}
    response = requests.get("https://discord.com/api/v10/users/@me", headers=header)

    if response.status_code == 200:
        return response.json()["username"]
    else:
        return None


def read_statuses(filename):
    """Read status messages from a file."""
    if not os.path.exists(filename):
        console.print(f"[bold red]Error:[/bold red] File '{filename}' does not exist.")
        return []

    statuses = []
    last_mode = "online"
    with open(filename, "r") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            if MODE_SEPARATOR in line:
                status, mode = line.rsplit(MODE_SEPARATOR, 1)
                mode = mode.strip().lower()

                if not mode in ["online", "dnd", "invisible", "invis", "on", "idle"]:
                    console.print(
                        f"[bold red]Error:[/bold red] Invalid mode '{mode}' in line {line_number}: '{line}'. Skipping."
                    )
                    continue

                mode = "invisible" if mode == "invis" else mode
                mode = "online" if mode == "on" else mode
                last_mode = mode  # Update last valid mode
                statuses.append((status.strip(), mode))

            else:
                console.print(
                    f"[bold yellow]Warning:[/bold yellow] Using last mode '{last_mode}' for line {line_number}: {line}."
                )
                statuses.append((line.strip(), last_mode))
    return statuses


def set_status(status, status_mode, token=TOKEN):
    """Change the user's status message."""
    header = {"Authorization": token}
    custom_status = {"text": status}

    response = requests.patch(
        "https://discord.com/api/v10/users/@me/settings",
        headers=header,
        json={"custom_status": custom_status, "status": status_mode},
    )
    return response


def format_mode(mode):
    """Return the formatted mode with colors."""
    if mode == "online":
        return "[bold green]Online[/bold green]"
    elif mode == "dnd":
        return "[bold red]Do Not Disturb[/bold red]"
    elif mode == "idle":
        return "[yellow]Idle[/yellow]"
    elif mode == "invisible":
        return "[gray]Invisible[/gray]"
    return mode


def main():
    """Main function to run the status changer."""
    console.print(BANNER, style="bold cyan")
    user = fetch_user(TOKEN)
    if user is None:
        console.print("Error: Invalid token.", style="bold red")
        return

    console.print(f"Logged in as: [bold green]{user}[/bold green].")

    console.print("Loading statuses...", style="yellow")
    statuses_with_modes = read_statuses(FILENAME)
    if len(statuses_with_modes) == 0:
        console.print("Error: No valid statuses found.", style="bold red")
        return

    console.print(
        f"Loaded [bold green]{len(statuses_with_modes)}[/bold green] statuses."
    )
    count = 0

    try:
        input("Press enter to start. Press Ctrl + C to exit anytime...")
        while True:
            for status, mode in statuses_with_modes:
                current_time = time.strftime("%I:%M:%S %p")
                response = set_status(status, mode)

                if response.status_code != 200:
                    console.print(
                        f"Failed to change status to: [bold yellow]{status}[/bold yellow]",
                        style="bold red",
                    )
                    continue

                count += 1
                if LOG_CHANGE:
                    formatted_mode = format_mode(mode)
                    log_message = f"[{current_time}] Status changed to: [bold yellow]{status}[/bold yellow] | Mode: {formatted_mode} | Count: [cyan]{count}[/cyan]"
                    console.print(log_message)

                if CLEAR_TERMINAL and count % CLEAR_INTERVAL == 0:
                    clear_terminal()

                time.sleep(int(DELAY))
    except KeyboardInterrupt:
        console.print("\nExiting...", style="bold red")


if __name__ == "__main__":
    main()
