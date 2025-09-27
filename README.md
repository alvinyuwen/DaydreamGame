# MazeJoggers

MazeJoggers is a **2D maze survival game built with Python and Pygame**.  
Navigate through **6 challenging levels**, avoid invisible traps, beat the countdown timer, and wisely use your limited abilities to reach the end.  

---

## Gameplay

- Start with **6 health**.  
- Each new level reduces **base health by 1**.  
- Reach the **green exit tile** to progress.  
- Some floor tiles are **invisible traps** → stepping on one costs **1 health**.  
- If your health reaches 0 → **Game Over**.  
- Complete all 6 levels to become the **WINNER** 🎉.  

---

## Timer

- Level 1: **45 seconds**.  
- Each next level subtracts **5 seconds** (Level 2 = 40s, Level 3 = 35s, …).  
- Timer **starts only after your first move** in each level.  
- Run out of time → **Game Over**.  

---

## Abilities

You have 5 special abilities in total (use them wisely!):

- **Gain One Life (x2)** → Adds +1 temporary health for the current level.  
- **Break Wall (x2)** → Destroys one wall next to you.  
- **Draw Path (x1)** → Reveals the shortest path to the exit for 8 seconds.  

Once an ability is used, it’s gone forever.  

---

## Controls

| Key | Action |
|-----|--------|
| **Arrow Keys / WASD** | Move (hold to move smoothly) |
| **1** | Use *Gain One Life* |
| **2** | Use *Break Wall* |
| **3** | Use *Draw Path* |
| **SPACE** | Start the game |
| **R** | Restart after Game Over / Victory |
| **ESC** | Exit game |

---

## Screens

- **Title Screen** → Rules & abilities.  
- **Game Screen** → Maze + health + abilities + timer.  
- **Game Over Screen** → Retry or quit.  
- **Victory Screen** → Colourful celebratory blocks + “WINNER”.  

---

## Installation & Running

1. Install [Python 3.10+](https://www.python.org/downloads/).  
2. Install **Pygame**:  
   ```bash
   pip install pygame
