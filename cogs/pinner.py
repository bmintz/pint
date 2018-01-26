#!/usr/bin/env python3
# encoding: utf-8

import asyncio
from functools import wraps

import discord
from discord.ext import commands


def print_result(func):
	@wraps(func)
	async def wrapped(*args, **kwargs):
		result = await func(*args, **kwargs)
		print(func.__name__, 'returned', result)
		return result
	return wrapped


class Pinner:
	PUSHPIN_EMOJI = '📌'

	def __init__(self, bot):
		self.bot = bot
		self.db = self.bot.db # for convenience

	@print_result
	async def is_actionable_reaction(self, message, user, unpin):
		if not isinstance(user, discord.Member):
			return False

		return (
			#discord.utils.get(user.roles, name='Pin')
			#or user.permissions_in(message.channel).manage_messages
			await self.check_permissions(message, user))

	async def get_message(self, message_id, channel_id, user_id):
		channel = self.bot.get_channel(channel_id)

		if channel is None:
			raise discord.errors.NotFound('channel not found')
		elif isinstance(channel, discord.abc.PrivateChannel):
			raise NotImplementedError('DM and group chats Soon™')

		return await channel.get_message(message_id)

	async def on_raw_reaction(
			self,
			emoji,
			message_id,
			channel_id,
			user_id,
			unpin=False):

		if emoji.name != self.PUSHPIN_EMOJI:
			return

		message = await self.get_message(message_id, channel_id, user_id)
		pinned = await self.db.fetchrow("""
			SELECT *
			FROM pint.pins
			WHERE id = $1""",
			message_id)
		if pinned is not None:
			# it's already been pinned!
			await message.remove_reaction(emoji, user_id)
			return

		# cache miss
		await self.db.execute('INSERT INTO pint.pins VALUES($1)', user_id)
		user = message.guild.get_member(user_id)
		if user is not None:
			await self.handle_reaction(message, user, unpin)
		else:
			raise InvalidReactionEvent('user not in cache!')

	async def on_raw_reaction_add(self, *args):
		await self.on_raw_reaction(*args, unpin=False)

	async def handle_reaction(self, message, user, unpin=False):
		if await self.is_actionable_reaction(message, user, unpin):
			coro = message.unpin() if unpin else message.pin()
			await coro

	@commands.command()
	async def allow(
			self,
			context,
			user: discord.Member,
			channel: discord.TextChannel = None):
		...

	@print_result
	async def check_permissions(self, message, user):
		query = """
			SELECT 1
			FROM pint.permissions
			WHERE
				"user" = $1
				AND guild = $2
				AND (
					channel = $3
					OR channel IS NULL);"""
		return await self.db.fetchrow(
			query,
			user.id,
			message.guild.id,
			message.channel.id) is not None

	async def check_permissions_gay(self, guild_id, channel_id, user_id):
		class Empty():
			pass
		message, user, message.guild, message.channel = Empty(), Empty(), Empty(), Empty()
		message.guild.id = guild_id
		message.channel.id = channel_id
		user.id = user_id
		return await self.check_permissions(message, user)

	async def check_permissions_interactive(self):
		while True:
			try:
				args = map(int, input('Guild, channel, user: ').split())
				print(await self.check_permissions_gay(*args))
			except EOFError:
				return
			finally:
				# make sure there's always a newline if the user hits ^D, or not
				print()


class InvalidReactionEvent(Exception):
	"""Raised when some reaction is received that isn't valid.
	This could happen if the channel is not a GuildChannel.
	(Support for DM soon™)
	"""
	pass


def setup(bot):
	bot.add_cog(Pinner(bot))
