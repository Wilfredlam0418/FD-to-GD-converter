# FD-to-GD-converter
A Famidash to Geometry Dash level converter, written in Python. If you do not know what Famidash is, read more [here](https://github.com/tfdsoft/famidash).

## How to use
Before you run any file, you have to ensure that 2 things are done.

1. You have to ensure that Python is downloaded to your computer. If not, you will have to download it. Note that downloading Python is different for each operating system.
2. You have to ensure that the latest development version of GMDKIT is downloaded. If not, then run `pip install git+https://github.com/UHDanke/gmdkit.git`.
3. You have to ensure that GDShare is installed in Geometry Dash via Geode. If you do not have Geode, you can download it [here](https://geode-sdk.org/).

After you have done both things above, you now follow the instructions below.

## Converting a level
A Famidash level is a TMX with its metadata defined by a JSON5. The former can be found in `famidash-main/LEVELS/LEVEL DATA/lvlset_HUGE`, while the latter can be found in `famidash-main/LEVELS/metadata`. <br>
For example, the TMX file for Stereo Madness is `stereomadness.tmx`, with its metadata found in both `lvlset_A_metadata.json5` and `lvlset_HUGE_metadata.json5`.

A Geometry Dash level is a GMD.

To convert a Famidash level to a Geometry Dash level, you can follow the instructions below.

1. Move the TMX and JSON5 files into the FD to GD converter file.
2. Open the Terminal. You can find it by searching "Terminal".
3. Enter `cd` followed by the path to the file. For example, if your FD to GD converter is located in the Desktop, you would enter `cd Desktop/FD-to-GD-converter-main`.
4. Run `python main.py`. Then insert the information about the level, including the names of the TMX, JSON5 and the resulting GMD.
5. Import the level into Geometry Dash via GDShare. Click on the magenta file button above the green list button to import the GMD file.
