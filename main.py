import os
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

@bot.tree.command(name='message', description='Write the message you want to send')
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

ANNOUNCEMENT_AUTHOR = "📢 VVNE・ANNOUNCEMENT"
ANNOUNCEMENT_COLOR = 0xC97734


# CHECK ANNOUNCEMENT

def is_vvne_announcement(message):
    if not bot.user or message.author.id != bot.user.id:
        return False

    if not message.embeds:
        return False

    embed = message.embeds[0]

    return (
        embed.author is not None
        and embed.author.name == ANNOUNCEMENT_AUTHOR
    )


def is_poll_announcement(embed):
    footer = embed.footer.text or ""
    return "POLL" in footer.upper()


# EMOJI HANDLING

def parse_voting_emoji(value):
    value = value.strip()

    if not value:
        raise ValueError("Please enter an emoji")

    if value.startswith("<") or value.endswith(">"):
        emoji = discord.PartialEmoji.from_str(value)

        if emoji.id is None or not emoji.name:
            raise ValueError("Invalid Custom Emoji format")

        return emoji

    return value


def get_emoji_key(value):
    emoji = parse_voting_emoji(value)

    if isinstance(emoji, discord.PartialEmoji):
        return f"custom:{emoji.id}"

    return f"unicode:{emoji}"


# ANNOUNCEMENT TYPE

class AnnouncementTypeView(discord.ui.View):
    def __init__(self, channel, mention_everyone):
        super().__init__(timeout=180)

        self.channel = channel
        self.mention_everyone = mention_everyone

    @discord.ui.button(
        label="General",
        emoji="💼",
        style=discord.ButtonStyle.primary
    )
    async def general(self, interaction, button):
        await interaction.response.send_modal(
            AnnouncementDetailsModal(
                self.channel,
                self.mention_everyone,
                "general"
            )
        )

    @discord.ui.button(
        label="Poll",
        emoji="🪴",
        style=discord.ButtonStyle.success
    )
    async def poll(self, interaction, button):
        await interaction.response.send_modal(
            AnnouncementDetailsModal(
                self.channel,
                self.mention_everyone,
                "poll"
            )
        )


# ANNOUNCEMENT DETAILS

class AnnouncementDetailsModal(discord.ui.Modal):
    def __init__(self, channel, mention_everyone, announcement_type):
        super().__init__(title="VVNE Announcement")

        self.channel = channel
        self.mention_everyone = mention_everyone
        self.announcement_type = announcement_type

        self.title_input = discord.ui.TextInput(
            label="𐔌 🪴𓂃 Announcement Title ၄💼၃ ꒱",
            placeholder="╰┈➤・Enter announcement title ୨୧",
            max_length=100
        )

        self.message_input = discord.ui.TextInput(
            label="𐔌 👢 Announcement Message :: 🍮 ꒱",
            placeholder="╰┈➤・Enter announcement details ୨୧",
            style=discord.TextStyle.paragraph,
            max_length=1000
        )

        self.add_item(self.title_input)
        self.add_item(self.message_input)

    async def on_submit(self, interaction):
        view = AnnouncementBuilderView(
            channel=self.channel,
            title=self.title_input.value.strip(),
            message=self.message_input.value.strip(),
            mention_everyone=self.mention_everyone,
            announcement_type=self.announcement_type
        )

        await interaction.response.send_message(
            embed=view.create_embed(),
            view=view,
            ephemeral=True
        )

        view.message_preview = await interaction.original_response()


# ADD POLL OPTION

class AddVotingOptionModal(discord.ui.Modal):
    def __init__(self, builder):
        super().__init__(title="Add Voting Option")

        self.builder = builder

        self.option_input = discord.ui.TextInput(
            label="𐔌 🍁ᯓ Option Name 📋 ꒱",
            placeholder="╰┈➤・Enter option name ୨୧",
            max_length=45
        )

        self.emoji_input = discord.ui.TextInput(
            label="𐔌 📬 Option Emoji 🧸 ˙ᵕ˙ ꒱",
            placeholder="╰┈➤・Enter Unicode or Custom Emoji",
            required=True,
            max_length=100
        )

        self.add_item(self.option_input)
        self.add_item(self.emoji_input)

    async def on_submit(self, interaction):
        option = self.option_input.value.strip()
        emoji = self.emoji_input.value.strip()

        if not option:
            await interaction.response.send_message(
                "Please enter an option name",
                ephemeral=True
            )
            return

        try:
            emoji_key = get_emoji_key(emoji)
        except ValueError as error:
            await interaction.response.send_message(
                str(error),
                ephemeral=True
            )
            return

        if len(self.builder.options) >= 20:
            await interaction.response.send_message(
                "You can add up to 20 voting options",
                ephemeral=True
            )
            return

        for existing_option, existing_emoji in self.builder.options:
            if get_emoji_key(existing_emoji) == emoji_key:
                await interaction.response.send_message(
                    "This emoji has already been used",
                    ephemeral=True
                )
                return

        self.builder.options.append((option, emoji))

        await interaction.response.defer(ephemeral=True)

        try:
            if self.builder.message_preview is None:
                raise RuntimeError("Announcement preview not found")

            await self.builder.message_preview.edit(
                embed=self.builder.create_embed(),
                view=self.builder
            )

            await interaction.followup.send(
                "Voting option added successfully!",
                ephemeral=True
            )

        except (discord.HTTPException, RuntimeError) as error:
            self.builder.options.pop()

            await interaction.followup.send(
                f"Failed to update announcement preview: {error}",
                ephemeral=True
            )


