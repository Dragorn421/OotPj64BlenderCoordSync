# OotPj64BlenderCoordSync
Synchronize Link's coordinates in Ocarina of Time 64 in Project64 with a Blender object

[Hylian Modding discord](https://discordapp.com/invite/74pHDEU)

## Installation
The py script is a blender addon and can be installed as such.

The js script is for Project64: put it in the Scripts folder (create the folder if needed) in your Project64 install directory

## Usage
Offsets used are for the MQ debug rom, probably won't work with any other rom

Tested with Blender 2.79b and Project64 v2.4.0-1127-g185c658 (a March 2020 nightly build)

### Project64
A recent nightly (development) build may be required
1. Enable Debugger: uncheck `Hide advanced settings` in `Options > Settings > Options` and check `Enable debugger` in the new `Advanced` tab
2. Run script: go to `Debugger > Scripts` and run the script (double-click the script entry, or right-click it and `Run`). It will start listening on port 80
3. Load the MQ debug rom (may be important to do this step last, had several crashs when loading the script with the rom already loaded) and go whereever

### Blender
2.8x won't work due to API changes. Script could easily be ported though due to how small it is.
1. Install add-on: `File > User Preferences > Add-ons > Install Add-on from File...`, choose the file, enable the add-on, remember to save
2. For starting synchronization, select an object
3. Invoke operator: open the `Operator Search` (with the Space key by default in 2.79), search "oot64", click Start or Stop to start or stop the synchronization

#### Start operator
Updates per second: Choose how many times a second to sync coordinates

Scale: apply a multiplier to coordinates, scale is in blender units per oot units (imported zmap are 1:1 in scale)

Hit OK to start synchronizing coordinates between Link and the active object

#### Stop operator
This operator stops the sync silently or does nothing if it wasn't running
