#!/usr/bin/env python3
# encoding: utf-8

import asyncio
import json
import traceback

import asyncpg
import discord
from discord.ext import commands


with open('config.json', 'r') as f:
	CONFIG = json.load(f)


async def get_db():
	credentials = {
		'user': 'pint',
		'password': CONFIG['database']['password'],
		'database': 'pint',
		'host': '127.0.0.1'}
	db = await asyncpg.create_pool(**credentials)
	await db.execute('CREATE SCHEMA IF NOT EXISTS pint')
	await db.execute(
		'CREATE TABLE IF NOT EXISTS pint.permissions('
			'guild bigint NOT NULL,'
			'"user" bigint NOT NULL,'
			'channel bigint)')
	await db.execute(
		'CREATE TABLE IF NOT EXISTS pint.pins('
			'id bigint NOT NULL)')
	return db


class Bot(commands.Bot):
	STARTUP_EXTENSIONS = (
		'pinner',
		'admin',
		'stats',)

	def __init__(self, db, description=None, **kwargs):
		super().__init__(
			description=description,
			command_prefix=commands.when_mentioned)
		self.config = CONFIG
		self.db = db

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
			await self.conn.close()

	async def on_ready(self):
		message = 'Logged in as: %s' % self.user
		separator = '━' * len(message)
		print(separator, message, separator, sep='\n')


async def main():
	bot = Bot(await get_db(), CONFIG['description'])
	await bot.run(CONFIG['tokens']['discord'])


if __name__ == '__main__':
	asyncio.get_event_loop().run_until_complete(main())
