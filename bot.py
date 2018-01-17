#!/usr/bin/env python3
# encoding: utf-8

import asyncio
import json
import traceback

import asyncpg
import discord
from discord.ext import commands


LOOP = asyncio.get_event_loop()


with open('config.json', 'r') as f:
	CONFIG = json.load(f)


async def get_db():
	credentials = {
		key: CONFIG['database'][key]
		for key in ('password', 'host')}
	credentials.update(dict(
		user='pint',
		database='pint',))
	db = await asyncpg.create_pool(**credentials)

	await db.execute(
		'CREATE TABLE IF NOT EXISTS permissions('
			'id bigint PRIMARY KEY,'
			'guild_id bigint NOT NULL,'
			'user_id bigint NOT NULL,'
			# if the channel is null,
			# the user has permissions to the whole guild
			'channel_id bigint)')

	return db


class Bot(commands.Bot):
	STARTUP_EXTENSIONS = (
		'pinner',
		'admin',
		'stats',)

	def __init__(self, **kwargs):
		self.db = LOOP.run_until_complete(get_db())
		self.config = CONFIG
		super().__init__(
			loop=LOOP,
			description=self.config['description'],
			command_prefix=commands.when_mentioned)

		for extension in self.STARTUP_EXTENSIONS:
			print('Loading extension', extension)
			try:
				self.load_extension('cogs.'+extension)
			except Exception as e:
				exc = '{}: {}'.format(type(e).__name__, e)
				print('Failed to load extension {}\n{}'.format(extension, exc))
				print(traceback.format_exc())

	async def run(self, token, *args, **kwargs):
		try:
			await self.start(token, *args, **kwargs)
		finally:
			await self.db.close()

	async def on_ready(self):
		message = 'Logged in as: %s' % self.user
		separator = '━' * len(message)
		print(separator, message, separator, sep='\n')


def main():
	bot = Bot()
	loop = asyncio.get_event_loop()
	loop.run_until_complete(bot.run(CONFIG['tokens']['discord']))


if __name__ == '__main__':
	main()
