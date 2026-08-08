# 🎓 Intelligent Campus Networking System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-00D4FF?style=for-the-badge)
![NetworkX](https://img.shields.io/badge/NetworkX-3.x-10B981?style=for-the-badge)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-F59E0B?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-7C3AED?style=for-the-badge)

**A social network graph application for student connectivity and intelligent recommendations — powered by Graph Data Structures and BFS.**

*Built with the same algorithms that power Facebook, LinkedIn, and Spotify.*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Algorithms & Data Structures](#-algorithms--data-structures)
- [Real World Connections](#-real-world-connections)
- [Screenshots](#-screenshots)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Team](#-team)

---

## 🌐 Overview

The **Intelligent Campus Networking System (ICNS)** is a desktop application that models a university campus as a **social network graph**. Students are represented as **nodes** and their relationships as **edges** in an adjacency list — the exact same structure used by the world's largest social platforms.

The system solves four real problems students face on campus:

| Problem | Solution |
|---|---|
| Hard to find peers with similar interests | Interest matching via Set intersection |
| Can't find study partners across departments | Greedy scoring algorithm |
| Don't know who connects them to others | BFS shortest path via Queue |
| No way to discover new people | Mutual friends graph traversal |

---

## ✨ Features

### 👥 Student Management
- **Add Student** — Register name, department, and interests
- **Edit Student** — Update department or interests at any time
- **Delete Student** — Remove student and all their connections with confirmation dialog
- **Search Student** — Find and highlight any student with one click

### 🔗 Connection Management
- **Connect Students** — Create bidirectional friendship edges in the graph
- **Remove Connection** — Disconnect two students with confirmation
- **Show Connections** — Visual card popup showing all connections per student

### 🔍 Discovery & Recommendations
- **Interest Matching** — Find all students sharing a specific interest (keyword search)
- **Mutual Friends** — Suggest new connections via shared friends, with shared interest highlighting and a one-click Connect button
- **Most Popular** — Highlight the most connected student in the network
- **Smart Study Partner** — AI-style greedy scoring recommends the best study match with detailed reasons

### 📡 Graph Algorithms
- **Shortest Path (BFS)** — Visual node-chain popup showing the minimum hops between any two students with step-by-step breakdown
- **Network Visualization** — Full NetworkX + Matplotlib graph rendered with department-colored nodes and scaled sizing by degree

### 📊 Analytics Dashboard
- **6 live stat cards** — Students, Connections, Departments, Avg Connections, Density, Top Interest
- **Network Health Score** — 0–100 score calculated from density, connections, and size
- **Department Bar Chart** — Matplotlib-rendered bar chart with per-department color coding
- **Top 3 Leaderboard** — Gold/Silver/Bronze ranked most-connected students with avatars
- **Extra stats strip** — Most popular, most active department, top interest, density

### 🎨 UI/UX
- **Student Card Grid** — 3-column card view with avatar circles, dept badges, interest tags, ★ TOP badge
- **Live Search** — Debounced real-time filtering by name
- **Department Filter** — Dropdown to filter cards by department
- **Profile Popup** — Full student profile with 2-column connection grid and shared interest highlights
- **Toast Notifications** — Color-coded slide-in toasts for all actions
- **Cards / Log toggle** — Switch between card grid and activity log views
- **Persistent storage** — All data saved to `students.txt` on every change

---

## 🧠 Algorithms & Data Structures

### 1. Graph — Adjacency List

```python
network = {
    "Alice": ["Bob", "Carol"],
    "Bob":   ["Alice", "Dave"],
    ...
}
```

Every student is a **node (vertex)**. Every connection is a **bidirectional edge**. The graph is stored as a Python dictionary of lists — an **adjacency list** — giving O(1) average lookup by name.

---

### 2. BFS — Breadth-First Search `O(V + E)`

Used for **Shortest Connection Path** between any two students.

```
Algorithm:
1. Add start student to Queue
2. While Queue is not empty:
     current = dequeue front
     if current == target → DONE, backtrack path
     for each unvisited neighbor:
         mark visited, set parent, enqueue
3. Reconstruct path from parent[] array
```

BFS guarantees the **minimum number of hops** because it explores all nodes at distance 1 before distance 2, etc. This is identical to how LinkedIn calculates "2nd degree connections."

---

### 3. Queue — FIFO `deque`

Powers the BFS traversal. Python's `collections.deque` is used for O(1) append and popleft operations.

```
State:  [A✓] [B✓] [C ← processing] [D] [E]
         done  done    active         next next
         ← dequeue                    enqueue →
```

---

### 4. Greedy Scoring — Study Partner `O(N)`

Scans every other student and computes a compatibility score:

```python
score = 0
if same_department:              score += 3
for each shared interest:        score += 2
for each mutual connection:      score += 1
```

The student with the **highest total score** is recommended. This is a classic **greedy algorithm** — it makes the locally optimal choice at each comparison step.

---

### 5. Set Intersection — Interest Matching `O(min(a, b))`

```python
shared = set(interests[student_A]) & set(interests[student_B])
```

Python sets use hash tables internally, making intersection sub-linear. Used in both interest matching and the study partner scoring.

---

### 6. HashMap / Dictionary `O(1)` average

Three dictionaries store all data:

```python
network     = { name: [connections] }   # graph edges
departments = { name: "CS" }            # node attribute
interests   = { name: ["AI", "DB"] }    # node attribute
```

O(1) average lookup, insertion, and deletion by student name.

---

### Complexity Summary

| Operation | Time Complexity | Data Structure |
|---|---|---|
| Add / Find student | O(1) average | Dictionary |
| Add / Remove connection | O(degree) | Adjacency List |
| Shortest path (BFS) | O(V + E) | Queue + Dict |
| Study partner recommendation | O(N) | Greedy + Set |
| Interest matching | O(N × k) | Set |
| Mutual friends | O(degree²) | Adjacency List |
| Network density | O(1) | Math formula |

---

## 🌍 Real World Connections

The data structures and algorithms in this project are the **exact same foundations** used by billion-dollar platforms:

| Platform | How They Use It |
|---|---|
| **Facebook** | Adjacency list graph + BFS for "People You May Know" |
| **LinkedIn** | BFS finds 1st / 2nd / 3rd degree connections |
| **Instagram** | Follower graph + Queue-based feed ranking |
| **Spotify** | BFS traverses song similarity graph for "Recommended" |
| **Google Maps** | BFS / Dijkstra for shortest route between locations |
| **Discord** | Weighted graph models server communities and roles |
| **YouTube** | Queue-based BFS crawls related video recommendation graph |

> *"The algorithms we implemented are not student exercises — they are production-level algorithms running at billions of requests per day at Meta, Google, and LinkedIn."*

---

## 📸 Screenshots

### Main Card View
> *Add screenshot here — the 3-column student card grid with dept colors, avatars, and interest tags*

### Student Profile Popup
> *Add screenshot here — compact hero with side-by-side avatar + name, stat boxes, 2-col connection grid*

### Smart Study Partner
> *Add screenshot here — partner card + 2-column reason grid*

### Shortest Path Visualization
> *Add screenshot here — node chain with department-colored avatars and step-by-step cards*

### Live Analytics Dashboard
> *Add screenshot here — 6 stat cards, matplotlib bar chart, top-3 leaderboard*

### Network Graph (NetworkX)
> *Add screenshot here — full graph visualization with dept-colored nodes*

---

## 📁 Project Structure

```
campus-network/
│
├── campus_network_gui.py     # Main application (all code in one file)
├── students.txt              # Auto-generated data file (pipe-separated)
└── README.md                 # This file
```

### Data File Format (`students.txt`)

```
Name|Department|Interests|Connections
Alice|CS|AI,DB,Web|Bob,Carol
Bob|AI|ML,Deep Learning|Alice,Dave
Carol|SE|Web,UI|Alice
```

Each line represents one student. The file is read on startup and written on every add, edit, delete, or connection change.

---

## ⚙️ Installation

### Requirements

- Python 3.10 or higher
- pip

### Step 1 — Clone or download

```bash
git clone https://github.com/AhsanTatiq7/Campus-Networking-System.git
cd campus-network
```

### Step 2 — Install dependencies

```bash
pip install customtkinter networkx matplotlib
```

### Step 3 — Run

```bash
python campus_network_gui.py
```

> **Windows users:** If you see a blank window on first launch, resize it once — this is a known CustomTkinter startup quirk on some Windows versions.

---

## 🚀 Usage

### Adding Your First Students

1. Click **Add Student** in the sidebar
2. Enter name, department (CS / AI / SE / EE / ME / BBA / DS / IT), and interests (comma-separated)
3. Click **Save Student** — the card appears immediately in the grid

### Connecting Students

1. Click **Connect Students**
2. Enter two student names exactly as added
3. Click **Connect** — both cards update their connection count

### Finding the Shortest Path

1. Click **Shortest Path**
2. Enter start and target student names
3. Click **Find Path** — a visual popup shows the node chain and step-by-step hops

### Getting a Study Partner

1. Click **Study Partner**
2. Enter your student name
3. The system scores all other students and returns the best match with colored reason cards

### Opening the Dashboard

1. Click **Live Dashboard**
2. See live stats, matplotlib department chart, top-3 leaderboard, and network health score

---

## 👥 Team

| Role | Name | 
|---|---|
| **Developer** | Muhammad Ahsan Tariq |
| **Developer** | Muhammad Taha Khan | 



---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core language |
| CustomTkinter | 5.x | Modern dark-themed GUI |
| NetworkX | 3.x | Graph data structure + spring layout |
| Matplotlib | 3.x | Network visualization + dashboard charts |
| collections.deque | stdlib | BFS queue |
| File I/O | stdlib | Persistent data storage |

---

## 📐 Key Design Decisions

**Why adjacency list over adjacency matrix?**
The campus network is sparse — most students connect to a small fraction of all students. An adjacency list uses O(V + E) space vs O(V²) for a matrix, and neighbor iteration is faster for sparse graphs.

**Why BFS over DFS for shortest path?**
DFS explores depth-first and may find *a* path but not the *shortest* one. BFS explores level by level, guaranteeing minimum hops in an unweighted graph — which is exactly what social distance means.

**Why deque over list for the queue?**
Python `list.pop(0)` is O(n) because it shifts all elements. `collections.deque.popleft()` is O(1). For large networks this matters significantly.

**Why greedy for study partner?**
A greedy approach gives O(N) time with explainable results. Each factor (department, interests, mutual connections) has a clear weight and shows up in the "Why this match?" reason cards — making the recommendation transparent and educational.

---

