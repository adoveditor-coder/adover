import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import os
from datetime import datetime, timedelta
import aiosqlite
import re

# إعدادات البوت الأساسية مع تحسين الأداء [citation:1]
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix='!', 
    intents=intents,
    # تحسين أداء البوت [citation:1]
    max_messages=None,  # تقليل استخدام الذاكرة
    chunk_guilds_at_startup=False  # تحسين وقت البدء
)

# قاعدة البيانات مع تحسين الأداء [citation:1]
DB_NAME = "bot_database.db"

# ترجمة النصوص للغتين مع تحسين استخدام الذاكرة [citation:1]
translations = {
    "ar": {
        "ban_success": "تم حظر {} بسبب: {}",
        "ban_no_permission": "ليس لديك صلاحية لحظر الأعضاء!",
        "unban_success": "تم رفع الحظر عن {}",
        "unban_no_permission": "ليس لديك صلاحية لرفع الحظر عن الأعضاء!",
        "unban_not_found": "لم يتم العثور على هذا المستخدم أو الآيدي غير صحيح!",
        "kick_success": "تم طرد {} بسبب: {}",
        "kick_no_permission": "ليس لديك صلاحية لطرد الأعضاء!",
        "mute_success": "تم كتم {} لمدة {} دقائق بسبب: {}",
        "mute_no_permission": "ليس لديك صلاحية لكتم الأعضاء!",
        "unmute_success": "تم رفع الكتم عن {}",
        "unmute_no_permission": "ليس لديك صلاحية لرفع الكتم عن الأعضاء!",
        "unmute_not_muted": "هذا العضو غير مكتوم!",
        "warn_success": "تم تحذير {}. عدد تحذيراته: {}. السبب: {}",
        "warn_no_permission": "ليس لديك صلاحية لتحذير الأعضاء!",
        "clear_success": "تم مسح {} رسالة!",
        "clear_no_permission": "ليس لديك صلاحية لمسح الرسائل!",
        "clear_too_many": "لا يمكن مسح أكثر من 100 رسالة في المرة الواحدة!",
        "nick_success": "تم تغيير لقب {} إلى {}",
        "nick_no_permission": "ليس لديك صلاحية لتغيير الألقاب!",
        "role_add_success": "تم إضافة دور {} إلى {}",
        "role_remove_success": "تم إزالة دور {} من {}",
        "role_no_permission": "ليس لديك صلاحية لإدارة الأدوار!",
        "role_invalid_action": "الإجراء يجب أن يكون إما add أو remove!",
        "language_set": "تم تعيين اللغة إلى العربية بنجاح!",
        "language_already_set": "اللغة مضبوطة بالفعل على العربية!",
        "language_changed": "تم تغيير اللغة إلى العربية بنجاح!",
        "language_set_english": "Language has been set to English successfully!",
        "language_already_set_english": "Language is already set to English!",
        "language_changed_english": "Language has been changed to English successfully!",
        "select_language": "يرجى اختيار اللغة / Please select a language",
        "arabic": "العربية",
        "english": "English",
        "points_display": "{} لديه {} نقطة!",
        "rep_success": "تم منح نقطة سمعة لـ {}!",
        "rep_self": "لا يمكنك منح السمعة لنفسك!",
        "server_info_title": "معلومات السيرفر: {}",
        "user_info_title": "معلومات المستخدم: {}",
        "top_members_title": "أفضل 10 أعضاء حسب النقاط",
        "profile_title": "الملف الشخصي لـ {}",
        "roll_result": "🎲 {} رمى النرد وحصل على: {} (من أصل {})",
        "8ball_response": "🎱 السؤال: {}\nالإجابة: {}",
        "coinflip_result": "🪙 {} رمى العملة وحصل على: {}",
        "meme_title": "ميم عشوائي",
        "ping_result": "🏓 سرعة الاستجابة: {}ms",
        "welcome_message": "مرحباً بك في السيرفر! يرجى استخدام الأمر `/language` لاختيار اللغة.",
        "channel_restrict_success": "تم تقييد البوت للقناة {} بنجاح!",
        "channel_restrict_remove": "تم إلغاء تقييد البوت للقناة {} بنجاح!",
        "channel_restrict_list": "القنوات المسموح للبوت بالعمل فيها: {}",
        "channel_restrict_none": "لا توجد قيود على القنوات، البوت يعمل في جميع القنوات.",
        "channel_not_allowed": "هذا البوت غير مسموح له بالعمل في هذه القناة!",
        "slowmode_success": "تم تعيين الوضع البطيء إلى {} ثواني لهذه القناة!",
        "slowmode_remove": "تم إلغاء الوضع البطيء لهذه القناة!",
        "poll_created": "تم إنشاء الاستفتاء بنجاح!",
        "poll_question": "سؤال الاستفتاء",
        "suggest_added": "تم إضافة الاقتراح بنجاح!",
        "tag_created": "تم إنشاء الوسم '{}' بنجاح!",
        "tag_exists": "هذا الوسم موجود بالفعل!",
        "tag_not_found": "الوسم '{}' غير موجود!",
        "tag_deleted": "تم حذف الوسم '{}' بنجاح!",
        "tag_info": "معلومات الوسم '{}': {}",
        "invite_bot": "https://discord.com/oauth2/authorize?client_id={}&scope=bot&permissions=8",
        "trigger_added": "تم إضافة الاختصار '{}' بنجاح للرتب: {}!",
        "trigger_removed": "تم إزالة الاختصار '{}' بنجاح!",
        "trigger_exists": "الاختصار '{}' موجود بالفعل!",
        "trigger_not_found": "الاختصار '{}' غير موجود!",
        "trigger_list": "قائمة الاختصارات:\n{}",
        "trigger_no_permission": "ليس لديك صلاحية لإدارة الاختصارات!",
        "help_command": """
**🎯 الأوامر الإدارية:**
`/ban` - حظر عضو من السيرفر
`/unban` - رفع الحظر عن عضو
`/kick` - طرد عضو من السيرفر
`/mute` - كتم عضو
`/unmute` - رفع الكتم عن عضو
`/warn` - تحذير عضو
`/clear` - مسح الرسائل
`/setnick` - تغيير لقب عضو
`/role` - إدارة أدوار العضو
`/slowmode` - تعيين وضع بطيء
`/serverinfo` - معلومات السيرفر
`/userinfo` - معلومات المستخدم

**🎪 الأوامر الترفيهية:**
`/roll` - رمي نرد عشوائي
`/8ball` - سؤال الكرة السحرية
`/coinflip` - رمي عملة معدنية
`/meme` - عرض ميم عشوائي
`/ping` - اختبار سرعة الاستجابة

**⚙️ أوامر الإعدادات:**
`/language` - تغيير لغة البوت
`/channel_restrict` - تقييد البوت للقناة
`/channel_unrestrict` - إلغاء تقييد القناة
`/channel_list` - عرض القنوات المسموحة

**🏷️ أوامر الأوسمة:**
`/tag_create` - إنشاء وسم جديد
`/tag` - عرض وسم
`/tag_delete` - حذف وسم
`/tag_list` - عرض جميع الأوسمة

**📊 أوامر النقاط:**
`/credits` - عرض الرصيد
`/rep` - منح سمعة
`/rank` - عرض الرتبة
`/top` - أفضل الأعضاء
`/profile` - الملف الشخصي

**🔧 أوامر الاختصارات (باستخدام !):**
`!addtrigger` - إضافة اختصار جديد
`!deltrigger` - حذف اختصار
`!listtriggers` - عرض جميع الاختصارات
"""
    },
    "en": {
        "ban_success": "Banned {} for: {}",
        "ban_no_permission": "You don't have permission to ban members!",
        "unban_success": "Unbanned {}",
        "unban_no_permission": "You don't have permission to unban members!",
        "unban_not_found": "User not found or ID is incorrect!",
        "kick_success": "Kicked {} for: {}",
        "kick_no_permission": "You don't have permission to kick members!",
        "mute_success": "Muted {} for {} minutes because: {}",
        "mute_no_permission": "You don't have permission to mute members!",
        "unmute_success": "Unmuted {}",
        "unmute_no_permission": "You don't have permission to unmute members!",
        "unmute_not_muted": "This member is not muted!",
        "warn_success": "Warned {}. Warning count: {}. Reason: {}",
        "warn_no_permission": "You don't have permission to warn members!",
        "clear_success": "Cleared {} messages!",
        "clear_no_permission": "You don't have permission to clear messages!",
        "clear_too_many": "Cannot delete more than 100 messages at once!",
        "nick_success": "Changed {}'s nickname to {}",
        "nick_no_permission": "You don't have permission to change nicknames!",
        "role_add_success": "Added role {} to {}",
        "role_remove_success": "Removed role {} from {}",
        "role_no_permission": "You don't have permission to manage roles!",
        "role_invalid_action": "Action must be either add or remove!",
        "language_set": "تم تعيين اللغة إلى العربية بنجاح!",
        "language_already_set": "اللغة مضبوطة بالفعل على العربية!",
        "language_changed": "تم تغيير اللغة إلى العربية بنجاح!",
        "language_set_english": "Language has been set to English successfully!",
        "language_already_set_english": "Language is already set to English!",
        "language_changed_english": "Language has been changed to English successfully!",
        "select_language": "يرجى اختيار اللغة / Please select a language",
        "arabic": "العربية",
        "english": "English",
        "points_display": "{} has {} points!",
        "rep_success": "Gave a reputation point to {}!",
        "rep_self": "You cannot give reputation to yourself!",
        "server_info_title": "Server Info: {}",
        "user_info_title": "User Info: {}",
        "top_members_title": "Top 10 Members by Points",
        "profile_title": "{}'s Profile",
        "roll_result": "🎲 {} rolled the dice and got: {} (out of {})",
        "8ball_response": "🎱 Question: {}\nAnswer: {}",
        "coinflip_result": "🪙 {} flipped a coin and got: {}",
        "meme_title": "Random Meme",
        "ping_result": "🏓 Ping: {}ms",
        "welcome_message": "Welcome to the server! Please use the `/language` command to choose a language.",
        "channel_restrict_success": "Bot restricted to channel {} successfully!",
        "channel_restrict_remove": "Bot restriction removed from channel {} successfully!",
        "channel_restrict_list": "Channels where bot is allowed: {}",
        "channel_restrict_none": "No channel restrictions, bot works in all channels.",
        "channel_not_allowed": "This bot is not allowed to work in this channel!",
        "slowmode_success": "Set slowmode to {} seconds for this channel!",
        "slowmode_remove": "Slowmode disabled for this channel!",
        "poll_created": "Poll created successfully!",
        "poll_question": "Poll question",
        "suggest_added": "Suggestion added successfully!",
        "tag_created": "Tag '{}' created successfully!",
        "tag_exists": "This tag already exists!",
        "tag_not_found": "Tag '{}' not found!",
        "tag_deleted": "Tag '{}' deleted successfully!",
        "tag_info": "Tag '{}' info: {}",
        "invite_bot": "https://discord.com/oauth2/authorize?client_id={}&scope=bot&permissions=8",
        "trigger_added": "Trigger '{}' added successfully for roles: {}!",
        "trigger_removed": "Trigger '{}' removed successfully!",
        "trigger_exists": "Trigger '{}' already exists!",
        "trigger_not_found": "Trigger '{}' not found!",
        "trigger_list": "Trigger list:\n{}",
        "trigger_no_permission": "You don't have permission to manage triggers!",
        "help_command": """
**🎯 Administrative Commands:**
`/ban` - Ban a member
`/unban` - Unban a member
`/kick` - Kick a member
`/mute` - Mute a member
`/unmute` - Unmute a member
`/warn` - Warn a member
`/clear` - Clear messages
`/setnick` - Change member nickname
`/role` - Manage member roles
`/slowmode` - Set slowmode
`/serverinfo` - Server information
`/userinfo` - User information

**🎪 Entertainment Commands:**
`/roll` - Roll a dice
`/8ball` - Ask the magic ball
`/coinflip` - Flip a coin
`/meme` - Show random meme
`/ping` - Test response speed

**⚙️ Settings Commands:**
`/language` - Change bot language
`/channel_restrict` - Restrict bot to channel
`/channel_unrestrict` - Remove channel restriction
`/channel_list` - Show allowed channels

**🏷️ Tag Commands:**
`/tag_create` - Create a new tag
`/tag` - Show a tag
`/tag_delete` - Delete a tag
`/tag_list` - Show all tags

**📊 Points Commands:**
`/credits` - Show credits
`/rep` - Give reputation
`/rank` - Show rank
`/top` - Top members
`/profile` - Profile

**🔧 Trigger Commands (using !):**
`!addtrigger` - Add a new trigger
`!deltrigger` - Delete a trigger
`!listtriggers` - List all triggers
"""
    }
}

