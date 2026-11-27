import asyncio
import os
import json
import discord
from discord import app_commands
from discord.ext import commands

from myserver import server_on

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())




# Bot Event
# คำสั่งบอทพร้อมใช้งาน

@bot.event
async def on_ready():
    print(f"Status : {bot.user} Online!")
    synced = await bot.tree.sync()
    print(f"{len(synced)} command(s)")

# VVNE BOT - คำสั่งบอทแจ้งเมื่อมีสมาชิกใหม่เข้ากลุ่ม

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1554350154352689202)

    text = (
        "────────୨ৎ────────\n"
        "💼・MENU・Ი𐑼\n"
        "・𐙚 rules • <#1554373479569162270>\n"
        "・𐙚 global chat • <#1554380791113457675>\n"
        "・𐙚 thread • <#1554380919530332200>\n"
        "・𐙚 voice chat • https://discord.com/channels/1554346869344440330/1554382938072678420\n"
        "\n"
        "🍂・Please verify yourself in this channel・𝜗𝜚\n"
        "・𐙚 Let’s verify your identity • <#1554392774088859648>\n"
        "────────୨ৎ────────\n"
        "Ი𐑼 Have fun with the group 𝜗𝜚🐻"
    )

    emmbed = discord.Embed(
        title=f"🧸 {member.display_name}",
        description=(
            f"Welcome to the Toca Vivienne official discord ᰔᩚ\n\n"
            f"{text}"
        ),
        color=0xC97734
    )

    emmbed.set_author(
        name=member.display_name,
        icon_url=member.display_avatar.url
    )

    emmbed.set_thumbnail(
        url=member.display_avatar.url
    )

    emmbed.set_image(
        url="https://imglink.cc/cdn/F02w4SubQ_.jpg"
    )

    await channel.send(embed=emmbed)

# VVNE BOT - กำหนดคำสั่งบอท เริ่มต้น

# @bot.command()
# async def text(ctx, arg):
    # await ctx.send(arg)

# VVNE BOT - ระบบส่งข้อความ || Slash

@bot.tree.command(name='create_message', description='Write the message you want to send')
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    channel='Select the channel to send the message to',
    message='Enter the message you want to send',
    emmbed='Choose whether to send the message as an embed'
)
@app_commands.choices(emmbed=[
    app_commands.Choice(name='📋 Open Embed', value='yes'),
    app_commands.Choice(name='📎 Close Embed', value='no')
])
async def message(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str,
    emmbed: app_commands.Choice[str]
):
    if emmbed.value == 'yes':
        embed = discord.Embed(
            description=message,
            color=0xC97734
        )
        await channel.send(embed=embed)
    else:
        await channel.send(message)

    await interaction.response.send_message(
        f'Message sent to {channel.mention} successfully!',
        ephemeral=True
    )

# VVNE BOT - ระบบ Announcement || Slash

VVNE_ANNOUNCEMENT_DATA = "vvne_announcement_data.json"
VVNE_BAR_LENGTH = 16
VVNE_MAX_BUTTON_OPTIONS = 10

def _load_announcement_data():
    try:
        with open(VVNE_ANNOUNCEMENT_DATA, "r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Invalid announcement data")
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        data = {}
    data.setdefault("announcements", {})
    data.setdefault("polls", {})
    return data

ANNOUNCEMENT_DATA = _load_announcement_data()
_RESTORED_POLL_VIEWS = False


def _save_announcement_data():
    temp_file = VVNE_ANNOUNCEMENT_DATA + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(ANNOUNCEMENT_DATA, file, ensure_ascii=False, indent=2)
    os.replace(temp_file, VVNE_ANNOUNCEMENT_DATA)


def _parse_announcement_emoji(value):
    value = value.strip()
    if not value:
        raise ValueError("Please enter an emoji.")
    if value.startswith("<") and value.endswith(">"):
        emoji = discord.PartialEmoji.from_str(value)
        if emoji.id is None or not emoji.name:
            raise ValueError("Invalid custom emoji. Use a format such as <:name:id>.")
        return str(emoji)
    return value


def _emoji_key(value):
    parsed = _parse_announcement_emoji(value)
    if parsed.startswith("<"):
        emoji = discord.PartialEmoji.from_str(parsed)
        return f"custom:{emoji.id}"
    return f"unicode:{parsed}"


def _is_vvne_announcement(message):
    if bot.user is None or message.author.id != bot.user.id:
        return False

    if str(message.id) in ANNOUNCEMENT_DATA["announcements"]:
        return True

    # Backward compatibility: also recognize announcements created by the old Embed system.
    for embed in message.embeds:
        if embed.author and embed.author.name == "📢 VVNE・ANNOUNCEMENT":
            return True
    return False


