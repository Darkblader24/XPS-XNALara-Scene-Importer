<h1 align="center">XPS/XNALara Scene Importer</h1>

This Blender plugin allows XPS users to easily import their .scene files into Blender, for immediate high-quality real-time rendering in the Eevee engine. 

This tool works just the same as XPS’s scene importer, and brings your entire scene into Blender for convenient high-quality rendering, exactly as you created it. It retrieves the correct .meshes, applies the right poses and transformations, and builds new adjustable lamps from XPS’s lights - no need to manually redo any of your existing work.

<p align="center">
  <img height="500" src="https://i.imgur.com/xQDguPZ.png">
</p>

---

### [Download](https://github.com/Darkblader24/XPS-XNALara-Scene-Importer/archive/refs/heads/master.zip)

### Features
- Import Models, Poses, Lights, Camera and Ground

### Requirements
- Blender 3.3 or above
- For model import: [XNALaraMesh Plugin](https://github.com/johnzero7/XNALaraMesh)

### Installation
- [Download](https://github.com/Darkblader24/XPS-XNALara-Scene-Importer/archive/refs/heads/master.zip) the latest release
- Install the downloaded zip file via the Blender User Preferences

### Usage
- In the 3D View, open the panel (N) and select the XPS tab
- Optionally select your XPS installation folder and your XPS asset folder
  - These folders will be searched for any missing assets, so make sure they are there
- Click the "Import Scene" button and select your .scene file
- Watch the magic happen

---

## Details

(readme written by [judgemk](https://www.deviantart.com/judgemk) on dA. I commissioned this because of how badly I needed it, so now you all get to use it, too.)

XPS is a fantastic and simple tool for posing and scene construction, and its convenient sliders and color picker make it possible to quickly build vivid, colorful light setups. However, for 3D artists looking to improve their realism, it has some shortcomings, especially the lack of cast shadows. Blender’s Eevee engine is extremely capable and works in real time, just the same as XPS, and it renders quickly and allows for multiple saved camera angles, strongly improving upon XPS’s existing functions. 
XPS has often been treated as a tool in a larger rendering workflow, where you import your character and create your pose, then export as .obj to render in a different program. But what if you want to adjust your pose after export? What if you like the light setup you already made in XPS? Too bad, so sad - until now! With this plugin, you get the best of both worlds: you can upgrade to Blender 3.3 as your final renderer, and still pose models and build new scenes in XPS, or improve your old XPS scenes with the literal click of a button.

### Import Options: 
Within the Import XPS selection window, there are several checkbox options:
- Import Models: Exactly what it sounds like. This function tracks down every model saved in your scene (generic_item.mesh, xps.xps, or generic_item.mesh.ascii) and imports them to Blender, at the correct coordinates, and with the correct pose loaded. 
- Import Lights: The primary reason that this plugin was built, and THE function that you will find nowhere else. The plugin takes the data from XPS’s saved .scene files and constructs lamps that provide very similar light. 
- Import Camera: Recreates the camera saved from your .scene file, with the same window dimensions, camera placement, field of view, and other parameters. 
- Import Floor: If you’re feeling nostalgic for that gray tile, this will add in the XPS Floor we all know and love. It’s set to Shadow mode: None by default, so it won’t block any light sources that you’ve placed below the ground.
- Exclude Hidden Models: I very strongly recommend keeping this option turned on. However, it can be deactivated if you really need to. If it’s on, it will load your scene exactly as XPS shows it. If it’s off, it will load every single model you’ve saved to the scene, including hidden ones you might have forgotten about, which will increase your load time.

### Lights: 
The importer performs some wizardry to convert XPS’s light parameters (horizontal and vertical rotation angle, strength, and color) into three Blender point lamps that match your original scene lights extremely closely. For a more easy and direct UI for lamp control, install the Gaffer addon, linked at the end of the readme.
- The plugin converts Angle Horizontal and Angle Vertical to X/Y/Z location information for each lamp. As such, you won’t see the same exact horizontal/vertical angle numbers in Blender as you did in XPS. However, all 3 lamps are parented to central Empty controls, so you can control the rotation and adjust them however you like.
- Lamps come with the Contact Shadows turned on by default (ray-tracing), which makes models look even more realistic. If your scene seems too dark or heavily shadowed, Contact Shadows can be easily turned off on one or more lamps.
- The Size number value on the lamps affects how far the light spreads, but it also makes the light weaker if you increase the number. The plugin imports them with a default size of 2. Turn them down to 1 for a more intense, closer light. 
- Unlike XPS (but like real life), the lamps do have distance-based falloff, so you may see a few differences based on that, especially the ground area being darker. To overcome this, I’ve found it useful to make a small extra point lamp or two with very low strength and place them around the character’s waist and feet, with the following settings: Power 70mW (or similarly low), Diffuse: 0.5; Specular: 0.0; Size: 0.5m; Custom Distance; turn down the Distance to 0.4m.
- Specular Factor on each lamp is similar to the “bump specular gloss” controller in XPS. By default it’s 1. If your model looks too shiny, turn the numbers down. If it’s too matte, turn them up. 
- For reasons unknown, Blender displays the lamp color preview as white, unless its saturation is maxed out at 1, even if you have a color tint. Never fear; the plugin will import your colors correctly. Use the R/G/B number values to manually adjust color tone. I recommend adding or subtracting in values of 20, since the values are 1-255. 

### Camera:
Use Blender’s View > Viewpoint > Camera to instantly see your scene exactly as it was saved in XPS.
- By default, it is set to render your images at 200% resolution, similar to the XPS save-image dialog box. This can be changed in Scene > Format > Resolution %. 
- For easily setting up a scene with multiple camera angles, select your camera, use the Insert Keyframe function on the camera (I, Loc/Rot/Scale), then use your arrow keys to step forward 1 frame, use "Lock Camera to View", press I to save the next angle, etc. If you worked hard on a 3D model and want to show it off from multiple angles, this is the way to go! Set your cameras once with keyframes, and you’ll never have to repeat your work. 

### Optimization: 
To make your renders look as good as possible, adjust your .blend file to the following settings, which increase brightness and contrast and enhance your lighting.
- World panel > Surface > Strength: 1.3
- Scene panel > Color Management > Look: Very High Contrast
- Scene panel > Color Management > Exposure: -0.5
- Scene panel > Color Management > Gamma: 1.5 

### Saving:
Blender renders your image with a press of a button (F12). To make Blender automatically save those renders to a folder of your choice, follow this tutorial. https://www.youtube.com/watch?v=HFyXAc5xWCo 

### Posing:
I’m including a note about easy XPS posing here, since a surprising number of XPS users I’ve met don’t know about it. I prefer XPS posing to Blender posing because of its keyboard shortcuts. Hold down the Q, W, or E keys and click-and-drag to rotate along the X, Y, and Z axes (hold down two keys at once to rotate along 2 axes together.) Hold down Shift to do the same thing but for Move instead of Rotate. For more tips, read the Help menu in XPS, right below the red X button to close the control window.

### Materials: 
This plugin is built on the XPS Model Importer by johnzero7: https://github.com/johnzero7/XNALaraMesh It functions exactly the same way. However, there are some small changes and improvements to how it handles materials, and some tips I’d recommend. (Note: I mostly use render groups 24, 25, and 27. I already know RG 40 doesn’t look great in Blender, so I’d stick with the tried and true classics and use the XPS material editor if your import isn’t looking right.)
- The default XPS importer plugin has an issue with flipping the normals (XPS’s normals configuration is +X, -Y, +Z.), causing them to display upside down. This plugin fixes it by default; nothing to worry about. However, to correct that issue on models imported with the original johnzero plugin, open the Shader Editor, then enter the XPS Shader node group (click the small button in the upper right hand corner, Tab to go back). Adjust the first Invert Channel node's G slider to 1, and you will see the normals return to normal. (lol)
- This plugin also contains built-in improvements to how Blender 3.3 imports reflective and shiny materials (RG 27), especially hair. I’m including additional adjustment instructions below in case you need to tweak the materials even more.
- To reduce glossiness/reflectivity, lower the Emission Strength number value in the Materials panel. I find that for overly shiny hair, changing 0.1 to 0.01 looks good. For translucent materials, I’d also recommend changing Blend mode to Alpha Blend.
- To reduce specularity/shine, make a new copy of the XPS Shader node (click the number, next to the little shield icon.) Then, enter that node group (upper right hand corner button, Tab to go back), and in the Principled BSDF node, lower the Specular number value (right below Metallic). Be careful if you’re only fixing one item; if you don’t make a new copy of the XPS Shader node, that specularity value change will affect every material.
- To avoid translucent materials casting a shadow when they’re not supposed to (such as smoke or shadow effects) change the Blend mode to Alpha Blend and the Shadow mode to None. 
- This is a very specific case, but I needed it, so you might too. I use a very thin contact lens-style mesh to add reflective shine to eye irises (a RG 27 material). To make it work correctly, I made another copy of the XPS Shader node, then plugged in the Reflect texture to the Environment slot instead of Emission. Then I set its Emission strength to 0.1 and its Alpha strength to 0.001, and changed its Blend mode to Alpha Blend instead of Hashed. For a glasses lens material, I fixed it exactly the same way as the above, but with an Emission value of .001. Not sure how much the emission number ultimately mattered, but it worked. If you have problems with those types of materials, I’d start here for a fix.

### Sampling:
Blender’s “sampling” parameters (under Scene) are by default Render > 64 and Viewport > 16. These mostly affect how smooth your shadows are. To make your renders save faster, set Render to 32. If your viewport is lagging (though it shouldn’t), reduce that value to 8; conversely, if you want your viewport’s shadows to look more realistic and final, set the value to 32. 

### Optional Items:
Like all other Blender XPS import tools, Scene Importer will show every item on a character by default. If they have hidden-by-default optional items, such as weapons or accessories, simply move them to another collection and hide that all at once. Refer to the Addons section for info on Collection Manager, an add-on that makes this easier.
- For character showcase render sets, where you may want to display your model both with and without optional items, I suggest moving their optional items to an extra collection/layer of their own. Use the Outliner menu’s visibility/rendering toggle buttons (the eye and the camera) to shoot your renders without those items.

### Known Issues:
- Currently only .scene files version 1.21 or above are supported. If you have older version files, please open an issue with a download link to them.
- There are no known problems with XPS Scene Importer’s functionality, but we don’t have a way to replicate the Vignette postprocessing parameter. However, see above (Optimization) for tips on recreating your preferred brightness/contrast looks.

### Addons: 
- The Collection Manager (built into Blender) is essential. This mostly restores Blender 2.79’s Layers panel, which lets you see where your items are within the .blend file, and hide or show groups and items. 
- The add-on Gaffer makes Blender’s lighting setups much easier to use, especially in connection with XPS Importer. It is free and the free version has no limits, but I’m linking the Blender Market version too anyway, in case you want to support the dev.
  - https://github.com/gregzaal/Gaffer (free trial)
  - https://blendermarket.com/products/gaffer-light-manager ($20)
- I also recommend activating the Stored Views addon (built into Blender), which works similarly to the XPS camera lock and gives you infinite camera lock options. This is much faster than XPS, which only allows for one camera angle lock, and you can create a camera from your view at any time. This can be found in the Add-ons section of User Prefs. 
- The Photographer 4 addon is paid ($16) but allows you much more control over the final postprocessing parameters and the look and feel of your setup, especially color/light balance, brightness and contrast, etc. 
  - https://chafouin.gumroad.com/l/HPrCY 

### Shout-outs:
- Massive thanks to Hotox/Darkblader24, the highly talented coder who made and is posting this plugin (also a developer of the Cats plugin). Thank you for accepting the commission for it, and for being willing to give this crazy idea a chance. It’s still unbelievable to me that this tool actually exists now. It’s already made a tremendous difference in my rendering workflow. Every 3D model now looks exactly as good as it’s supposed to.
- To my fellow XPS users, I hope that this will remove any obstacles in your path for making the switch from our favorite little model viewer program to a high-powered top-of-the-line render engine. No need to give up XPS at all, either; the plugin is an incredibly convenient bridge between the posing/lighting tool and the final image output.
- Additional special thanks to ZCochrane on deviantArt, the author of GLLara (the Mac equivalent of XNALara/XPS) for assistance and guidance on how to make this plugin work, as well as linking us the source code! Wouldn’t have been possible without you.
- And a major thanks to Dusan Pavlicek and XNAAraL for having created and maintained the XPS/XNALara program itself for all these years. We all owe you one.

### Enjoy!
