# MelonDS Cheat Splitter
Splits Nintendo DS `cheats.xml` files into MelonDS-compatible `.mch` files.

- MelonDS releases: https://melonds.kuribo64.net/
- Cheat DB releases (this is where you'll find the latest cheats.xml): https://gbatemp.net/threads/deadskullzjrs-nds-i-cheat-databases.488711/

## Usage
- Download this repo. If on Windows, you can instead download an executable [here](https://github.com/TheRealPSV/MelonDSCheatSplitter/releases/latest/download/MelonDSCheatSplitter.exe) or from the Releases page.
- Place your `cheats.xml` file next to `split_cheats_melonds.py` or the downloaded `MelonDSCheatSplitter.exe` if on Windows.
- Install the Python version specified in `.python-version`, and run `split_cheats_melonds.py` with it (the command is `python .\split_cheats_melonds.py`).
  - If using Windows, you don't need to install anything, just run the downloaded `MelonDSCheatSplitter.exe` instead.
  - NOTE: you can pass `--help` to the program for optional arguments.
- Once the program finishes, you should find `.mch` files in an `MCH/` folder next to the program.
- Find the file corresponding to the game you want to apply cheats to, place it next to the game's `.nds` file, and rename it to match the `.nds` file (for example, if the game's `.nds` file is `game.nds` rename the `.mch` file to `game.mch`).
- Once you launch the game in MelonDS, you should be able to go to the `System` menu, make sure `Enable cheats` is checked, then choose `Setup cheat codes`. From there, your cheats will be available.