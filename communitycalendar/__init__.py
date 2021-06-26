from redbot.core.bot import Red

from .communitycalendar import CommunityCalendar


def setup(bot: Red):
    bot.add_cog(CommunityCalendar(bot))
