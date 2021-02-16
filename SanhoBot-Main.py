import discord
from discord.ext import commands
import json
import os


class SanhoDB:
    @staticmethod
    def create_user_data(
        user_id: int
    ):
        user_json_file_path = f"./Users/{user_id}.json"
        if not os.path.isfile(
            path=user_json_file_path
        ):
            open(
                file=user_json_file_path,
                mode="w"
            ).close()

            with open(
                file=user_json_file_path,
                mode="w",
                encoding="utf-8"
            ) as user_json_file_writer:
                json.dump(
                    obj={
                        "level_info": {
                            "level": 1,
                            "exp": 0
                        },
                        "economy_info": {
                            "money": 1000
                        },
                        "item_in_inv": [
                            "나무 단검 Wooden Dagger",
                            "사과 Apple × 10"
                        ]
                    },
                    fp=user_json_file_writer,
                    indent=4,
                    ensure_ascii=False
                )

            return True
        else:
            return False

    @staticmethod
    def get_user_data(
            user_id: int
    ):
        user_json_file_path = f"./Users/{user_id}.json"

        SanhoDB.create_user_data(user_id)

        with open(
            file=user_json_file_path,
            mode="r",
            encoding="utf-8"
        ) as user_json_file_reader:
            return json.load(
                fp=user_json_file_reader
            )


bot = commands.Bot(
    command_prefix="$",
    help_command=None,
    intents=discord.Intents.all()
)


@bot.event
async def on_ready():
    print("[System] 산호봇 클라이언트 구동기를 실행했습니다! ")
    await bot.change_presence(
        activity=discord.Game(name=f"{bot.command_prefix}help | Alpha Test"),
        status=discord.Status.dnd
    )


@bot.command(
    name="help",
    aliases=["도움", "도움말"]
)
async def help_command(
    ctx: discord.ext.commands.Context
):
    help_embed = discord.Embed(
        title=":clipboard: 저희의 명령어 목록입니다! ",
        description=f"• 명령어 접두어 : `{bot.command_prefix}`\n\n• `<>` - 필수 항목\n• `[]` - 선택적 항목\n• `a | b` - 다중 항목 선택"
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}help**",
        value=f"- 명령어 목록을 표시합니다. \n- (Aliases : {bot.command_prefix}도움, {bot.command_prefix}도움말)",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}ping**",
        value=f"- 봇의 디스코드 통신 상태를 표시합니다. \n- (Aliases : {bot.command_prefix}핑)",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}role <@RoleMention | RoleID>**",
        value=f"- 해당 역할의 정보를 표시합니다. \n- (Aliases : {bot.command_prefix}roleinfo, {bot.command_prefix}역할, {bot.command_prefix}역할정보)",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}bag [<@UserMention | UserID>]**",
        value=f"- 해당 유저 또는 자신의 소지품 정보를 표시합니다. \n- (Aliases : {bot.command_prefix}inv, {bot.command_prefix}inventory, {bot.command_prefix}가방, {bot.command_prefix}소지품)"
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}connect**",
        value=f"- 자신이 입장한 음성 채널에 봇을 입장시킵니다. \n- (Aliases : {bot.command_prefix}join, {bot.command_prefix}연결, {bot.command_prefix}입장, {bot.command_prefix}참가, {bot.command_prefix}참여)",
        inline=False
    )
    help_embed.add_field(
        name=f"**{bot.command_prefix}disconnect**",
        value=f"- 봇이 현재 입장 중인 음성 채널에서 봇을 퇴장시킵니다. \n- (Aliases : {bot.command_prefix}leave, {bot.command_prefix}quit, {bot.command_prefix}퇴장)"
    )

    help_embed.set_footer(
        text=f"• 명령어 작성자 : @{ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=help_embed
    )


@bot.command(
    name="ping",
    aliases=["핑"]
)
async def ping_command(
    ctx: discord.ext.commands.Context
):
    ping_embed = discord.Embed(
        title=":signal_strength: 현재 디스코드 통신 상태입니다. ",
        description=f"• Discord 통신 속도 : **{round(bot.latency * 1000)} ms**"
    )

    ping_embed.set_footer(
        text=f"• 명령어 작성자 : @{ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=ping_embed
    )


@bot.command(
    name="role",
    aliases=["roleinfo", "역할", "역할정보"]
)
async def role_info_command(
    ctx: discord.ext.commands.Context,
    role: discord.Role = None
):
    if ctx.channel.type == discord.ChannelType.private:
        await ctx.send("개인 메시지에서 실행할 수 없습니다. ")
        return
    if isinstance(role, type(None)):
        await ctx.send("역할이 지정되어 있지 않습니다...")
        return

    role_member_list = ""
    limit_reached = False
    another_member_count = 0
    for member in role.members:
        if not limit_reached:
            if len(role_member_list + member.name + member.discriminator) + 5 > 512:
                limit_reached = True
                another_member_count += 1
            else:
                role_member_list += f"- @{member.name}#{member.discriminator}\n"
        else:
            another_member_count += 1

    if another_member_count > 0:
        role_member_list += f"...그리고 {another_member_count}명"
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
        value=f"- 총 {len(role.members)}명입니다. ",
        inline=False
    )
    role_info_embed.add_field(
        name="**• 디버깅 정보 : **",
        value=f"- 역할 ID : {role.id}",
        inline=False
    )

    role_info_embed.set_footer(
        text=f"• 명령어 작성자 : @{ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=role_info_embed
    )


