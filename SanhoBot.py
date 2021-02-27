# ------------------------------
# Module Setup
# ------------------------------

import bs4
import discord
from discord.ext import commands, tasks
from inspect import Parameter
import math
import os
import requests
from SanhoDB import SanhoDB
import tempfile
from urllib import parse


# ------------------------------
# Variable Setup
# ------------------------------

bot = commands.Bot(
    command_prefix="$",
    help_command=None,
    intents=discord.Intents.all()
)

presence_list_current_presence = 0


# ------------------------------
# Task Manager
# ------------------------------

@tasks.loop(
    seconds=0.1
)
async def user_exp_update():
    for user in os.listdir("./Users/"):
        if user[:-5].endswith("."):
            user_id = int(user[:-6])
        else:
            user_id = int(user[:-5])

        data = SanhoDB.load_user_data(user_id)

        if user.endswith(".json") and data["exp"] >= 10 + (data["level"] - 1) * 5 - math.floor(data["level"] / 10):
            while True:
                if data["level"] >= 100:
                    break
                data["exp"] -= 10 + (data["level"] - 1) * 5 - math.floor(data["level"] / 10)
                data["level"] += 1
                if data["exp"] < 10 + (data["level"] - 1) * 5 - math.floor(data["level"] / 10):
                    break

            if data["level"] >= 100:
                max_level_reached_message = "\n**최대 레벨을 달성했습니다! **"
            else:
                max_level_reached_message = ""

            level_up_embed = discord.Embed(
                title=f":arrow_up: 레벨이 올랐습니다! ",
                description=f"""• {bot.get_user(user_id).name}#{bot.get_user(user_id).discriminator}님의 레벨이 Lv.{data["level"]}(으)로 상승하였습니다! {max_level_reached_message}"""
            )

            level_up_embed.set_footer(
                text=f"""• Triggered by {bot.get_user(user_id).name}#{bot.get_user(user_id).discriminator}"""
            )
            await bot.get_guild(812235738040107069).get_channel(812275042989768754).send(
                embed=level_up_embed
            )

            SanhoDB.dump_user_data(
                obj=data,
                user_id=user_id
            )


@tasks.loop(
    seconds=10
)
async def presence_auto_change():
    global presence_list_current_presence

    presence_list = [
        f"• Bot Author : {(await bot.application_info()).owner.name}#{(await bot.application_info()).owner.discriminator}",
        f"{bot.command_prefix}help | Alpha Test"
    ]

    if presence_list_current_presence < len(presence_list) - 1:
        presence_list_current_presence += 1
    else:
        presence_list_current_presence = 0

    await bot.change_presence(
        activity=discord.Game(
            name=presence_list[presence_list_current_presence]
        ),
        status=discord.Status.dnd
    )


# ------------------------------
# Start Tasks Manager
# ------------------------------

@bot.event
async def on_ready():
    print("[System] Starting Bot! ")
    await bot.change_presence(
        activity=discord.Game(f"{bot.command_prefix}help | Alpha Test"),
        status=discord.Status.dnd
    )
    user_exp_update.start()
    presence_auto_change.start()


# ------------------------------
# Message Level Manager
# ------------------------------

@bot.event
async def on_message(
    message: discord.Message
):
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(
            message=message
        )
    elif not message.author.bot:
        if not message.channel.type == discord.ChannelType.private:
            if message.guild.name != "서버니" or message.guild.name != "SanhoBot Workshop":
                return

            data = SanhoDB.load_user_data(message.author.id)
            data["exp"] += 1

            SanhoDB.dump_user_data(
                obj=data,
                user_id=message.author.id
            )


# ------------------------------
# Member Join Message
# ------------------------------

