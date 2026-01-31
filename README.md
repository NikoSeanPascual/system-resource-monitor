# NSR Monitor (Niko’s System Resource Monitor)

A modern **System Resource Monitor** built with **CustomTkinter** and **psutil**.  
Designed with a terminal-inspired neon UI and real-time system statistics.(I won't be updating this project anymore, you're free to use it and do whatever you want with it =))

---

## Features

### 📊 Live Monitoring
- **CPU usage** (percentage + core count)
- **RAM usage** (used / total)
- **Disk usage** (used / total)

### 📈 Real-Time Graphs
- CPU usage history (neon green)
- RAM usage history (dim green)
- Smooth scrolling graph with configurable data points

### 🚨 Smart Alerts
- Logs warnings when:
  - CPU usage exceeds 85%
  - RAM usage exceeds 85%
  - Disk usage exceeds 90%
- Timestamped alert logs

### ⏸ Control Panel
- Pause / Resume monitoring
- Change update interval:
  - 0.5s
  - 1s
  - 2s
- Clear logs instantly

### 🎨 UI & UX
- Dark cyber-style theme
- Progress bars with dynamic color changes
- Fixedsys retro font aesthetic
- Clean dashboard layout

---

## Libraries Used

- `customtkinter` – modern UI framework
- `psutil` – system resource access
- `collections.deque` – efficient history storage
- `datetime` – timestamped logs

## How It Works (High-Level)

1. Uses `psutil` to fetch system stats
2. Updates UI on a timed loop (`after`)
3. Stores history using fixed-size deques
4. Draws graphs manually using `CTkCanvas`
5. Triggers alerts when thresholds are exceeded

---

## Requirements

```bash
pip install customtkinter psutil
