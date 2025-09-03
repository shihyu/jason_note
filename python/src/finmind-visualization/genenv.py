import os
from configparser import ConfigParser


local_config = ConfigParser()
local_config.read("local.ini")
if os.environ.get("VERSION", ""):
    section = local_config[os.environ.get("VERSION", "")]
else:
    section = local_config["DEFAULT"]

env_content = ""
for sec in section:
    env_content += "{}={}\n".format(sec.upper(), section[sec])

with open(".env", "w", encoding="utf8") as env:
    env.write(env_content)