@bot.event
async def on_member_join(
    member: discord.Member
):
    if member.guild.id == 812235738040107069:
        member_join_embed = discord.Embed(
            title=f":white_check_mark: {member.name}#{member.discriminator}님이 입장하셨습니다! ",
            description=f"• {member.name}#{member.discriminator}님, **{member.guild.name}**에 오신 것을 환영합니다. "
        )

        member_join_embed.set_footer(
            text=f"• Triggered by {member.name}#{member.discriminator}"
        )
        await member.guild.get_channel(814466249501310980).send(
            embed=member_join_embed
        )


# ------------------------------
# Main Commands Source Code
# ------------------------------

@bot.command(
    name="help",
    aliases=["도움", "도움말"]
)
async def _help(
    ctx: commands.Context
):
    help_embed = discord.Embed(
        title=":clipboard: 저희의 명령어 목록입니다! ",
        description=f"""• 명령어 접두어 : `{bot.command_prefix}`

• `<requires>` - 필수 항목
• `[non-requires]` - 선택적 항목
• `argA | argB` - 다중 항목 선택"""
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}help**",
        value=f"""- 명령어 목록을 표시합니다. 
- (Aliases : {bot.command_prefix}도움, {bot.command_prefix}도움말)""",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}ping**",
        value=f"""- 봇의 디스코드 통신 상태를 표시합니다. 
- (Aliases : {bot.command_prefix}핑)""",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}pf [<User 유저>]**",
        value=f"""- 해당 유저 또는 자신의 프로필을 표시합니다. 
- (Aliases : {bot.command_prefix}profile, {bot.command_prefix}uinfo, {bot.command_prefix}user, {bot.command_prefix}유저, {bot.command_prefix}유저정보)""",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}rinfo <Role 역할>**",
        value=f"""- 해당 역할의 정보를 표시합니다. 
- (Aliases : {bot.command_prefix}role, {bot.command_prefix}역할, {bot.command_prefix}역할정보)""",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}server**",
        value=f"""- 서버의 정보를 표시합니다. 
- (Aliases : {bot.command_prefix}sinfo, {bot.command_prefix}서버, {bot.command_prefix}서버정보)"""
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}bag [<User 유저>]**",
        value=f"""- 해당 유저 또는 자신의 소지품 정보를 표시합니다. 
- (Aliases : {bot.command_prefix}inv, {bot.command_prefix}inventory, {bot.command_prefix}가방, {bot.command_prefix}소지품)""",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}exp [<User 유저>]**",
        value=f"""- 해당 유저 또는 자신의 레벨 정보를 표시합니다. 
- (Aliases : {bot.command_prefix}level, {bot.command_prefix}linfo, {bot.command_prefix}경험치, {bot.command_prefix}레벨, {bot.command_prefix}레벨정보)""",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}weather <region 지역명>**",
        value=f"""- 해당 지역의 날씨를 표시합니다. 
- (Aliases : {bot.command_prefix}날씨)""",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}covid-19**",
        value=f"""- 코로나19 현황을 표시합니다. 
- (Aliases : {bot.command_prefix}covid19, {bot.command_prefix}코로나, {bot.command_prefix}코로나19)""",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}owner**",
        value=f"""- 봇 개발자 (이하 소유자)를 표시합니다. 
- (Aliases : {bot.command_prefix}소유자, {bot.command_prefix}제작자)"""
    )

    help_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=help_embed
    )


@bot.command(
    name="ping",
    aliases=["핑"]
)
async def _ping(
    ctx: commands.Context
):
    ping_embed = discord.Embed(
        title=":signal_strength: 현재 디스코드 통신 상태입니다. ",
        description=f"• Discord API 지연 시간 : **{round(bot.latency * 1000)} ms**"
    )

    ping_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=ping_embed
    )