# أنظمة داخلية مع تحسين الأداء [citation:1]
class DatabaseSystem:
    def __init__(self, db_name):
        self.db_name = db_name
        # تحسين استخدام الذاكرة [citation:1]
        self._connection_pool = None
        
    async def _get_connection(self):
        if self._connection_pool is None:
            self._connection_pool = await aiosqlite.connect(
                self.db_name,
                check_same_thread=False,
                cached_statements=100  # تحسين أداء الاستعلامات [citation:1]
            )
        return self._connection_pool
        
    async def init_db(self):
        conn = await self._get_connection()
        
        # جدول إعدادات السيرفر
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'ar',
                welcome_channel_id INTEGER DEFAULT NULL,
                log_channel_id INTEGER DEFAULT NULL
            )
        ''')
        
        # جدول المستخدمين
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                points INTEGER DEFAULT 0,
                reputation INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                warnings INTEGER DEFAULT 0
            )
        ''')
        
        # جدول القنوات المسموحة
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS allowed_channels (
                guild_id INTEGER,
                channel_id INTEGER,
                PRIMARY KEY (guild_id, channel_id)
            )
        ''')
        
        # جدول الأوسمة
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                guild_id INTEGER,
                name TEXT,
                content TEXT,
                PRIMARY KEY (guild_id, name)
            )
        ''')
        
        # جدول الاختصارات (Triggers)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS triggers (
                guild_id INTEGER,
                trigger_word TEXT,
                response TEXT,
                PRIMARY KEY (guild_id, trigger_word)
            )
        ''')
        
        # جدول رتب الاختصارات
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS trigger_roles (
                guild_id INTEGER,
                trigger_word TEXT,
                role_id INTEGER,
                PRIMARY KEY (guild_id, trigger_word, role_id)
            )
        ''')
        
        await conn.commit()
    
    async def get_guild_language(self, guild_id):
        conn = await self._get_connection()
        cursor = await conn.execute('SELECT language FROM guild_settings WHERE guild_id = ?', (guild_id,))
        data = await cursor.fetchone()
        if data:
            return data[0]
        else:
            # إنشاء إعدادات جديدة للسيرفر إذا لم توجد
            await conn.execute('INSERT INTO guild_settings (guild_id, language) VALUES (?, ?)', (guild_id, 'ar'))
            await conn.commit()
            return 'ar'
    
    async def set_guild_language(self, guild_id, language):
        conn = await self._get_connection()
        await conn.execute('UPDATE guild_settings SET language = ? WHERE guild_id = ?', (language, guild_id))
        await conn.commit()
    
    async def get_user_data(self, user_id):
        conn = await self._get_connection()
        cursor = await conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        data = await cursor.fetchone()
        if data:
            return {
                'user_id': data[0],
                'points': data[1],
                'reputation': data[2],
                'level': data[3],
                'warnings': data[4]
            }
        else:
            # إنشاء مستخدم جديد إذا لم يوجد
            await conn.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            await conn.commit()
            return {
                'user_id': user_id,
                'points': 0,
                'reputation': 0,
                'level': 1,
                'warnings': 0
            }
    
    async def add_points(self, user_id, amount):
        conn = await self._get_connection()
        await conn.execute('UPDATE users SET points = points + ? WHERE user_id = ?', (amount, user_id))
        await conn.commit()
    
    async def add_reputation(self, user_id, amount):
        conn = await self._get_connection()
        await conn.execute('UPDATE users SET reputation = reputation + ? WHERE user_id = ?', (amount, user_id))
        await conn.commit()
    
    async def get_allowed_channels(self, guild_id):
        conn = await self._get_connection()
        cursor = await conn.execute('SELECT channel_id FROM allowed_channels WHERE guild_id = ?', (guild_id,))
        channels = await cursor.fetchall()
        return [channel[0] for channel in channels]
    
    async def add_allowed_channel(self, guild_id, channel_id):
        conn = await self._get_connection()
        await conn.execute('INSERT OR IGNORE INTO allowed_channels (guild_id, channel_id) VALUES (?, ?)', (guild_id, channel_id))
        await conn.commit()
    
    async def remove_allowed_channel(self, guild_id, channel_id):
        conn = await self._get_connection()
        await conn.execute('DELETE FROM allowed_channels WHERE guild_id = ? AND channel_id = ?', (guild_id, channel_id))
        await conn.commit()
    
    async def get_tag(self, guild_id, name):
        conn = await self._get_connection()
        cursor = await conn.execute('SELECT content FROM tags WHERE guild_id = ? AND name = ?', (guild_id, name))
        data = await cursor.fetchone()
        return data[0] if data else None
    
    async def set_tag(self, guild_id, name, content):
        conn = await self._get_connection()
        await conn.execute('INSERT OR REPLACE INTO tags (guild_id, name, content) VALUES (?, ?, ?)', (guild_id, name, content))
        await conn.commit()
    
    async def delete_tag(self, guild_id, name):
        conn = await self._get_connection()
        await conn.execute('DELETE FROM tags WHERE guild_id = ? AND name = ?', (guild_id, name))
        await conn.commit()
    
    async def get_all_tags(self, guild_id):
        conn = await self._get_connection()
        cursor = await conn.execute('SELECT name FROM tags WHERE guild_id = ?', (guild_id,))
        tags = await cursor.fetchall()
        return [tag[0] for tag in tags]
    
    # دوال نظام الاختصارات
    async def add_trigger(self, guild_id, trigger_word, response, role_ids):
        conn = await self._get_connection()
        # إضافة الاختصار
        await conn.execute('INSERT INTO triggers (guild_id, trigger_word, response) VALUES (?, ?, ?)', 
                        (guild_id, trigger_word, response))
        
        # إضافة الرتب المسموحة
        for role_id in role_ids:
            await conn.execute('INSERT INTO trigger_roles (guild_id, trigger_word, role_id) VALUES (?, ?, ?)', 
                            (guild_id, trigger_word, role_id))
        
        await conn.commit()
    
    async def remove_trigger(self, guild_id, trigger_word):
        conn = await self._get_connection()
        # حذف الاختصار
        await conn.execute('DELETE FROM triggers WHERE guild_id = ? AND trigger_word = ?', 
                        (guild_id, trigger_word))
        
        # حذف الرتب المرتبطة
        await conn.execute('DELETE FROM trigger_roles WHERE guild_id = ? AND trigger_word = ?', 
                        (guild_id, trigger_word))
        
        await conn.commit()
    
    async def get_trigger(self, guild_id, trigger_word):
        conn = await self._get_connection()
        cursor = await conn.execute('SELECT response FROM triggers WHERE guild_id = ? AND trigger_word = ?', 
                                (guild_id, trigger_word))
        data = await cursor.fetchone()
        return data[0] if data else None
    
    async def get_trigger_roles(self, guild_id, trigger_word):
        conn = await self._get_connection()
        cursor = await conn.execute('SELECT role_id FROM trigger_roles WHERE guild_id = ? AND trigger_word = ?', 
                                (guild_id, trigger_word))
        roles = await cursor.fetchall()
        return [role[0] for role in roles]
    
    async def get_all_triggers(self, guild_id):
        conn = await self._get_connection()
        cursor = await conn.execute('SELECT trigger_word FROM triggers WHERE guild_id = ?', 
                                (guild_id,))
        triggers = await cursor.fetchall()
        return [trigger[0] for trigger in triggers]
    
    async def trigger_exists(self, guild_id, trigger_word):
        conn = await self._get_connection()
        cursor = await conn.execute('SELECT 1 FROM triggers WHERE guild_id = ? AND trigger_word = ?', 
                                (guild_id, trigger_word))
        return await cursor.fetchone() is not None
    
    async def close(self):
        if self._connection_pool:
            await self._connection_pool.close()

