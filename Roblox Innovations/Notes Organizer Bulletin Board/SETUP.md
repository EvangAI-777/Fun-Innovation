# Notes Organizer Bulletin Board -- Studio Setup

**Version 1.0.3** -- Multi-player room overlap fix, pending folder ID resolution, position input validation, DataStore error logging

## Overview

A shared creative space where notes are physical objects. Write a note, click a wall or surface to place it, and it becomes a framed sign anyone can read. Folders become rooms -- separate 3D spaces with themed accent colors and door signs. Notes persist across sessions via DataStore. Other players can read your public notes; private notes appear faded to others.

## Scripts

| File | Type | Place In |
|------|------|----------|
| `BulletinConfig.luau` | ModuleScript | ReplicatedStorage |
| `NoteManager.luau` | ModuleScript | ServerStorage |
| `BulletinServer.luau` | Script | ServerScriptService |
| `BulletinClient.luau` | LocalScript | StarterPlayer > StarterPlayerScripts |

## Setup Steps

1. Open Roblox Studio and create a new Baseplate experience (or an empty place)
2. **Delete the default Baseplate** -- the server builds its own lobby floor and rooms
3. Enable **API Services** in Game Settings > Security (required for DataStore)
4. Create a **ModuleScript** in **ReplicatedStorage**, rename it to `BulletinConfig`, paste the contents of `BulletinConfig.luau`
5. Create a **ModuleScript** in **ServerStorage**, rename it to `NoteManager`, paste the contents of `NoteManager.luau`
6. Create a **Script** in **ServerScriptService**, rename it to `BulletinServer`, paste the contents of `BulletinServer.luau`
7. Create a **LocalScript** in **StarterPlayer > StarterPlayerScripts**, rename it to `BulletinClient`, paste the contents of `BulletinClient.luau`
8. Press **Play** to test

**Note:** DataStore does not work in Studio test mode without enabling API Services. For local testing, notes will not persist between sessions but all other functionality works.

## What You Should See

- A marble-floor lobby with a "BULLETIN BOARD" sign
- Bottom toolbar with "+ New Note" and "+ New Room" buttons
- Click "+ New Note" to open the creation panel (title, body, folder selector)
- Click "Place on Surface" then click any wall, floor, or surface to pin the note
- Notes appear as framed signs with title, body text, and author name
- Walk up to any note and use the proximity prompt (E) to read the full content
- "+ New Room" creates a new walled room with a door, colored accent stripe, and sign
- Activity feed in the top right shows who pinned, edited, or removed notes

## Controls

- **+ New Note** -- Open the note creation panel
- **+ New Room** -- Create a new folder-room
- **Place on Surface** -- Enter placement mode; click any surface to pin
- **E** (ProximityPrompt) -- Read a note when nearby
- **Esc** -- Cancel placement, close read overlay, or close creation panel

## Features

| Feature | How It Works |
|---------|-------------|
| Note creation | Title + body text, assign to a folder/room |
| Surface placement | Raycast-based; notes snap to walls, floors, any Part surface |
| Folder rooms | Each folder is a physical room with walls, door, themed accents |
| Public/private | Toggle visibility; private notes appear faded to non-owners |
| Persistence | DataStore saves all notes and folders per player |
| Read overlay | ProximityPrompt opens a clean reading view of any note |
| Activity feed | Real-time notifications when anyone pins, edits, or removes notes |

## Architecture

```
Client (BulletinClient)
  |-- Creation panel: title, body, folder selector
  |-- Placement mode: raycast preview, click to pin
  |-- Read overlay: proximity prompt triggers full-text view
  |-- Activity feed: shows real-time note events

Server (BulletinServer)
  |-- DataStore load/save per player (auto-save every 2 min + on leave)
  |-- CRUD handlers: create, update, delete notes; create/delete folders
  |-- Builds lobby on init, rooms on player join
  |-- NoteManager builds physical 3D note models with SurfaceGui

Shared (BulletinConfig)
  |-- Note sizes, colors, materials, placement range
  |-- Room dimensions, themes, max counts
  |-- DataStore key, interaction settings
```

## Tuning

Key values in `BulletinConfig.luau`:

- `NotePartSize` -- Physical size of each note frame
- `RoomSize` -- Interior dimensions of folder rooms
- `MaxNotesPerPlayer` -- Cap on notes per player (default 50)
- `MaxRooms` -- Cap on rooms/folders per player (default 12)
- `InteractionRange` -- How close you need to be to read a note
- `PlacementRange` -- How far you can place a note from your character
- `PublicByDefault` -- Whether new notes start as public or private

## No Dependencies

Everything is self-contained. DataStore is the only Roblox service that requires API Services enabled. `HttpService` is used solely for `JSONEncode`/`JSONDecode` (DataStore serialization) -- no network requests are made. No plugins, no external assets.