@bot.command(
    name="pf",
    aliases=["profile", "uinfo", "user"]
)
async def _profile(
    ctx: commands.Context,
    user: discord.User = None
):
    if not user:
        user = ctx.author

    if user.bot:
        await ctx.send("봇의 데이터를 수정/확인할 수 없습니다. ")
        return

    if user.status != discord.Status.offline:
        is_online = "온라인"
    else:
        is_online = "오프라인"

    profile_embed = discord.Embed(
        title=f":information_source: {user.name}#{user.discriminator}님의 프로필"
    )
    profile_embed.add_field(
        name="**• 사용자 정보 : **",
        value=f"""- 사용자 태그 : **{user.name}#{user.discriminator}**
- 온라인 여부 : **{is_online}**"""
    )
    if ctx.channel.type != discord.ChannelType.private:
        if user.top_role == ctx.guild.default_role:
            top_role = "-"
        else:
            top_role = user.top_role.name

        if not user.nick:
            nickname = "-"
        else:
            nickname = user.nick

        if user in user.guild.premium_subscribers:
            is_booster = "(부스트함. )"
        else:
            is_booster = "(부스트 안함. )"

        profile_embed.add_field(
            name="**• 멤버 정보 : **",
            value=f"""- 서버에서 사용하는 별명 : **{nickname}**
- 최상위 역할 : **{top_role}**
- 부스터 여부 : **{is_booster}**""",
            inline=False
        )
    profile_embed.add_field(
        name="**• 디버깅 정보 : **",
        value=f"- 사용자 ID : **{user.id}**",
        inline=False
    )

    profile_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=profile_embed
    )


@bot.command(
    name="rinfo",
    aliases=["role", "역할", "역할정보"]
)
async def _role_info(
    ctx: commands.Context,
    role: discord.Role
):
    role_member_list = ""
    full_role_member_list = ""
    another_member_count = 0

    role_member_count = 0
    role_member_in_online_count = 0
    role_member_bot_count = 0

    for role_member in role.members:
        role_member_count += 1
        if role_member.bot:
            role_member_bot_count += 1
        if role_member.status != discord.Status.offline:
            role_member_in_online_count += 1

        full_role_member_list += f"- {role_member.name}#{role_member.discriminator}\n"
        if len(full_role_member_list) <= 512:
            role_member_list += f"- {role_member.name}#{role_member.discriminator}\n"
        else:
            another_member_count += 1

    if len(full_role_member_list) > 512:
        role_member_list += f"...그리고 {another_member_count}명 (자세한 건 첨부 파일 확인)"
    elif not role_member_list:
        role_member_list = "- (해당 역할에 소속된 멤버가 없습니다. )"
    else:
        role_member_list = role_member_list[:-1]

    role_info_embed = discord.Embed(
        title=f":placard: 역할 {role.name}의 정보입니다. "
    )
    role_info_embed.add_field(
        name="**• 소속 멤버 리스트 : **",
        value=role_member_list,
        inline=False
    )
    role_info_embed.add_field(
        name="**• 소속 멤버 카운트 : **",
        value=f"""- 총 멤버 : **{role_member_count}명**
- 온라인 : **{role_member_in_online_count}명**
- Discord 봇 : **{role_member_bot_count}명**""",
        inline=False
    )
    role_info_embed.add_field(
        name="**• 디버깅 정보 : **",
        value=f"- 역할 ID : **{role.id}**",
        inline=False
    )

    role_info_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    if len(full_role_member_list) > 512:
        full_role_member_list_tempfile_path = tempfile.mktemp(
            dir="./Temp"
        )
        with open(
            file=full_role_member_list_tempfile_path,
            mode="w",
            encoding="utf-8"
        ) as full_role_member_list_tempfile:
            full_role_member_list_tempfile.write(full_role_member_list)

        await ctx.send(
            embed=role_info_embed,
            file=discord.File(
                fp=full_role_member_list_tempfile_path,
                filename="FULL_ROLE_MEMBER_LIST.txt"
            )
        )

        os.remove(
            path=full_role_member_list_tempfile_path
        )
    else:
        await ctx.send(
            embed=role_info_embed
        )