# تهيئة نظام قاعدة البيانات
db_system = DatabaseSystem(DB_NAME)

# نظام الاختصارات مع تحسين الأداء [citation:1]
class TriggerSystem:
    def __init__(self):
        self._triggers_cache = {}  # كاش للاختصارات لتحسين الأداء [citation:1]
        
    async def load_triggers(self, guild_id):
        """تحميل الاختصارات للكاش لتحسين الأداء"""
        if guild_id not in self._triggers_cache:
            triggers = await db_system.get_all_triggers(guild_id)
            self._triggers_cache[guild_id] = triggers
        return self._triggers_cache[guild_id]
        
    async def invalidate_cache(self, guild_id):
        """مسح الكاش عند التعديل على الاختصارات"""
        if guild_id in self._triggers_cache:
            del self._triggers_cache[guild_id]

# تهيئة نظام الاختصارات
trigger_system = TriggerSystem()

# أحداث البوت مع تحسين الأداء [citation:1]
@bot.event
async def on_ready():
    print(f'✅ تم تسجيل الدخول كـ {bot.user}')
    await db_system.init_db()
    try:
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أوامر")
    except Exception as e:
        print(f"❌ خطأ في مزامنة الأوامر: {e}")

@bot.event
async def on_guild_join(guild):
    # إرسال رسالة ترحيب عند انضمام البوت إلى سيرفر جديد
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            try:
                # الحصول على لغة السيرفر
                lang = await db_system.get_guild_language(guild.id)
                welcome_msg = translations[lang]["welcome_message"]
                await channel.send(welcome_msg)
            except:
                continue
            break