# ANNOUNCEMENT BUILDER

class AnnouncementBuilderView(discord.ui.View):
    def __init__(
        self,
        channel,
        title,
        message,
        mention_everyone,
        announcement_type
    ):
        super().__init__(timeout=900)

        self.channel = channel
        self.title = title
        self.announcement_text = message
        self.mention_everyone = mention_everyone
        self.announcement_type = announcement_type
        self.options = []
        self.message_preview = None

        if self.announcement_type == "general":
            for item in self.children:
                if (
                    isinstance(item, discord.ui.Button)
                    and item.custom_id == "vvne_add_poll_option"
                ):
                    self.remove_item(item)
                    break

    def create_embed(self):
        description = self.announcement_text

        if self.announcement_type == "poll":
            if self.options:
                description += (
                    "\n\n"
                    "**୨˗ˏˋ react with an emoji to vote❕୨ৎ**\n\n"
                )

                description += "\n".join(
                    f"{emoji}  **{option}**"
                    for option, emoji in self.options
                )
            else:
                description += (
                    "\n\n"
                    "*Add voting options using the button below*"
                )

        embed = discord.Embed(
            title=self.title,
            description=description,
            color=ANNOUNCEMENT_COLOR
        )

        embed.set_author(name=ANNOUNCEMENT_AUTHOR)

        embed.set_footer(
            text=(
                "VVNE・ANNOUNCEMENT | POLL"
                if self.announcement_type == "poll"
                else "VVNE・ANNOUNCEMENT | GENERAL"
            )
        )

        return embed

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        if self.message_preview:
            try:
                await self.message_preview.edit(view=self)
            except discord.HTTPException:
                pass

    @discord.ui.button(
        label="Add Option",
        emoji="➕",
        style=discord.ButtonStyle.secondary,
        custom_id="vvne_add_poll_option",
        row=0
    )
    async def add_option(self, interaction, button):
        if self.announcement_type != "poll":
            await interaction.response.send_message(
                "This is not a Poll announcement",
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            AddVotingOptionModal(self)
        )

    @discord.ui.button(
        label="Publish Announcement",
        emoji="📢",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def publish(self, interaction, button):
        if self.announcement_type == "poll" and len(self.options) < 2:
            await interaction.response.send_message(
                "Please add at least 2 voting options",
                ephemeral=True
            )
            return

        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server",
                ephemeral=True
            )
            return

        bot_member = guild.me

        if bot_member is None:
            await interaction.response.send_message(
                "Unable to identify bot permissions",
                ephemeral=True
            )
            return

        permissions = self.channel.permissions_for(bot_member)

        if not permissions.send_messages:
            await interaction.response.send_message(
                "The bot needs Send Messages permission",
                ephemeral=True
            )
            return

        if not permissions.embed_links:
            await interaction.response.send_message(
                "The bot needs Embed Links permission",
                ephemeral=True
            )
            return

        if self.mention_everyone and not permissions.mention_everyone:
            await interaction.response.send_message(
                "The bot needs Mention Everyone permission",
                ephemeral=True
            )
            return

        if self.announcement_type == "poll":
            if not permissions.add_reactions:
                await interaction.response.send_message(
                    "The bot needs Add Reactions permission",
                    ephemeral=True
                )
                return

            for option, emoji_value in self.options:
                emoji = parse_voting_emoji(emoji_value)

                if (
                    isinstance(emoji, discord.PartialEmoji)
                    and guild.get_emoji(emoji.id) is None
                    and not permissions.use_external_emojis
                ):
                    await interaction.response.send_message(
                        "The bot needs Use External Emojis permission",
                        ephemeral=True
                    )
                    return

        await interaction.response.defer(ephemeral=True)

        try:
            announcement_message = await self.channel.send(
                content=(
                    "@everyone || announcement ﹒ᐟ﹒ᐟ"
                    if self.mention_everyone
                    else None
                ),
                embed=self.create_embed(),
                allowed_mentions=discord.AllowedMentions(
                    everyone=self.mention_everyone,
                    users=False,
                    roles=False
                )
            )

        except discord.Forbidden:
            await interaction.edit_original_response(
                content="The bot does not have permission to publish here",
                embed=None,
                view=None
            )
            return

        except discord.HTTPException as error:
            await interaction.edit_original_response(
                content=f"Failed to publish announcement: {error}",
                embed=None,
                view=None
            )
            return

        reaction_errors = []

        if self.announcement_type == "poll":
            for option, emoji_value in self.options:
                try:
                    reaction = parse_voting_emoji(emoji_value)
                    await announcement_message.add_reaction(reaction)

                except (discord.HTTPException, ValueError) as error:
                    reaction_errors.append(
                        f"{emoji_value}: {error}"
                    )

        self.stop()

        result = (
            f"Announcement published successfully!\n"
            f"Channel: {self.channel.mention}\n"
            f"Message ID: `{announcement_message.id}`"
        )

        if reaction_errors:
            result += (
                "\n\nFailed to add some reactions:\n"
                + "\n".join(reaction_errors)
            )

        await interaction.edit_original_response(
            content=result,
            embed=None,
            view=None
        )