@bot.command(
    name="server",
    aliases=["sinfo", "서버", "서버정보"]
)
async def _server_info(
    ctx: commands.Context
):
    if ctx.channel.type == discord.ChannelType.private:
        await on_command_error(
            ctx=ctx,
            error=commands.NoPrivateMessage(
                message=ctx.message
            )
        )
        return

    member_list = ""
    full_member_list = ""
    another_member_count = 0

    member_count = 0
    member_in_online_count = 0
    member_bot_count = 0

    for member in ctx.guild.members:
        member_count += 1
        if member.bot:
            member_bot_count += 1
        if member.status != discord.Status.offline:
            member_in_online_count += 1

        full_member_list += f"- {member.name}#{member.discriminator}\n"
        if len(full_member_list) <= 512:
            member_list += f"- {member.name}#{member.discriminator}\n"
        else:
            another_member_count += 1

    if len(full_member_list) > 512:
        member_list += f"...그리고 {another_member_count}명 (자세한 건 첨부 파일 확인)"
    elif not member_list:
        member_list = "- (서버가 비어있습니다. )"
    else:
        member_list = member_list[:-1]

    emoji_list = ""
    full_emoji_list = ""
    another_emoji_count = 0

    emoji_count = 0

    for emoji in ctx.guild.emojis:
        emoji_count += 1

        full_emoji_list += f"- {emoji}\n"
        if len(full_emoji_list) <= 512:
            emoji_list += f"- {emoji}\n"
        else:
            another_emoji_count += 1

    if len(full_emoji_list) > 512:
        emoji_list += f"...그리고 {another_emoji_count}개 (자세한 건 첨부 파일 확인)"
    elif not emoji_list:
        emoji_list = "- (서버에 이모티콘이 없습니다. )"
    else:
        emoji_list = emoji_list[:-1]

    if ctx.guild.premium_subscription_count == 0:
        boost_count = "-"
    else:
        boost_count = f"{ctx.guild.premium_subscription_count}회"

    if ctx.guild.premium_tier == 0:
        boost_level = "-"
    else:
        boost_level = f"{ctx.guild.premium_tier} 레벨"

    server_info_embed = discord.Embed(
        title=f":information_source: 서버 {ctx.guild.name}의 정보입니다. "
    )
    server_info_embed.add_field(
        name="• 서버 멤버 리스트 : ",
        value=member_list,
        inline=False
    )
    server_info_embed.add_field(
        name="• 서버 멤버 카운트 : ",
        value=f"""- 총 멤버 : **{member_count}명**
- 온라인 : **{member_in_online_count}명**
- Discord 봇 : **{member_bot_count}명**""",
        inline=False
    )
    server_info_embed.add_field(
        name="• 서버 이모티콘 리스트 : ",
        value=f"{emoji_list}",
        inline=False
    )
    server_info_embed.add_field(
        name="• 서버 이모티콘 카운트 : ",
        value=f"• 총 이모티콘 : **{emoji_count}개**",
        inline=False
    )
    server_info_embed.add_field(
        name="• 부스트 정보 : ",
        value=f"""- 부스트 레벨 : **{boost_level}**
- 부스트 횟수 : **{boost_count}**""",
        inline=False
    )
    server_info_embed.add_field(
        name="• 디버깅 정보 : ",
        value=f"• 서버 ID : **{ctx.guild.id}**",
        inline=False
    )

    server_info_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    server_info_embed_files = []

    full_member_list_tempfile_path = ""
    if len(full_member_list) > 512:
        full_member_list_tempfile_path = tempfile.mktemp(
            dir="./Temp"
        )
        with open(
            file=full_member_list_tempfile_path,
            mode="w",
            encoding="utf-8"
        ) as full_member_list_tempfile:
            full_member_list_tempfile.write(full_member_list)

        server_info_embed_files.append(discord.File(
            fp=full_member_list_tempfile_path,
            filename="FULL_MEMBER_LIST.txt"
        ))

    full_emoji_list_tempfile_path = ""
    if len(full_emoji_list) > 512:
        full_emoji_list_tempfile_path = tempfile.mktemp(
            dir="./Temp"
        )
        with open(
            file=full_emoji_list_tempfile_path,
            mode="w",
            encoding="utf-8"
        ) as full_emoji_list_tempfile:
            full_emoji_list_tempfile.write(full_emoji_list)

        server_info_embed_files.append(discord.File(
            fp=full_emoji_list_tempfile_path,
            filename="FULL_EMOJI_LIST.txt"
        ))

    await ctx.send(
        embed=server_info_embed,
        files=server_info_embed_files
    )

    if len(full_member_list) > 512:
        os.remove(full_member_list_tempfile_path)
    if len(full_emoji_list) > 512:
        os.remove(full_emoji_list_tempfile_path)