@bot.event
async def on_interaction(interaction):
    # التحقق من أن البوت مسموح له في هذه القناة
    if not await is_channel_allowed(interaction):
        lang = await db_system.get_guild_language(interaction.guild.id)
        await interaction.response.send_message(translations[lang]["channel_not_allowed"], ephemeral=True)
        return
    await bot.process_application_commands(interaction)

# نظام الاختصارات (Triggers)
@bot.event
async def on_message(message):
    # تجاهل الرسائل من البوت نفسه لتقليل المعالجة [citation:1]
    if message.author == bot.user:
        return
    
    # تجاهل الرسائل في الرسائل الخاصة (DM)
    if not message.guild:
        return
    
    # التحقق من أن البوت مسموح له في هذه القناة
    allowed_channels = await db_system.get_allowed_channels(message.guild.id)
    if allowed_channels and message.channel.id not in allowed_channels:
        return
    
    # التحقق من وجود اختصار في الرسالة باستخدام الكاش [citation:1]
    try:
        triggers = await trigger_system.load_triggers(message.guild.id)
        for trigger in triggers:
            if trigger in message.content:
                # الحصول على رد الاختصار
                response = await db_system.get_trigger(message.guild.id, trigger)
                
                # الحصول على الرتب المسموحة لهذا الاختصار
                allowed_roles = await db_system.get_trigger_roles(message.guild.id, trigger)
                
                # إذا لم يتم تحديد رتب، يرسل الرد للجميع
                if not allowed_roles:
                    await message.channel.send(response)
                    break
                
                # التحقق إذا كان لدى المستخدم أي من الرتب المسموحة
                user_roles = [role.id for role in message.author.roles]
                has_allowed_role = any(role_id in user_roles for role_id in allowed_roles)
                
                if has_allowed_role:
                    await message.channel.send(response)
                    break
    except Exception as e:
        print(f"❌ خطأ في معالجة الاختصارات: {e}")
    
    # معالجة الأوامر العادية (البريفكس)
    await bot.process_commands(message)