# SLASH COMMAND - ANNOUNCEMENT

@bot.tree.command(
    name="announcement",
    description="Create a General or Poll announcement"
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    channel="Select announcement channel",
    mention_everyone="Mention everyone or not"
)
async def announcement(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    mention_everyone: bool = False
):
    embed = discord.Embed(
        title="📢 VVNE・ANNOUNCEMENT BUILDER",
        description=(
            "Select an announcement type to get started 👢 .ᐟ\n\n"
            "💼 **General**\n"
            "Create a normal announcement❕\n\n"
            "🪴 **Poll**\n"
            "Create an announcement with voting options and emojis :: 🍮"
        ),
        color=ANNOUNCEMENT_COLOR
    )

    await interaction.response.send_message(
        embed=embed,
        view=AnnouncementTypeView(
            channel,
            mention_everyone
        ),
        ephemeral=True
    )


# DELETE ANNOUNCEMENT

@bot.tree.command(
    name="delete_announcement",
    description="Delete a VVNE announcement"
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    channel="Select announcement channel",
    message_id="Announcement Message ID"
)
async def delete_announcement(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message_id: str
):
    if not message_id.isdigit():
        await interaction.response.send_message(
            "Please enter a valid Message ID",
            ephemeral=True
        )
        return

    try:
        announcement_message = await channel.fetch_message(
            int(message_id)
        )

        if not is_vvne_announcement(announcement_message):
            await interaction.response.send_message(
                "This is not a VVNE BOT announcement",
                ephemeral=True
            )
            return

        await announcement_message.delete()

        await interaction.response.send_message(
            "Announcement deleted successfully!",
            ephemeral=True
        )

    except discord.NotFound:
        await interaction.response.send_message(
            "Message not found | Please check the Message ID",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "The bot does not have permission to delete this message",
            ephemeral=True
        )

    except discord.HTTPException as error:
        await interaction.response.send_message(
            f"An error occurred: {error}",
            ephemeral=True
        )


# CLOSE VOTING

@bot.tree.command(
    name="voteing_closed",
    description="Close voting on an announcement"
)
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    channel="Select announcement channel",
    message_id="Announcement Message ID"
)
async def voteing_closed(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message_id: str
):
    if not message_id.isdigit():
        await interaction.response.send_message(
            "Please enter a valid Message ID",
            ephemeral=True
        )
        return

    try:
        poll_message = await channel.fetch_message(
            int(message_id)
        )

        if not is_vvne_announcement(poll_message):
            await interaction.response.send_message(
                "This is not a VVNE BOT announcement",
                ephemeral=True
            )
            return

        embed = poll_message.embeds[0]

        if not is_poll_announcement(embed):
            await interaction.response.send_message(
                "This announcement is not a Poll",
                ephemeral=True
            )
            return

        if "POLL CLOSED" in (embed.footer.text or "").upper():
            await interaction.response.send_message(
                "Voting is already closed",
                ephemeral=True
            )
            return

        bot_member = interaction.guild.me
        permissions = channel.permissions_for(bot_member)

        if not permissions.manage_messages:
            await interaction.response.send_message(
                "The bot needs Manage Messages permission",
                ephemeral=True
            )
            return

        embed.description = (
            (embed.description or "")
            + "\n\n🐻 **voting closed**"
        )

        embed.set_footer(
            text="VVNE・ANNOUNCEMENT | POLL CLOSED"
        )

        await poll_message.edit(embed=embed)
        await poll_message.clear_reactions()

        await interaction.response.send_message(
            "Voting closed successfully!",
            ephemeral=True
        )

    except discord.NotFound:
        await interaction.response.send_message(
            "Message not found | Please check the Message ID",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "The bot does not have permission to manage this message",
            ephemeral=True
        )

    except discord.HTTPException as error:
        await interaction.response.send_message(
            f"An error occurred: {error}",
            ephemeral=True
        )

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
    name="anonymous_setup",
    description="Set up the anonymous message system"
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


server_on()

bot.run(os.getenv('TOKEN'))