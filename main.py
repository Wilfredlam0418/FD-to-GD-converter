# This is the code for the Famidash to Geometry Dash converter.

try:
	import gmdkit
except ModuleNotFoundError:
	raise SystemExit("The module gmdkit is not installed! Run \"pip install gmdkit\" to use this program.")
import copy
import fd_values

file_name = input("TMX file to use: ")
if not file_name[-4:] == ".tmx":
	file_name += ".tmx"

# Copy file level
with open(file_name) as f:
	file = f.read()

# Turn file into list with multiple lines
file_list = [""]
for i in file:
	if i == "\n":
		file_list.append("")
	else:
		file_list[-1] += i

meta_name = input("JSON5 file to use: ")
if not meta_name[-6:] == ".json5":
	meta_name += ".json5"

# Copy file metadata
with open(meta_name) as f:
	meta = f.read()

# Turn file into list with multiple lines
meta_list = [""]
for i in meta:
	if i == "\n":
		meta_list.append("")
	else:
		meta_list[-1] += i

line = 999999

# Extract properties from metadata
for i in range(len(meta_list)):
	if "level:" in meta_list[i] and "\"" + file_name.replace(".tmx", "").lower() + "\"" in meta_list[i]:
		line = i + 1
		break

block_set = song = bg_color = g_color = ""
gamemode = speed = 0
disable_parallax = False

nested = start_offset = 0
offset_multiplier = 1
object_offsets = [{"cx": -1, "cy": -1, "ox": 0, "oy": 0}]
while not (line >= len(meta_list) or "level:" in meta_list[line] or "globalObjectOffsets:" in meta_list[line]):
	if nested == 0:
		quote = False

		# Block set
		if "blockSet:" in meta_list[line]:
			for j in meta_list[line]:
				if j == "\"":
					quote = not quote
				elif quote:
					block_set += j

		# Song
		if "songID:" in meta_list[line]:
			for j in meta_list[line]:
				if j == "\"":
					quote = not quote
				elif quote:
					song += j

		# Starting game mode
		if "startingGameMode:" in meta_list[line]:
			for j in meta_list[line]:
				if j == ":" or j == ",":
					quote = not quote
				elif quote and j.isnumeric():
					gamemode *= 10
					gamemode += int(j)

		# Starting speed
		if "startingSpeed:" in meta_list[line]:
			for j in meta_list[line]:
				if j == ":" or j == ",":
					quote = not quote
				elif quote and j.isnumeric():
					speed *= 10
					speed += int(j)

		# Starting background color
		if "startingBackgroundColor:" in meta_list[line]:
			for j in meta_list[line]:
				if j == "x" or j == ",":
					quote = not quote
				elif quote:
					bg_color += j

		# Starting ground color
		if "startingGroundColor:" in meta_list[line]:
			for j in meta_list[line]:
				if j == "x" or j == ",":
					quote = not quote
				elif quote:
					g_color += j

		# Disabling the parallax, currently not used
		if "parallaxDisable:" in meta_list[line] and "true" in meta_list[line]:
			disable_parallax = True

		# Offsets in objects
		if "objectOffsets:" in meta_list[line]:
			change_mode = axis_change = 0
			nested = 1

	else:
		if "coordinates" in meta_list[line]:
			change_mode = axis_change = 0
			object_offsets.append({"cx": -1, "cy": -1, "ox": 0, "oy": 0})
		if "offsetX" in meta_list[line]:
			change_mode = 1
			axis_change = 0
		elif "offsetY" in meta_list[line]:
			change_mode = axis_change = 1
		for j in meta_list[line]:

			# Skip to the next line if comment reached
			if j == "/":
				break

			# Change number of layers nested
			if j == "{" or j == "[":
				nested += 1
			if j == "}" or j == "]":
				nested -= 1

			if change_mode == 1:

				# Change offset value
				if j.isnumeric():
					if axis_change == 1:
						for k in range(start_offset, len(object_offsets)):
							object_offsets[k]["oy"] *= 10
							object_offsets[k]["oy"] += int(j) * offset_multiplier
					else:
						for k in range(start_offset, len(object_offsets)):
							object_offsets[k]["ox"] *= 10
							object_offsets[k]["ox"] += int(j) * offset_multiplier
				if j == "-":
					if axis_change == 1:
						for k in range(start_offset, len(object_offsets)):
							offset_multiplier = -1
					else:
						for k in range(start_offset, len(object_offsets)):
							offset_multiplier = -1
			else:

				# Change coordinate value
				if j == ",":
					if axis_change == 1:
						object_offsets.append({"cx": -1, "cy": -1, "ox": 0, "oy": 0})
					axis_change = (axis_change + 1) % 2
				if j.isnumeric():
					if axis_change == 1:
						if object_offsets[-1]["cy"] == -1:
							object_offsets[-1]["cy"] = 0
						object_offsets[-1]["cy"] *= 10
						object_offsets[-1]["cy"] += int(j)
					else:
						if object_offsets[-1]["cx"] == -1:
							object_offsets[-1]["cx"] = 0
						object_offsets[-1]["cx"] *= 10
						object_offsets[-1]["cx"] += int(j)
					if object_offsets[start_offset]["ox"] != 0 or object_offsets[start_offset]["oy"] != 0:
						start_offset = len(object_offsets) - 1
	offset_multiplier = 1
	line += 1