# وظيفة للتحقق من صلاحية القناة
async def is_channel_allowed(interaction):
    allowed_channels = await db_system.get_allowed_channels(interaction.guild.id)
    # إذا لم يتم تحديد قنوات مسموحة، يكون البوت فعالاً في جميع القنوات
    if not allowed_channels:
        return True
    # إذا تم تحديد قنوات مسموحة، التحقق من أن الأمر ينفذ في قناة مسموحة
    return interaction.channel.id in allowed_channels

# الأوامر الإدارية
@bot.tree.command(name="ban", description="حظر عضو من السيرفر")
@app_commands.describe(member="العضو المراد حظره", reason="سبب الحظر")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message(translations[lang]["ban_no_permission"], ephemeral=True)
        return
    
    await member.ban(reason=reason)
    await interaction.response.send_message(translations[lang]["ban_success"].format(member.mention, reason))

@bot.tree.command(name="unban", description="رفع الحظر عن عضو")
@app_commands.describe(user_id="الآيدي الخاص بالعضو")
async def unban(interaction: discord.Interaction, user_id: str):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message(translations[lang]["unban_no_permission"], ephemeral=True)
        return
    
    try:
        user_id = int(user_id)
        user = await bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.response.send_message(translations[lang]["unban_success"].format(user.name))
    except (ValueError, discord.NotFound):
        await interaction.response.send_message(translations[lang]["unban_not_found"], ephemeral=True)

@bot.tree.command(name="kick", description="طرد عضو من السيرفر")
@app_commands.describe(member="العضو المراد طرده", reason="سبب الطرد")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message(translations[lang]["kick_no_permission"], ephemeral=True)
        return
    
    await member.kick(reason=reason)
    await interaction.response.send_message(translations[lang]["kick_success"].format(member.mention, reason))

@bot.tree.command(name="mute", description="كتم عضو في القنوات الصوتية أو النصية")
@app_commands.describe(member="العضو المراد كتمه", duration="مدة الكتم (بالدقائق)", reason="سبب الكتم")
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "لا يوجد سبب"):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.mute_members:
        await interaction.response.send_message(translations[lang]["mute_no_permission"], ephemeral=True)
        return
    
    # إنشاء رتبة ميوت إذا لم تكن موجودة
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await interaction.guild.create_role(name="Muted")
        
        # إزالة صلاحيات التحدث من جميع القنوات
        for channel in interaction.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)
    
    await member.add_roles(mute_role, reason=reason)
    await interaction.response.send_message(translations[lang]["mute_success"].format(member.mention, duration, reason))
    
    # إزالة الكتم بعد المدة المحددة
    await asyncio.sleep(duration * 60)
    if mute_role in member.roles:
        await member.remove_roles(mute_role)

@bot.tree.command(name="unmute", description="رفع الكتم عن عضو")
@app_commands.describe(member="العضو المراد رفع الكتم عنه")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.mute_members:
        await interaction.response.send_message(translations[lang]["unmute_no_permission"], ephemeral=True)
        return
    
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if mute_role and mute_role in member.roles:
        await member.remove_roles(mute_role)
        await interaction.response.send_message(translations[lang]["unmute_success"].format(member.mention))
    else:
        await interaction.response.send_message(translations[lang]["unmute_not_muted"], ephemeral=True)

@bot.tree.command(name="warn", description="تحذير عضو")
@app_commands.describe(member="العضو المراد تحذيره", reason="سبب التحذير")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message(translations[lang]["warn_no_permission"], ephemeral=True)
        return
    
    user_data = await db_system.get_user_data(member.id)
    new_warnings = user_data['warnings'] + 1
    
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET warnings = ? WHERE user_id = ?', (new_warnings, member.id))
        await db.commit()
    
    await interaction.response.send_message(translations[lang]["warn_success"].format(member.mention, new_warnings, reason))