@bot.command(
    name="bag",
    aliases=["inv", "inventory", "가방", "소지품"]
)
async def _bag(
    ctx: commands.Context,
    user: discord.User = None
):
    if not user:
        user = ctx.author
    elif user.bot:
        await ctx.send("봇의 데이터를 수정/확인할 수 없습니다. ")
        return

    data = SanhoDB.load_user_data(user.id)

    item_list = ""
    for item_stack in data["bag"]["item_list"]:
        if item_stack["item_count"] > 1:
            item_list += f"""- {item_stack["item_type"]} × {item_stack["item_count"]}\n"""
        elif not item_stack["item_count"] == 0:
            item_list += f"""- {item_stack["item_type"]}\n"""
    if item_list[-1] == "\n":
        item_list = item_list[:-1]

    bag_embed = discord.Embed(
        title=f":scroll: {user.name}#{user.discriminator}님의 소지품 목록",
        description=f"""• 보유 Dott : **{data["bag"]["money"]} 도트**"""
    )
    bag_embed.add_field(
        name="**• 아이템 목록 : **",
        value=item_list,
        inline=False
    )

    bag_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=bag_embed
    )


@bot.command(
    name="exp",
    aliases=["level", "linfo", "경험치", "레벨", "레벨정보"]
)
async def _level_info(
    ctx: commands.Context,
    user: discord.User = None
):
    if not user:
        user = ctx.author

    data = SanhoDB.load_user_data(user.id)
    exp_total = data["exp"]
    for exp_total_level_index in range(1, data["level"]):
        exp_total += 10 + (exp_total_level_index - 1) * 5

    if math.floor(data["exp"] / (10 + (data["level"] - 1) * 5 - math.floor(data["level"] / 10)) * 100 * 100) / 100 > 100:
        exp_percent = 100
    else:
        exp_percent = math.floor(data["exp"] / (10 + (data["level"] - 1) * 5 - math.floor(data["level"] / 10)) * 100 * 100) / 100

    level_info_embed = discord.Embed(
        title=f":star: {user.name}#{user.discriminator}님의 레벨 정보",
        description=f"""• 현재 레벨 : **Lv.{data["level"]}**
• 현재 경험치 : **{data["exp"]} / {10 + (data["level"] - 1) * 5} ({exp_percent}%)**
• 경험치 총합 : **{exp_total}**"""
    )

    level_info_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=level_info_embed
    )


@bot.command(
    name="mine",
    aliases=["채광"]
)
async def _mine(
    ctx: discord.ext.commands.Context
):
    SanhoDB.add_user_item(
        item={
            "item_type": "돌의 파편 Stone Shard",
            "item_count": 1
        },
        user_id=ctx.author.id
    )

    mine_embed = discord.Embed(
        title=":pick: 채광에 성공했습니다! ",
        description="• 채광 결과물 : **돌의 파편 Stone Shard**"
    )

    mine_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=mine_embed
    )


