# pint
A Discord pin bot for admins who don't want to grant "manage messages" to people

## Installation
<!--Inspired by <a href="https://github.com/Rapptz/RoboDanny">R. Danny's</a> config-->

If you don't want to do all this, you can just invite the bot here:
<https://discordapp.com/oauth2/authorize?client_id=400783180732563456&scope=bot&permissions=27712>

1. **Install Python 3.5 or higher**

This is required to actually run the bot.

2. **Set up venv**

`python3.5 -m venv venv`

3. **Install dependencies**

`pip3 install -U -r requirements.txt`

4. **Create the database in PostgreSQL**

Type the following in the `psql` tool:

```sql
CREATE ROLE pint WITH LOGIN PASSWORD 'yourpw';
CREATE DATABASE pint OWNER pint;
```

5. **Setup configuration**

Copy `config.example.json` to `config.json` and edit it accordingly.
The `postgresql` key should be set to a URL like so:
`postgresql://user:password@host/database`

6. **Configuration of database**

To configure the PostgreSQL database for use by the bot, run
`python3.5 dbinit.py`


## License

    Pint lets Discord admins grant "pin message" permissions without granting "manage messages"
    Copyright © 2018 Benjamin Mintz <bmintz@protonmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