@bot.tree.command(name="clear", description="مسح الرسائل في القناة")
@app_commands.describe(amount="عدد الرسائل المراد مسحها")
async def clear(interaction: discord.Interaction, amount: int = 10):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(translations[lang]["clear_no_permission"], ephemeral=True)
        return
    
    if amount > 100:
        await interaction.response.send_message(translations[lang]["clear_too_many"], ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(translations[lang]["clear_success"].format(len(deleted)), ephemeral=True)

@bot.tree.command(name="setnick", description="تغيير لقب عضو")
@app_commands.describe(member="العضو المراد تغيير لقبه", nickname="اللقب الجديد")
async def setnick(interaction: discord.Interaction, member: discord.Member, nickname: str):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.manage_nicknames:
        await interaction.response.send_message(translations[lang]["nick_no_permission"], ephemeral=True)
        return
    
    await member.edit(nick=nickname)
    await interaction.response.send_message(translations[lang]["nick_success"].format(member.mention, nickname))

@bot.tree.command(name="role", description="إضافة أو إزالة دور من عضو")
@app_commands.describe(member="العضو", role="الدور", action="الإجراء (add/remove)")
async def role(interaction: discord.Interaction, member: discord.Member, role: discord.Role, action: str):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message(translations[lang]["role_no_permission"], ephemeral=True)
        return
    
    if action.lower() == "add":
        await member.add_roles(role)
        await interaction.response.send_message(translations[lang]["role_add_success"].format(role.name, member.mention))
    elif action.lower() == "remove":
        await member.remove_roles(role)
        await interaction.response.send_message(translations[lang]["role_remove_success"].format(role.name, member.mention))
    else:
        await interaction.response.send_message(translations[lang]["role_invalid_action"], ephemeral=True)

@bot.tree.command(name="slowmode", description="تعيين وضع بطيء للقناة")
@app_commands.describe(duration="المدة بالثواني (0 لإلغاء الوضع البطيء)")
async def slowmode(interaction: discord.Interaction, duration: int = 10):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("ليس لديك صلاحية لإدارة القنوات!", ephemeral=True)
        return
    
    if duration == 0:
        await interaction.channel.edit(slowmode_delay=0)
        await interaction.response.send_message(translations[lang]["slowmode_remove"])
    else:
        if duration > 21600:  # 6 ساعات الحد الأقصى
            duration = 21600
        await interaction.channel.edit(slowmode_delay=duration)
        await interaction.response.send_message(translations[lang]["slowmode_success"].format(duration))

@bot.tree.command(name="serverinfo", description="عرض معلومات السيرفر")
async def serverinfo(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    guild = interaction.guild
    title = translations[lang]["server_info_title"].format(guild.name)
    embed = discord.Embed(title=title, color=0x00ff00)
    embed.add_field(name="المالك" if lang == "ar" else "Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="عدد الأعضاء" if lang == "ar" else "Members", value=guild.member_count, inline=True)
    embed.add_field(name="عدد القنوات" if lang == "ar" else "Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="عدد الأدوار" if lang == "ar" else "Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="تاريخ الإنشاء" if lang == "ar" else "Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="عرض معلومات المستخدم")
@app_commands.describe(member="العضو (اختياري)")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not member:
        member = interaction.user
    
    user_data = await db_system.get_user_data(member.id)
    title = translations[lang]["user_info_title"].format(member)
    embed = discord.Embed(title=title, color=0x00ff00)
    embed.add_field(name="اسم المستخدم" if lang == "ar" else "Username", value=member.name, inline=True)
    embed.add_field(name="الآيدي" if lang == "ar" else "ID", value=member.id, inline=True)
    embed.add_field(name="تاريخ الانضمام" if lang == "ar" else "Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="تاريخ إنشاء الحساب" if lang == "ar" else "Created At", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="النقاط" if lang == "ar" else "Points", value=user_data['points'], inline=True)
    embed.add_field(name="السمعة" if lang == "ar" else "Reputation", value=user_data['reputation'], inline=True)
    embed.add_field(name="المستوى" if lang == "ar" else "Level", value=user_data['level'], inline=True)
    embed.add_field(name="التحذيرات" if lang == "ar" else "Warnings", value=user_data['warnings'], inline=True)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="credits", description="عرض رصيد النقاط")
@app_commands.describe(member="العضو (اختياري)")
async def credits(interaction: discord.Interaction, member: discord.Member = None):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not member:
        member = interaction.user
    
    user_data = await db_system.get_user_data(member.id)
    await interaction.response.send_message(translations[lang]["points_display"].format(member.mention, user_data['points']))

@bot.tree.command(name="rep", description="منح نقطة سمعة")
@app_commands.describe(member="العضو المراد منحه السمعة")
async def rep(interaction: discord.Interaction, member: discord.Member):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if member.id == interaction.user.id:
        await interaction.response.send_message(translations[lang]["rep_self"], ephemeral=True)
        return
    
    await db_system.add_reputation(member.id, 1)
    await interaction.response.send_message(translations[lang]["rep_success"].format(member.mention))

@bot.tree.command(name="rank", description="عرض رتبة العضو")
@app_commands.describe(member="العضو (اختياري)")
async def rank(interaction: discord.Interaction, member: discord.Member = None):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not member:
        member = interaction.user
    
    user_data = await db_system.get_user_data(member.id)
    level = user_data['level']
    points = user_data['points']
    next_level_points = level * 100
    
    embed = discord.Embed(title=f"رتبة {member}" if lang == "ar" else f"{member}'s Rank", color=0x00ff00)
    embed.add_field(name="المستوى" if lang == "ar" else "Level", value=level, inline=True)
    embed.add_field(name="النقاط" if lang == "ar" else "Points", value=f"{points}/{next_level_points}", inline=True)
    embed.add_field(name="التقدم" if lang == "ar" else "Progress", value=f"{round((points/next_level_points)*100)}%", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="top", description="عرض أفضل الأعضاء حسب النشاط")
async def top(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10')
        top_users = await cursor.fetchall()
    
    title = translations[lang]["top_members_title"]
    embed = discord.Embed(title=title, color=0x00ff00)
    for i, (user_id, points) in enumerate(top_users, 1):
        user = bot.get_user(user_id)
        if user:
            embed.add_field(name=f"{i}. {user.name}", value=f"{points} {'نقطة' if lang == 'ar' else 'points'}", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="profile", description="عرض الملف الشخصي")
@app_commands.describe(member="العضو (اختياري)")
async def profile(interaction: discord.Interaction, member: discord.Member = None):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not member:
        member = interaction.user
    
    user_data = await db_system.get_user_data(member.id)
    title = translations[lang]["profile_title"].format(member)
    embed = discord.Embed(title=title, color=0x00ff00)
    embed.add_field(name="النقاط" if lang == "ar" else "Points", value=user_data['points'], inline=True)
    embed.add_field(name="السمعة" if lang == "ar" else "Reputation", value=user_data['reputation'], inline=True)
    embed.add_field(name="المستوى" if lang == "ar" else "Level", value=user_data['level'], inline=True)
    embed.add_field(name="التحذيرات" if lang == "ar" else "Warnings", value=user_data['warnings'], inline=True)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    await interaction.response.send_message(embed=embed)

# الأوامر الترفيهية
@bot.tree.command(name="roll", description="رمي نرد عشوائي")
@app_commands.describe(sides="عدد أوجه النرد (اختياري)")
async def roll(interaction: discord.Interaction, sides: int = 6):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if sides < 2:
        error_msg = "يجب أن يكون للنرد وجهان على الأقل!" if lang == "ar" else "The dice must have at least two sides!"
        await interaction.response.send_message(error_msg, ephemeral=True)
        return
    
    result = random.randint(1, sides)
    await interaction.response.send_message(translations[lang]["roll_result"].format(interaction.user.mention, result, sides))

@bot.tree.command(name="8ball", description="سؤال الكرة السحرية")
@app_commands.describe(question="السؤال")
async def eight_ball(interaction: discord.Interaction, question: str):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    responses_ar = [
        "نعم بالتأكيد",
        "من المحتمل",
        "أظن ذلك",
        "لا أعتقد",
        "بالطبع لا",
        "حاول مرة أخرى",
        "ليس الآن",
        "لا يمكنني الإجابة الآن",
        "اسأل مرة أخرى لاحقاً",
        "ركز واسأل مرة أخرى"
    ]
    
    responses_en = [
        "Yes, definitely",
        "Most likely",
        "I think so",
        "I don't think so",
        "Of course not",
        "Try again",
        "Not now",
        "I can't answer now",
        "Ask again later",
        "Focus and ask again"
    ]
    
    response = random.choice(responses_ar if lang == "ar" else responses_en)
    await interaction.response.send_message(translations[lang]["8ball_response"].format(question, response))

@bot.tree.command(name="coinflip", description="رمي عملة معدنية")
async def coinflip(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    result = random.choice(["صورة", "كتابة"] if lang == "ar" else ["Heads", "Tails"])
    await interaction.response.send_message(translations[lang]["coinflip_result"].format(interaction.user.mention, result))

@bot.tree.command(name="meme", description="عرض صورة ميم عشوائية")
async def meme(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    memes = [
        "https://i.imgur.com/8x9Zk9j.jpg",
        "https://i.imgur.com/3JQ2q0L.jpg",
        "https://i.imgur.com/5Z0Z0Z0.jpg",
        "https://i.imgur.com/7X8Y9Z0.jpg",
        "https://i.imgur.com/1A2B3C4.jpg"
    ]
    meme_url = random.choice(memes)
    title = translations[lang]["meme_title"]
    embed = discord.Embed(title=title, color=0x00ff00)
    embed.set_image(url=meme_url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="اختبار سرعة الاستجابة")
async def ping(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(translations[lang]["ping_result"].format(latency))

# أمر تحديد اللغة
@bot.tree.command(name="language", description="تحديد لغة البوت")
@app_commands.describe(lang="اللغة (ar/en)")
async def language(interaction: discord.Interaction, lang: str):
    if lang not in ["ar", "en"]:
        await interaction.response.send_message("الرجاء اختيار ar للعربية أو en للإنجليزية / Please choose ar for Arabic or en for English", ephemeral=True)
        return
    
    current_lang = await db_system.get_guild_language(interaction.guild.id)
    
    if lang == current_lang:
        if lang == "ar":
            await interaction.response.send_message(translations[lang]["language_already_set"], ephemeral=True)
        else:
            await interaction.response.send_message(translations[lang]["language_already_set_english"], ephemeral=True)
    else:
        await db_system.set_guild_language(interaction.guild.id, lang)
        if lang == "ar":
            await interaction.response.send_message(translations[lang]["language_changed"])
        else:
            await interaction.response.send_message(translations[lang]["language_changed_english"])

# أوامر إدارة القنوات المسموحة
@bot.tree.command(name="channel_restrict", description="تقييد البوت للقناة الحالية")
async def channel_restrict(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("ليس لديك صلاحية لإدارة القنوات!", ephemeral=True)
        return
    
    await db_system.add_allowed_channel(interaction.guild.id, interaction.channel.id)
    await interaction.response.send_message(translations[lang]["channel_restrict_success"].format(interaction.channel.mention))

@bot.tree.command(name="channel_unrestrict", description="إلغاء تقييد البوت للقناة الحالية")
async def channel_unrestrict(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("ليس لديك صلاحية لإدارة القنوات!", ephemeral=True)
    return

    await db_system.remove_allowed_channel(interaction.guild.id, interaction.channel.id)
    await interaction.response.send_message(translations[lang]["channel_restrict_remove"].format(interaction.channel.mention))

@bot.tree.command(name="channel_list", description="عرض القنوات المسموح للبوت بالعمل فيها")
async def channel_list(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    allowed_channels = await db_system.get_allowed_channels(interaction.guild.id)
    if not allowed_channels:
        await interaction.response.send_message(translations[lang]["channel_restrict_none"])
    else:
        channels = [f"<#{channel_id}>" for channel_id in allowed_channels]
        await interaction.response.send_message(translations[lang]["channel_restrict_list"].format(", ".join(channels)))

# أوامر الأوسمة
@bot.tree.command(name="tag_create", description="إنشاء وسم جديد")
@app_commands.describe(name="اسم الوسم", content="محتوى الوسم")
async def tag_create(interaction: discord.Interaction, name: str, content: str):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    existing_tag = await db_system.get_tag(interaction.guild.id, name)
    if existing_tag:
        await interaction.response.send_message(translations[lang]["tag_exists"], ephemeral=True)
        return
    
    await db_system.set_tag(interaction.guild.id, name, content)
    await interaction.response.send_message(translations[lang]["tag_created"].format(name))

@bot.tree.command(name="tag", description="عرض محتوى الوسم")
@app_commands.describe(name="اسم الوسم")
async def tag(interaction: discord.Interaction, name: str):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    tag_content = await db_system.get_tag(interaction.guild.id, name)
    if not tag_content:
        await interaction.response.send_message(translations[lang]["tag_not_found"].format(name), ephemeral=True)
        return
    
    await interaction.response.send_message(tag_content)

@bot.tree.command(name="tag_delete", description="حذف وسم")
@app_commands.describe(name="اسم الوسم")
async def tag_delete(interaction: discord.Interaction, name: str):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("ليس لديك صلاحية لإدارة الوسوم!", ephemeral=True)
        return
    
    tag_content = await db_system.get_tag(interaction.guild.id, name)
    if not tag_content:
        await interaction.response.send_message(translations[lang]["tag_not_found"].format(name), ephemeral=True)
        return
    
    await db_system.delete_tag(interaction.guild.id, name)
    await interaction.response.send_message(translations[lang]["tag_deleted"].format(name))

@bot.tree.command(name="tag_list", description="عرض قائمة جميع الأوسمة")
async def tag_list(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    tags = await db_system.get_all_tags(interaction.guild.id)
    if not tags:
        await interaction.response.send_message("لا توجد أوسمة في هذا السيرفر!", ephemeral=True)
        return
    
    embed = discord.Embed(title="قائمة الأوسمة", color=0x00ff00)
    embed.description = "\n".join([f"• {tag}" for tag in tags])
    await interaction.response.send_message(embed=embed)

# أوامر إضافية
@bot.tree.command(name="poll", description="إنشاء استفتاء")
@app_commands.describe(question="سؤال الاستفتاء", option1="الخيار الأول", option2="الخيار الثاني")
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    embed = discord.Embed(title=translations[lang]["poll_question"], description=question, color=0x00ff00)
    embed.add_field(name="الخيار 1", value=option1, inline=True)
    embed.add_field(name="الخيار 2", value=option2, inline=True)
    
    message = await interaction.response.send_message(embed=embed)
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")

@bot.tree.command(name="invite", description="الحصول على رابط دعوة البوت")
async def invite(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    invite_url = translations[lang]["invite_bot"].format(bot.user.id)
    await interaction.response.send_message(f"رابط دعوة البوت: {invite_url}")

@bot.tree.command(name="help", description="عرض جميع أوامر البوت")
async def help_command(interaction: discord.Interaction):
    lang = await db_system.get_guild_language(interaction.guild.id)
    
    await interaction.response.send_message(translations[lang]["help_command"])

# أوامر إدارة الاختصارات (باستخدام البريفكس)
@bot.command(name='addtrigger')
async def add_trigger(ctx, trigger_word, *args):
    lang = await db_system.get_guild_language(ctx.guild.id)
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(translations[lang]["trigger_no_permission"])
        return
    
    # فصل الرد والرتب من الوسائط
    response_parts = []
    role_ids = []
    
    for arg in args:
        if arg.startswith('<@&') and arg.endswith('>'):  # تحديد إذا كان الوسيط هو رتبة
            role_id = int(arg[3:-1])
            role_ids.append(role_id)
        else:
            response_parts.append(arg)
    
    response = ' '.join(response_parts)
    
    # التحقق إذا كان الاختصار موجوداً بالفعل
    if await db_system.trigger_exists(ctx.guild.id, trigger_word):
        await ctx.send(translations[lang]["trigger_exists"].format(trigger_word))
        return
    
    # إضافة الاختصار
    await db_system.add_trigger(ctx.guild.id, trigger_word, response, role_ids)
    await trigger_system.invalidate_cache(ctx.guild.id)
    
    # الحصول على أسماء الرتب لعرضها
    role_mentions = []
    for role_id in role_ids:
        role = ctx.guild.get_role(role_id)
        if role:
            role_mentions.append(role.mention)
    
    role_list = ", ".join(role_mentions) if role_mentions else "الجميع"
    
    await ctx.send(translations[lang]["trigger_added"].format(trigger_word, role_list))

@bot.command(name='deltrigger')
async def del_trigger(ctx, trigger_word):
    lang = await db_system.get_guild_language(ctx.guild.id)
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(translations[lang]["trigger_no_permission"])
        return
    
    # التحقق إذا كان الاختصار موجوداً
    if not await db_system.trigger_exists(ctx.guild.id, trigger_word):
        await ctx.send(translations[lang]["trigger_not_found"].format(trigger_word))
        return
    
    # حذف الاختصار
    await db_system.remove_trigger(ctx.guild.id, trigger_word)
    await trigger_system.invalidate_cache(ctx.guild.id)
    await ctx.send(translations[lang]["trigger_removed"].format(trigger_word))

@bot.command(name='listtriggers')
async def list_triggers(ctx):
    lang = await db_system.get_guild_language(ctx.guild.id)
    
    if not ctx.author.guild_permissions.administrator:
        await ctx.send(translations[lang]["trigger_no_permission"])
        return
    
    # الحصول على جميع الاختصارات
    triggers = await db_system.get_all_triggers(ctx.guild.id)
    
    if not triggers:
        await ctx.send("لا توجد اختصارات في هذا السيرفر!")
        return
    
    # الحصول على معلومات كل اختصار
    trigger_list = []
    for trigger in triggers:
        response = await db_system.get_trigger(ctx.guild.id, trigger)
        allowed_roles = await db_system.get_trigger_roles(ctx.guild.id, trigger)
        
        role_mentions = []
        for role_id in allowed_roles:
            role = ctx.guild.get_role(role_id)
            if role:
                role_mentions.append(role.name)
        
        role_list = ", ".join(role_mentions) if role_mentions else "الجميع"
        trigger_list.append(f"**{trigger}** → {response} (مسموح للرتب: {role_list})")
    
    await ctx.send(translations[lang]["trigger_list"].format("\n".join(trigger_list)))

# تشغيل البوت مع معالجة الأخطاء [citation:1]
async def main():
    try:
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            raise ValueError("لم يتم تعيين رمز البوت في متغيرات البيئة!")
        await bot.start(token)
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")
    finally:
        await db_system.close()

if __name__ == "__main__":
    asyncio.run(main())
