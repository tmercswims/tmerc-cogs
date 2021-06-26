import logging
import random
import shutil

from redbot.core import commands, data_manager

__author__ = "tmerc"

log = logging.getLogger("red.tmerc.randimage")


class RandImage(commands.Cog):
    """Create categories and add images to the categories, then fetch a random one from a category."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__base_dir = data_manager.cog_data_path(self)