def _make_announcement_text(title, body):
    return f"**{title}**\n{body}".strip()


def _render_button_poll(record):
    total = sum(len(voters) for voters in record["votes"].values())
    lines = [f"**{record['title']}**", record["body"], ""]
    lines.append("**Poll results**")
    for index, option in enumerate(record["options"]):
        voters = record["votes"].get(str(index), [])
        count = len(voters)
        percent = (count / total * 100) if total else 0
        filled = round(percent / 100 * VVNE_BAR_LENGTH)
        bar = option["bar"] * filled + "▫️" * (VVNE_BAR_LENGTH - filled)
        lines.append(
            f"{option['emoji']} **{option['name']}**\n"
            f"{percent:.1f}% · {count} vote(s)\n"
            f"{bar}"
        )
    if record.get("closed"):
        lines.append("\n🔒 **Voting closed**")
    else:
        lines.append("\nSelect an option below to vote.")
    return "\n".join(lines)


def _make_voter_list(guild, user_ids):
    names = []

# VVNE BOT - ระบบฝากบอก

ANONYMOUS_GENERAL_CHANNEL_ID = 1554380791113457675
ANONYMOUS_AUDIT_CHANNEL_ID = 1570792552758775929
ANONYMOUS_AUDIT_TOPIC = "VVNE_ANONYMOUS_AUDIT"


def get_anonymous_audit_channel(guild):
    channel = guild.get_channel(ANONYMOUS_AUDIT_CHANNEL_ID)

    if isinstance(channel, discord.TextChannel):
        return channel

    return discord.utils.get(
        guild.text_channels,
        topic=ANONYMOUS_AUDIT_TOPIC
    )


async def setup_anonymous_audit_channel(guild):
    audit_channel = get_anonymous_audit_channel(guild)

    owner = guild.get_member(guild.owner_id)

    if owner is None:
        owner = await guild.fetch_member(guild.owner_id)

    bot_member = guild.me

    if bot_member is None:
        bot_member = guild.get_member(bot.user.id)

    if bot_member is None:
        bot_member = await guild.fetch_member(bot.user.id)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=False
        ),
        owner: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            embed_links=True
        ),
        bot_member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            embed_links=True
        )
    }

    if audit_channel is None:
        audit_channel = await guild.create_text_channel(
            name="anonymous-message-logs",
            topic=ANONYMOUS_AUDIT_TOPIC,
            overwrites=overwrites,
            reason="Create private anonymous message logs"
        )
    else:
        await audit_channel.edit(
            topic=ANONYMOUS_AUDIT_TOPIC,
            overwrites=overwrites,
            reason="Update anonymous message log permissions"
        )

    return audit_channel


