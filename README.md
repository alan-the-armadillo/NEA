# GRAFTED - NEA PROJECT

A dungeon-crawler roguelike game created for my CS NEA project.

### Author

[@alan-the-armadillo](https://github.com/alan-the-armadillo)

## Concept

Grafted is a dungeon-crawler roguelike game in which you play as a robot defeating enemies.
Enemies will drop loot such as weapons which you may equip, and may even drop their limbs.
You can graft these limbs in place of your own, developing your robot further and further.

## Controls
 - wasd : up, left, down and right respectively
 - e : interact
 - \# : screenshot (screenshots saved to screenshots folder within program folder)
 - escape : close program

## Current progress
This project is a work-in-progress, with some core functionality not yet implemented. Planned features include:

- animation system
- items
- ability to attack
- enemy drops
- inventory
- level progression
- save file system
- finalised graphics

There are some helper programs in the helper programs folder.
The **control setter** is to show the respective integer for each pygame input.
The **item helper**, while still in development, makes adding items to the main json file much easier.
The **anim helper**, while still in development, makes creating animations easier.
The helper programs will not be in the final program folder as user modding is not a goal of my game, and have not been made for easy user experience for others.

## Requirements

- Windows
- Python 3.13+

## Dependencies:
- pygame
  
To install, use the following format in command prompt:
```bash
pip install pygame
```

## To run
To run this program, use the following commands in a command prompt:
```bash
git clone https://github.com/alan-the-armadillo/NEA.git
cd NEA
python main.py
```
