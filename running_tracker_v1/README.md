# Running Tracker V1

A Running Tracker CLI project using Object-Oriented Programming with Python.

## Architecture
- Race (domain object): manages distance and time of a race and calculates pace
- RunningTracker (application): manages Races tracked and is responsible for adding and getting them
- CLI: manages the user-side logic, is responsible for running the program and formatting input and output

---

## Flow
Input -> Parse -> Validate -> Store -> Retrieve -> Format -> Output

---

## Design Decisions
- Separates business logic (Domain and Application) from presentation logic (CLI)
- Add MM:SS parsing support (using re module)
- Run system in a loop and give user the option to exit