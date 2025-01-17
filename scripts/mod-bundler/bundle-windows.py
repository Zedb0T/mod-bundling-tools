import os
import shutil
import requests
import urllib.request
import zipfile

args = {
    "outputDir": os.getenv("outputDir"),
    "versionName": os.getenv("versionName"),
    "toolingVersion": os.getenv("toolingVersion"),
    "toolingBinaryDir": os.getenv("toolingBinaryDir"),
    "copyEntireBinaryDir": os.getenv("copyEntireBinaryDir"),
    "textureReplacementDir": os.getenv("textureReplacementDir"),
    "customLevelsDir": os.getenv("customLevelsDir"),
    "goalSourceDir": os.getenv("goalSourceDir"),
    "gameAssetsDir": os.getenv("gameAssetsDir"),
    "decompilerConfigDir": os.getenv("decompilerConfigDir"),
}

print(args)

# Create our output directory
if os.path.exists(os.path.join(args["outputDir"], "windows")):
    print(
        "Expected output directory already exists, clearing it - {}".format(
            os.path.join(args["outputDir"], "windows")
        )
    )
    os.rmdir(os.path.join(args["outputDir"], "windows"))

os.makedirs(os.path.join(args["outputDir"], "windows"), exist_ok=True)

# Download the Release
toolingVersion = args["toolingVersion"]
if toolingVersion == "latest":
    # Get the latest open-goal/jak-project release
    toolingVersion = requests.get(
        "https://api.github.com/repos/open-goal/jak-project/releases/latest"
    ).json()["tag_name"]
releaseAssetUrl = "https://github.com/open-goal/jak-project/releases/download/{}/opengoal-windows-{}.zip".format(
    toolingVersion, toolingVersion
)
urllib.request.urlretrieve(
    releaseAssetUrl, os.path.join(args["outputDir"], "windows", "release.zip")
)

# Extract it
with zipfile.ZipFile(
    os.path.join(args["outputDir"], "windows", "release.zip"), "r"
) as zip_ref:
    zip_ref.extractall(os.path.join(args["outputDir"], "windows"))
os.remove(os.path.join(args["outputDir"], "windows", "release.zip"))

if args["toolingBinaryDir"] != "":
    # User is specifying the binaries themselves, let's make sure they exist
    dir = args["toolingBinaryDir"]
    if (
        not os.path.exists(os.path.join(dir, "extractor.exe"))
        or not os.path.exists(os.path.join(dir, "goalc.exe"))
        or not os.path.exists(os.path.join(dir, "gk.exe"))
    ):
        print(
            "Tooling binaries not found, expecting extractor.exe, goalc.exe, and gk.exe"
        )
        exit(1)

    # Binaries are all there, let's replace 'em

    if args["copyEntireBinaryDir"] != "" and (args["copyEntireBinaryDir"] == "true" or args["copyEntireBinaryDir"]):
      # user has some DLLs or something, copy entire binary dir
      shutil.copytree(
        dir,
        os.path.join(args["outputDir"], "windows"),
        dirs_exist_ok=True
      )
    else:
      # copy the 3 key binaries
      shutil.copyfile(
          os.path.join(dir, "extractor.exe"),
          os.path.join(args["outputDir"], "windows", "extractor.exe"),
      )
      shutil.copyfile(
          os.path.join(dir, "goalc.exe"),
          os.path.join(args["outputDir"], "windows", "goalc.exe"),
      )
      shutil.copyfile(
          os.path.join(dir, "gk.exe"),
          os.path.join(args["outputDir"], "windows", "gk.exe")
      )

# Copy-in Mod Assets
textureReplacementDir = args["textureReplacementDir"]
if os.path.exists(textureReplacementDir):
    shutil.copytree(
        textureReplacementDir,
        os.path.join(args["outputDir"], "windows", "data", "texture_replacements"),
        dirs_exist_ok=True,
    )

customLevelsDir = args["customLevelsDir"]
if os.path.exists(customLevelsDir):
    shutil.copytree(
        customLevelsDir,
        os.path.join(args["outputDir"], "windows", "data", "custom_levels"),
        dirs_exist_ok=True,
    )

goalSourceDir = args["goalSourceDir"]
if not os.path.exists(goalSourceDir):
    print(
        "Goal source directory not found at {}, not much of a mod without that!".format(
            goalSourceDir
        )
    )
    exit(1)
shutil.copytree(
    goalSourceDir,
    os.path.join(args["outputDir"], "windows", "data", "goal_src"),
    dirs_exist_ok=True,
)

if args["gameAssetsDir"] != "":
  gameAssetsDir = args["gameAssetsDir"]
  if not os.path.exists(gameAssetsDir):
      print(
          "Game assets directory not found at {}!".format(
              gameAssetsDir
          )
      )
      exit(1)
  shutil.copytree(
      gameAssetsDir,
      os.path.join(args["outputDir"], "windows", "data", "game", "assets"),
      dirs_exist_ok=True,
  )

decompilerConfigDir = args["decompilerConfigDir"]
if os.path.exists(decompilerConfigDir):
    shutil.copytree(
        decompilerConfigDir,
        os.path.join(args["outputDir"], "windows", "data", "decompiler", "config"),
        dirs_exist_ok=True,
    )
else:
    print("Decompiler config directory not found at {}, skipping.".format(decompilerConfigDir))

# Rezip it up and prepare it for upload
shutil.make_archive(
    "windows-{}".format(args["versionName"]),
    "zip",
    os.path.join(args["outputDir"], "windows"),
)
os.makedirs(os.path.join(args["outputDir"], "dist"), exist_ok=True)
shutil.move(
    "windows-{}.zip".format(args["versionName"]),
    os.path.join(
        args["outputDir"], "dist", "windows-{}.zip".format(args["versionName"])
    ),
)

# Cleanup
shutil.rmtree(os.path.join(args["outputDir"], "windows"))
