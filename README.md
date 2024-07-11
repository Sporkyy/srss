# Shortcuts - Run Shell Scripts

These scripts are for use in the macOS Shortcuts app and executed as a Quick
Action in Finder.

## Step 1: Allow Shortcuts to Run Scripts

- Shortcuts
- ↳ Settings...
- ↳ Advanced
- ↳ ☑ Allow Running Scripts _(ticked)_

## Step 2: Create a Shortcut

- File
- ↳ New Shorcut

## Step 3: Configure it as a Quick Action

- Shortcut Details
- ↳ Details
- ↳ ☑ Use as Quick Action _(ticked)_
- ↳ ☑ Finder _(ticked)_

## Step 4: Configure it to Receive Files

- Receive [Images and 18 more]
- ↳ Untick all but "Files"

## Step 5: Add a Run Shell Script Action

- Action Library
- ↳ Run Shell Script

## Step 6: Configure the Run Shell Script Action

- Shell: 【`python3`】 _(/usr/bin/python3)_
- Input: 【`Shortcut Input`】 _(default)_
- Pass Input: 【`as arguments`】
- Run as Administrator: 🙩 _(unticked)_

## Step 7: Copy+Paste in the Python Script

- ✂️ 📋 🐍

## Lessons so far

- Using a shell from Homebrew is annoying
  - The location changes between Apple Silicon and x86-64
- Give up and use Python
  - It's not real shell scripting; it's easier