fd_values.replace_set("block", block_set)

# Load empty level
level = gmdkit.Level.from_file("empty_level.gmd")

object_list = level.objects

import_data = 0
level_data = []

coins = 0

# Find lines in the level that define layers
for i in range(len(file_list)):
	if "<layer" in file_list[i]:
		for j in range(len(file_list[i])):

			# Check width
			if j < len(file_list[i]) - 3 and file_list[i][j:j + 5] == "width":
				width = ""
				k = j + 7
				while file_list[i][k] != "\"":
					width += file_list[i][k]
					k += 1
				width = int(width)

			# Check height
			if j < len(file_list[i]) - 4 and file_list[i][j:j + 6] == "height":
				height = ""
				k = j + 8
				while file_list[i][k] != "\"":
					height += file_list[i][k]
					k += 1

				height = int(height)
	
	if import_data == 1:
		if "</data" in file_list[i]:
			for j in range(len(level_data)):
				if level_data[j] in fd_values.object_list:
					for k in fd_values.object_list[level_data[j]]:
						object_used = copy.deepcopy(k)
						if not "X" in object_used:
							object_used["X"] = 0
						if not "Y" in object_used:
							object_used["Y"] = 0
						object_used["X"] += j % width * 30 + 15
						object_used["Y"] += (height - j // width) * 30 - 15
						if level_data[j] > 256:
							for l in object_offsets:
								if l["cx"] == j % width and l["cy"] == j // width:
									object_used["X"] += l["ox"] * 15 / 8
									object_used["Y"] -= l["oy"] * 15 / 8

						# Add 1 to coin count if object is coin
						if object_used["ID"] == 1329:
							coins += 1

						# Turn string properties into number properties
						object_to_add = {}
						for l in object_used:

							# Add X position times 10 if property is group
							if type(l) == str and getattr(gmdkit.mappings.obj_prop, l) in {51, 57} or l in {51, 57}:
								if type(object_used[l]) == list:
									for m in range(len(object_used[l])):
										object_used[l][m] += j % width * 10
								else:
									object_used[l] += j % width * 10

							if type(l) == int:
								object_to_add[l] = object_used[l]
							elif getattr(gmdkit.mappings.obj_prop, l) == 57:
								object_to_add[getattr(gmdkit.mappings.obj_prop, l)] = gmdkit.models.prop.list.IDList(object_used[l])
							else:
								object_to_add[getattr(gmdkit.mappings.obj_prop, l)] = object_used[l]
						object_list.append(gmdkit.Object(object_to_add))

			level_data = []
			import_data = 0
		else:
			level_data.append("")
			for j in file_list[i]:
				if j == ",":
					level_data[-1] = int(level_data[-1])
					level_data.append("")
				else:
					level_data[-1] += j
			if level_data[-1] == "":
				level_data.pop()
			else:
				level_data[-1] = int(level_data[-1])

	if "<data" in file_list[i]:
		import_data = 1

# Change the song of the level
if song in fd_values.song_list:
	if fd_values.song_list[song] < 0:
		level[gmdkit.mappings.lvl_prop.OFFICIAL_SONG_ID] = -fd_values.song_list[song] - 1
	else:
		if type(fd_values.song_list[song]) == dict:
			level[gmdkit.mappings.lvl_prop.SONG_ID] = fd_values.song_list[song]["id"]
			object_list.append(gmdkit.Object({gmdkit.mappings.obj_prop.ID: 1934, gmdkit.mappings.obj_prop.X: 0, gmdkit.mappings.obj_prop.Y: 15, gmdkit.mappings.obj_prop.trigger.song.SONG_ID: fd_values.song_list[song]["id"], gmdkit.mappings.obj_prop.trigger.song.START: fd_values.song_list[song]["offset"]}))
		else:
			level[gmdkit.mappings.lvl_prop.SONG_ID] = fd_values.song_list[song]

# Add gamemode and speed portals to the beginning
if gamemode > 0:
	object_list.append(gmdkit.Object({gmdkit.mappings.obj_prop.ID: fd_values.gamemode_list[gamemode], gmdkit.mappings.obj_prop.X: 0, gmdkit.mappings.obj_prop.Y: 15, gmdkit.mappings.obj_prop.trigger.gamemode_portal.FREE_MODE: True, gmdkit.mappings.obj_prop.HIDE: True}))
if speed > 0:
	object_list.append(gmdkit.Object({gmdkit.mappings.obj_prop.ID: fd_values.speed_list[speed], gmdkit.mappings.obj_prop.X: 0, gmdkit.mappings.obj_prop.Y: 15, gmdkit.mappings.obj_prop.HIDE: True}))

# Set other values
level[gmdkit.mappings.lvl_prop.COINS] = coins

# Add starting background and ground color
if bg_color != "":
	object_list.append(gmdkit.Object({gmdkit.mappings.obj_prop.ID: 899, gmdkit.mappings.obj_prop.X: -315, gmdkit.mappings.obj_prop.Y: 45, 7: fd_values.color_list[int(bg_color, 16) + 1][0], 8: fd_values.color_list[int(bg_color, 16) + 1][1], 9: fd_values.color_list[int(bg_color, 16) + 1][2], 10: 0, 23: gmdkit.mappings.color_id.BACKGROUND}))
if g_color != "":
	object_list.append(gmdkit.Object({gmdkit.mappings.obj_prop.ID: 899, gmdkit.mappings.obj_prop.X: -315, gmdkit.mappings.obj_prop.Y: 15, 7: fd_values.color_list[int(g_color, 16) + 1][0], 8: fd_values.color_list[int(g_color, 16) + 1][1], 9: fd_values.color_list[int(g_color, 16) + 1][2], 10: 0, 23: gmdkit.mappings.color_id.GROUND}))

# Disable parallax
if disable_parallax:
	object_list.append(gmdkit.Object({gmdkit.mappings.obj_prop.ID: 3029, gmdkit.mappings.obj_prop.X: -315, gmdkit.mappings.obj_prop.Y: 75, gmdkit.mappings.obj_prop.trigger.change_bg.BG_ID: 10}))

save_name = input("GMD file to save to: ")
if not save_name[-4:] == ".gmd":
	save_name += ".gmd"
level[gmdkit.mappings.lvl_prop.NAME] = save_name.replace(".gmd", "")
level.to_file(save_name)
print("Conversion successful.")