@bot.command(
    name="weather",
    aliases=["날씨"]
)
async def weather_info_command(
    ctx: commands.Context,
    *region: str
):
    if not region:
        await on_command_error(
            ctx=ctx,
            error=commands.MissingRequiredArgument(Parameter(
                name="region",
                kind=Parameter.POSITIONAL_OR_KEYWORD
            ))
        )
        return
    region = " ".join(region)
    soup = bs4.BeautifulSoup(requests.get(f"""http://search.naver.com/search.naver?query={parse.quote(f"{region} 날씨")}""").text, "html.parser")

    if not soup.find(
        name="h2",
        class_="api_title"
    ):
        await ctx.send("해당 지역을 찾을 수 없습니다...")
        return
    elif soup.find(
        name="h2",
        class_="api_title"
    ).get_text() != "날씨정보":
        if not soup.find(
            name="h2",
            class_="api_title"
        ).get_text().endswith("날씨정보"):
            await ctx.send("해당 지역을 찾을 수 없습니다...")
        else:
            await ctx.send("해외 날씨 정보는 로드할 수 없습니다 :(")

        return

    if not soup.find(
        name="span",
        class_="btn_select",
        role="button"
    ):
        region = soup.find(
            name="a",
            class_="btn_select _selectLayerTrigger",
            role="button"
        ).findAll("em")[0].get_text()
    else:
        region = soup.find(
            name="span",
            class_="btn_select",
            role="button"
        ).findAll("em")[0].get_text()

    temperature = soup.find(
        name="span",
        class_="todaytemp"
    ).get_text()
    if soup.find(
        name="p",
        class_="cast_txt"
    ).get_text().split("˚")[-1].endswith("낮아요"):
        temperature_difference_from_yesterday = f"""{soup.find(
            name="p",
            class_="cast_txt"
        ).get_text().split("˚")[0].split(" ")[-1]}℃ 낮음. """
    else:
        temperature_difference_from_yesterday = f"""{soup.find(
            name="p",
            class_="cast_txt"
        ).get_text().split("˚")[0].split(" ")[-1]}℃ 높음. """
    min_temperature = soup.find(
        name="ul",
        class_="info_list"
    ).findAll("li")[1].find(
        name="span",
        class_="min"
    ).get_text()[:-1]
    max_temperature = soup.find(
        name="ul",
        class_="info_list"
    ).findAll("li")[1].find(
        name="span",
        class_="max"
    ).get_text()[:-1]
    sensible_temperature = soup.find(
        name="ul",
        class_="info_list"
    ).findAll("li")[1].find(
        name="span",
        class_="sensible"
    ).find(
        name="span",
        class_="num"
    ).get_text()

    air_status = soup.find(
        name="div",
        class_="detail_box"
    ).findAll("dd")
    fine_dust = air_status[0].find(
        name="span",
        class_="num"
    ).get_text()[:-3]
    fine_particulate_matter = air_status[1].find(
        name="span",
        class_="num"
    ).get_text()[:-3]
    ozone = air_status[2].find(
        name="span",
        class_="num"
    ).get_text()[:-3]

    if not soup.find(
        name="ul",
        class_="info_list"
    ).findAll("li")[2].find(
        name="span",
        class_="rainfall"
    ):
        UV_index = soup.find(
            name="ul",
            class_="info_list"
        ).findAll("li")[2].find(
            name="span",
            class_="num"
        ).get_text().split(" ")[-1]
        rainfall_per_hour = "-"
    else:
        UV_index = "-"
        rainfall_per_hour = soup.find(
            name="ul",
            class_="info_list"
        ).findAll("li")[2].find(
            name="span",
            class_="num"
        ).get_text().replace("~", " ~ ")

    weather_info_embed = discord.Embed(
        title=f":satellite: {region}의 날씨입니다. "
    )
    weather_info_embed.add_field(
        name="**• 기온 정보 : **",
        value=f"""- 현재 기온 : **{temperature}℃**
- 어제와의 온도 차 : **{temperature_difference_from_yesterday}**
- 최저 / 최고 기온 : **{min_temperature}℃ / {max_temperature}℃**
- 체감 온도 : **{sensible_temperature}℃**""",
        inline=False
    )
    weather_info_embed.add_field(
        name="**• 대기질 정보 : **",
        value=f"""- 미세먼지 : **{fine_dust} ㎍/㎥**
- 초미세먼지 : **{fine_particulate_matter} ㎍/㎥**
- 오존 지수 : **{ozone} ppm**""",
        inline=False
    )
    weather_info_embed.add_field(
        name="**• 기타 : **",
        value=f"""- 자외선 지수 : **{UV_index}**
- 시간당 강수량 : **{rainfall_per_hour}**""",
        inline=False
    )

    weather_info_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=weather_info_embed
    )