class AnonymousMessageModal(discord.ui.Modal):
    def __init__(self, recipient):
        super().__init__(title="Anonymous Message")
        self.recipient = recipient

        self.message_input = discord.ui.TextInput(
            label="𐔌 📋 Your Message ❕𓂃 ꒱",
            placeholder="╰┈➤・Type your anonymous message here ୨୧",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )
        self.add_item(self.message_input)

    async def on_submit(self, interaction: discord.Interaction):
        sender = interaction.user
        recipient = self.recipient
        message = self.message_input.value.strip()

        if not message:
            await interaction.response.send_message(
                "Please enter a message before submitting",
                ephemeral=True
            )
            return

        if recipient.id == sender.id:
            await interaction.response.send_message(
                "You cannot send an anonymous message to yourself",
                ephemeral=True
            )
            return

        if recipient.bot:
            await interaction.response.send_message(
                "You cannot send an anonymous message to a bot",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        delivery_status = "DM Delivered"

        dm_embed = discord.Embed(
            title="💌 Anonymous Message",
            description=message,
            color=0xC97734
        )
        dm_embed.set_footer(
            text="Someone sent you an anonymous message"
        )

        try:
            await recipient.send(embed=dm_embed)

        except (discord.Forbidden, discord.HTTPException):
            delivery_status = "DM Failed"

            general = interaction.client.get_channel(
                ANONYMOUS_GENERAL_CHANNEL_ID
            )

            if general is None:
                try:
                    general = await interaction.client.fetch_channel(
                        ANONYMOUS_GENERAL_CHANNEL_ID
                    )
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    general = None

            if general:
                fallback_embed = discord.Embed(
                    title="💌 Anonymous Message",
                    description=message,
                    color=0xC97734
                )
                fallback_embed.add_field(
                    name="📬 Recipient",
                    value=recipient.mention,
                    inline=False
                )
                fallback_embed.set_footer(
                    text="The recipient could not receive direct messages"
                )

                try:
                    await general.send(
                        embed=fallback_embed,
                        allowed_mentions=discord.AllowedMentions(
                            users=[recipient]
                        )
                    )
                    delivery_status = "General Fallback Delivered"

                except discord.HTTPException:
                    delivery_status = "DM and General Fallback Failed"

        # Save sender, recipient, and message
        audit_channel = get_anonymous_audit_channel(
            interaction.guild
        )

        if audit_channel:
            audit_embed = discord.Embed(
                title="📋 Anonymous Message Log",
                color=0xC97734
            )

            audit_embed.add_field(
                name="👤 Sender",
                value=f"{sender.mention}\n`{sender.id}`",
                inline=False
            )

            audit_embed.add_field(
                name="📬 Recipient",
                value=f"{recipient.mention}\n`{recipient.id}`",
                inline=False
            )

            audit_embed.add_field(
                name="💬 Message",
                value=message,
                inline=False
            )

            audit_embed.add_field(
                name="📡 Delivery Status",
                value=delivery_status,
                inline=False
            )

            try:
                await audit_channel.send(
                    embed=audit_embed,
                    allowed_mentions=discord.AllowedMentions.none()
                )
            except discord.HTTPException:
                pass

        await interaction.followup.send(
            "Your anonymous message has been sent! 💌"
            if delivery_status != "DM and General Fallback Failed"
            else "Your message could not be delivered. Please try again later.",
            ephemeral=True
        )


class AnonymousRecipientView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.recipient_select = discord.ui.UserSelect(
            placeholder="Select a recipient...",
            min_values=1,
            max_values=1
        )

        self.recipient_select.callback = self.select_recipient
        self.add_item(self.recipient_select)

    async def select_recipient(self, interaction: discord.Interaction):
        recipient = self.recipient_select.values[0]

        if recipient.id == interaction.user.id:
            await interaction.response.send_message(
                "You cannot select yourself as the recipient",
                ephemeral=True
            )
            return

        if recipient.bot:
            await interaction.response.send_message(
                "You cannot select a bot as the recipient",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            AnonymousMessageModal(recipient)
        )


class AnonymousMessageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Anonymous message",
        emoji="📬",
        style=discord.ButtonStyle.success,
        custom_id="vvne_anonymous_message"
    )
    async def anonymous_message(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "👀 Select the person you want to send an anonymous message to ୨୧",
            view=AnonymousRecipientView(),
            ephemeral=True
        )


@bot.tree.command(
    name="create_anonymous",
    description="Create an anonymous message"
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    channel="Select the channel where the anonymous message system will be posted"
)
async def anonymous_setup(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        # Create or reuse the single private audit channel
        audit_channel = await setup_anonymous_audit_channel(guild)

        # Original Thai Embed and green button
        embed = discord.Embed(
            description=(
                "**𐔌 👩🏼‍❤️‍💋‍👨🏼ᯓ anonymous message 📎﹒ᐟ﹒ᐟ**\n\n"
                "**🕰️୨୧ ฝากข้อความถึงใครบางคน โดยไม่เปิดเผยตัวตน ˙ᵕ˙ 🐻 ꒱**"
            ),
            color=0xC97734
        )

        await channel.send(
            embed=embed,
            view=AnonymousMessageView()
        )

        await interaction.followup.send(
            f"Anonymous message system has been successfully installed! 💚\n"
            f"📬 System Channel: {channel.mention}\n"
            f"🔒 Private Log Channel: {audit_channel.mention}",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.followup.send(
            "The bot does not have permission to create or manage channels.",
            ephemeral=True
        )

    except discord.HTTPException as error:
        await interaction.followup.send(
            f"An error occurred while setting up the system: {error}",
            ephemeral=True
        )


@anonymous_setup.error
async def anonymous_setup_error(
    interaction: discord.Interaction,
    error
):
    if isinstance(error, app_commands.MissingPermissions):
        message = "You need Administrator permission to use this command."
    else:
        message = f"An error occurred: {error}"

    if interaction.response.is_done():
        await interaction.followup.send(
            message,
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            message,
            ephemeral=True
        )


# Register persistent button view
bot.add_view(AnonymousMessageView())


# VVNE BOT - Status

@bot.tree.command(
    name="bot_status",
    description="Check VVNE status"
)
async def bot_status(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🖇️ VVNE BOT • Status",
        description="",
        color=0xC97734
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )

    status_lines = [
        f"➤ {bot.user}",
        "➤ Server is running!"
    ]

    displayed_text = ""

    for line in status_lines:
        await asyncio.sleep(0.7)

        displayed_text += (
            ("\n" if displayed_text else "")
            + line
        )

        embed.description = displayed_text

        await interaction.edit_original_response(
            embed=embed
        )

server_on()

bot.run(os.getenv('TOKEN'))
