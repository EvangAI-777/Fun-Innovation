# Academic Planner Study Hub -- Studio Setup

**Version 1.0.1** -- API audit: font enums updated to BuilderSans/BuilderSansBold

## Overview

A virtual campus where every player gets a dorm room with a desk. Assignments appear as color-coded sticky notes on the desk surface -- green for upcoming, yellow for due soon, red for overdue, gray for completed. A shared library displays who's studying what on a central whiteboard. Study rooms have group timers for focused sessions. Paste syllabus text into a text box and the system parses it into assignments automatically.

## Scripts

| File | Type | Place In |
|------|------|----------|
| `PlannerConfig.luau` | ModuleScript | ReplicatedStorage |
| `AssignmentManager.luau` | ModuleScript | ServerStorage |
| `PlannerServer.luau` | Script | ServerScriptService |
| `PlannerClient.luau` | LocalScript | StarterPlayer > StarterPlayerScripts |

## Setup Steps

1. Open Roblox Studio and create a new Baseplate experience (or an empty place)
2. **Delete the default Baseplate** -- the server builds the entire campus
3. Enable **API Services** in Game Settings > Security (required for DataStore)
4. Create a **ModuleScript** in **ReplicatedStorage**, rename it to `PlannerConfig`, paste the contents of `PlannerConfig.luau`
5. Create a **ModuleScript** in **ServerStorage**, rename it to `AssignmentManager`, paste the contents of `AssignmentManager.luau`
6. Create a **Script** in **ServerScriptService**, rename it to `PlannerServer`, paste the contents of `PlannerServer.luau`
7. Create a **LocalScript** in **StarterPlayer > StarterPlayerScripts**, rename it to `PlannerClient`, paste the contents of `PlannerClient.luau`
8. Press **Play** to test

**Note:** DataStore does not work in Studio test mode without enabling API Services. For local testing, assignments will not persist between sessions but all other functionality works.

## What You Should See

- A campus lobby with warm stone flooring and a "STUDY HUB" sign
- Directional signs pointing to Dorms, Library, and Study Rooms
- Your personal dorm room with a wooden desk and chair
- Your name on the door sign
- A library building with study tables and a "Who's Studying What" whiteboard
- 8 study rooms with whiteboards showing group timers
- Bottom toolbar with "+ New Assignment", "Paste Syllabus", and "Study Groups" buttons
- Top-left HUD showing your upcoming assignments color-coded by urgency

## Controls

- **+ New Assignment** -- Open the assignment creation panel
- **Paste Syllabus** -- Open the syllabus text parser
- **Study Groups** -- Open the study group/timer panel
- **E** (ProximityPrompt on desk) -- Open your planner
- **E** (ProximityPrompt on whiteboard) -- View study group timer or library board
- **H** -- Toggle the upcoming assignments HUD
- **Esc** -- Close any open panel

## Features

| Feature | How It Works |
|---------|-------------|
| Assignment CRUD | Add, complete, delete assignments with class info and due dates |
| Sticky notes on desk | Top 8 assignments appear as colored 3D notes on your desk surface |
| Color-coded urgency | Green (upcoming), yellow (due within 2 days), red (overdue), gray (done) |
| Syllabus parsing | Paste text, system detects assignment keywords and date patterns |
| Dorm rooms | Each player gets a private room with their name on the door |
| Library whiteboard | Shows all active players and what classes they're working on |
| Study groups | Join a study room (up to 6 players per room) |
| Group timer | Pomodoro-style countdown (default 25 min), start/pause/reset controls |
| Persistence | DataStore saves assignments per player (auto-save every 2 min) |

## Architecture

```
Client (PlannerClient)
  |-- Assignment creation panel: abbreviation, class, assignment, date, time
  |-- Assignment list: scrollable with complete/delete per row
  |-- Syllabus panel: paste text, parse, add detected items individually
  |-- Study group panel: join/leave rooms, start/pause/reset timers
  |-- HUD: top-left upcoming assignments color-coded by status
  |-- Feed: top-right notification messages

Server (PlannerServer)
  |-- DataStore load/save per player (auto-save every 2 min + on leave)
  |-- Assignment CRUD handlers with input validation
  |-- Dorm room allocation (one per player on join, cleaned up on leave)
  |-- Study group membership tracking per room
  |-- Timer tick loop (1-second interval for active timers)
  |-- Library whiteboard update (aggregates all players' active classes)
  |-- Campus generation on init (lobby, library, study rooms)

AssignmentManager
  |-- Campus geometry: lobby, dorm rooms, library, study rooms
  |-- Desk + chair + sticky note construction with SurfaceGui
  |-- Date parsing (M/D/YYYY, M-D-YYYY) with time (12-hour AM/PM)
  |-- Syllabus text parser (keyword + date pattern detection)
  |-- Whiteboard + timer display updates
  |-- Data serialization / deserialization

Shared (PlannerConfig)
  |-- Campus dimensions, materials, colors
  |-- Desk and sticky note sizing
  |-- Status colors and urgency thresholds
  |-- Assignment limits, study group limits
  |-- Timer defaults, interaction ranges
```

## Tuning

Key values in `PlannerConfig.luau`:

- `MaxAssignmentsPerPlayer` -- Cap on assignments per player (default 50)
- `DueSoonThreshold` -- Seconds before due date to turn yellow (default 2 days)
- `DefaultTimerDuration` -- Study timer default in seconds (default 1500 = 25 min)
- `MaxTimerDuration` -- Maximum timer duration (default 7200 = 2 hours)
- `MaxStudyRooms` -- Number of study rooms (default 8)
- `MaxGroupMembers` -- Players per study group (default 6)
- `DeskInteractionRange` -- How close to interact with a desk (default 8)

## No Dependencies

Everything is self-contained. DataStore is the only Roblox service that requires API Services enabled. `HttpService` is used solely for `JSONEncode`/`JSONDecode` (DataStore serialization) -- no network requests are made. No plugins, no external assets.