@bot.command(
    name="covid19",
    aliases=["covid-19", "코로나", "코로나19"]
)
async def covid19_status_info_command(
    ctx: commands.Context
):
    soup = bs4.BeautifulSoup(requests.get(f"""http://search.naver.com/search.naver?query={parse.quote("코로나19")}""").text, "html.parser")

    covid19_status = soup.find(
        name="div",
        class_="status_info"
    ).findAll("li")

    patient_count = covid19_status[0].find(
        name="p",
        class_="info_num"
    ).get_text().replace(",", "")
    if "variation_down" in covid19_status[0].find(
        name="em",
        class_="info_variation"
    ).attrs["class"]:
        patient_count_changelog = f"""{covid19_status[0].find(
            name="em",
            class_="info_variation"
        ).get_text().replace(",", "")}명 ▼"""
    else:
        patient_count_changelog = f"""{covid19_status[0].find(
            name="em",
            class_="info_variation"
        ).get_text().replace(",", "")}명 ▲"""

    checking_covid19_count = covid19_status[1].find(
        name="p",
        class_="info_num"
    ).get_text().replace(",", "")
    if "variation_down" in covid19_status[1].find(
        name="em",
        class_="info_variation"
    ).attrs["class"]:
        checking_covid19_count_changelog = f"""{covid19_status[1].find(
            name="em",
            class_="info_variation"
        ).get_text().replace(",", "")}명 ▼"""
    else:
        checking_covid19_count_changelog = f"""{covid19_status[1].find(
            name="em",
            class_="info_variation"
        ).get_text().replace(",", "")}명 ▲"""

    isolation_released_count = covid19_status[2].find(
        name="p",
        class_="info_num"
    ).get_text().replace(",", "")
    if "variation_down" in covid19_status[2].find(
        name="em",
        class_="info_variation"
    ).attrs["class"]:
        isolation_released_count_changelog = f"""{covid19_status[2].find(
            name="em",
            class_="info_variation"
        ).get_text().replace(",", "")}명 ▼"""
    else:
        isolation_released_count_changelog = f"""{covid19_status[2].find(
            name="em",
            class_="info_variation"
        ).get_text().replace(",", "")}명 ▲"""

    died_by_covid19_count = covid19_status[3].find(
        name="p",
        class_="info_num"
    ).get_text().replace(",", "")
    if "variation_down" in covid19_status[3].find(
        name="em",
        class_="info_variation"
    ).attrs["class"]:
        died_by_covid19_count_changelog = f"""{covid19_status[3].find(
            name="em",
            class_="info_variation"
        ).get_text()}명 ▼"""
    else:
        died_by_covid19_count_changelog = f"""{covid19_status[3].find(
            name="em",
            class_="info_variation"
        ).get_text()}명 ▲"""

    covid19_status_today = soup.find(
        name="div",
        class_="status_today"
    ).findAll("li")
    today_local_patient_count = covid19_status_today[1].find(
        name="em",
        class_="info_num"
    ).get_text().replace(",", "")
    today_oversea_patient_count = covid19_status_today[2].find(
        name="em",
        class_="info_num"
    ).get_text().replace(",", "")
    today_patient_total_count = str(int(today_local_patient_count) + int(today_oversea_patient_count)).replace(",", "")

    covid19_status_abroad = soup.find(
        name="div",
        class_="status_info abroad_info"
    ).findAll("li")
    patient_abroad_count = covid19_status_abroad[0].find(
        name="p",
        class_="info_num"
    ).get_text().replace(",", "")
    died_by_covid19_abroad_count = covid19_status_abroad[1].find(
        name="p",
        class_="info_num"
    ).get_text().replace(",", "")

    covid19_status_info_embed = discord.Embed(
        title=":information_source: 코로나19 현황입니다. "
    )
    covid19_status_info_embed.add_field(
        name="**• 국내 현황 : **",
        value=f"""- 확진환자 : **{patient_count}명 ({patient_count_changelog})**
- 검사중 : **{checking_covid19_count}명 ({checking_covid19_count_changelog})**
- 격리 해제됨 : **{isolation_released_count}명 ({isolation_released_count_changelog})**
- 사망자 : **{died_by_covid19_count}명 ({died_by_covid19_count_changelog})**""",
        inline=False
    )
    covid19_status_info_embed.add_field(
        name="**• 금일 신규 확진 현황 : **",
        value=f"""- 합계 : **{today_patient_total_count}명**
- 국내 발생 : **{today_local_patient_count}명**
- 해외 유입 : **{today_oversea_patient_count}명**"""
    )
    covid19_status_info_embed.add_field(
        name="**• 해외 현황 : **",
        value=f"""- 해외 확진환자 : **{patient_abroad_count}명**
- 해외 사망자 : **{died_by_covid19_abroad_count}명**""",
        inline=False
    )

    covid19_status_info_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=covid19_status_info_embed
    )