@role_info_command.error
async def _role_info_command_error(
    ctx: discord.ext.commands.Context,
    error
):
    if isinstance(error, discord.ext.commands.RoleNotFound):
        await ctx.send("해당 역할을 찾을 수 없습니다...")


@bot.command(
    name="bag",
    aliases=["inv", "inventory", "가방", "소지품"]
)
async def bag_command(
    ctx: discord.ext.commands.Context,
    user: discord.User = None
):
    if isinstance(user, type(None)):
        scanned_user = ctx.author
    else:
        scanned_user = user

    data = SanhoDB.get_user_data(
        user_id=scanned_user.id
    )
    money = data["economy_info"]["money"]
    inv = ""
    for item in data["item_in_inv"]:
        inv += f"- {item}\n"
    if inv[-1] == "\n":
        inv = inv[:-1]

    bag_embed = discord.Embed(
        title=f":scroll: @{scanned_user.name}#{scanned_user.discriminator}님의 소지품 목록",
        description=f"• 보유 Dott : **{money} 도트**"
    )
    bag_embed.add_field(
        name="**• 아이템 목록 : **",
        value=inv,
        inline=False
    )

    bag_embed.set_footer(
        text=f"@{ctx.author.name}#{ctx.author.discriminator}"
    )
    await ctx.send(
        embed=bag_embed
    )


@bag_command.error
async def _bag_command_error(
    ctx: discord.ext.commands.Context,
    error: BaseException
):
    if isinstance(error, discord.ext.commands.UserNotFound):
        await ctx.send("해당 유저를 찾을 수 없습니다...")


@bot.command(
    name="connect",
    aliases=["join", "연결", "입장", "참가", "참여"],
    description=""
)
async def connect_command(
        ctx: discord.ext.commands.Context
):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("개인 메시지에서 실행할 수 없습니다 :(")
        return
    try:
        await ctx.author.voice.channel.connect()

        join_success_embed = discord.Embed(
            title=":headphones: 음성 채널에 입장했습니다! ",
            description=f"• 음성 채널 #{ctx.author.voice.channel.name}에 입장했습니다. "
        )

        join_success_embed.set_footer(
            text=f"@{ctx.author.name}#{ctx.author.discriminator}"
        )
        await ctx.send(
            embed=join_success_embed
        )
    except discord.ClientException:
        join_fail_embed = discord.Embed(
            title=":warning: 이미 음성 채널에 입장했습니다..."
        )

        join_fail_embed.set_footer(
            text=f"@{ctx.author.name}#{ctx.author.discriminator}"
        )
        await ctx.send(
            embed=join_fail_embed
        )
    except AttributeError:
        leave_fail_embed = discord.Embed(
            title=f":warning: @{ctx.author.name}#{ctx.author.discriminator}님은 음성 채널에 입장해 있지 않습니다..."
        )

        leave_fail_embed.set_footer(
            text=f"• 명령어 작성자 : @{ctx.author.name}#{ctx.author.discriminator}"
        )
        await ctx.send(
            embed=leave_fail_embed
        )


@bot.command(
    name="disconnect",
    aliases=["leave", "quit", "퇴장"]
)
async def disconnect_command(
        ctx: discord.ext.commands.Context
):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("개인 메시지에서 실행할 수 없습니다 :(")
        return
    try:
        await ctx.voice_client.disconnect()

        leave_success_embed = discord.Embed(
            title=":headphones: 음성 채널에서 퇴장했습니다...",
            description=f"• 음성 채널 #{ctx.author.voice.channel.name}에서 퇴장했습니다. "
        )

        leave_success_embed.set_footer(
            text=f"• 명령어 작성자 : @{ctx.author.name}#{ctx.author.discriminator}"
        )
        await ctx.send(
            embed=leave_success_embed
        )
    except discord.ClientException:
        leave_fail_embed = discord.Embed(
            title=f":warning: @{ctx.author.name}#{ctx.author.discriminator} 음성 채널에 입장해 있지 않습니다. "
        )

        leave_fail_embed.set_footer(
            text=f"• 명령어 작성자 : @{ctx.author.name}#{ctx.author.discriminator}"
        )
        await ctx.send(
            embed=leave_fail_embed
        )
    except AttributeError:
        leave_fail_embed = discord.Embed(
            title=":warning: 봇이 음성 채널에 입장해 있지 않습니다. "
        )

        leave_fail_embed.set_footer(
            text=f"• 명령어 작성자 : @{ctx.author.name}#{ctx.author.discriminator}"
        )
        await ctx.send(
            embed=leave_fail_embed
        )


@bot.event
async def on_command_error(
    ctx: discord.ext.commands.Context,
    error: discord.ext.commands.CommandError
):
    if isinstance(error, discord.ext.commands.CommandNotFound):
        await help_command(ctx)


os.chdir(
    path="./Data"
)
if not os.path.isdir("./Users"):
    os.mkdir(
        path="./Users"
    )

bot.run(__import__("os").environ['bot_token'])
bot.help_command = bot.get_command(
    name="help"
)

while True:
    print("hello, world")