@bot.command(
    name="owner",
    aliases=["소유자", "제작자"]
)
async def owner_command(ctx):
    owner_embed = discord.Embed(
        title=":tools: 봇 개발자 (이하 소유자) 정보입니다. ",
        description=f"""• SanhoBot 개발자 태그 : **{(await bot.application_info()).owner.name}#{(await bot.application_info()).owner.discriminator}**
• SanhoBot 개발자 ID : **{(await bot.application_info()).owner.id}**"""
    )

    owner_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=owner_embed
    )


# ------------------------------
# Command Error Manager
# ------------------------------

@bot.event
async def on_command_error(
    ctx: commands.Context,
    error: commands.CommandError
):
    command_error_embed = discord.Embed(
        title=":warning: 명령 처리 중 오류가 발생했습니다! ",
        description="• Reason : "
    )

    if isinstance(error, commands.CommandNotFound):
        reason = "존재하지 않는 명령어"
    elif isinstance(error, commands.MissingRequiredArgument):
        reason = f"""명령어 매개변수가 비어있습니다...
{bot.command_prefix}help 명령어로 명령어 사용법을 확인해 주세요. """
    elif isinstance(error, commands.UserNotFound):
        reason = "해당 유저를 찾을 수 없습니다. "
    elif isinstance(error, commands.RoleNotFound):
        reason = "해당 역할을 찾을 수 없습니다. "
    elif isinstance(error, commands.NoPrivateMessage):
        reason = "개인 메시지에서 실행할 수 없습니다. "
    else:
        if len(str(error)) < 2048:
            reason = str(error)
        else:
            reason = """오류 내용 송신 범위 초과됨, 
별도의 에러를 출력합니다..."""
            print(reason)

    command_error_embed.description += f"**{reason}**"

    command_error_embed.set_footer(
        text=f"• 명령어 작성자 : {ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=command_error_embed
    )


# ------------------------------
# Bot Runtime
# ------------------------------

SanhoDB.setup_data()

bot.run("token")
bot.help_command = bot.get_command("help")
