from telebot.async_telebot import AsyncTeleBot
import asyncio
from secret import API_KEY
import pandas as pd
from telebot import types
from folders import Folder
from user import User

bot = AsyncTeleBot(API_KEY)
global msg_df
global folders_df
global users_df

def load_info():
    global msg_df
    global folders_df
    global users_df
    msg_df = pd.read_csv('saved_messages_data.csv')
    folders_df = pd.read_csv('folders.csv')
    users_df = pd.read_csv('user_data.csv')

def del_info():
    global msg_df
    global folders_df
    global users_df
    del msg_df
    del folders_df 
    del users_df 


@bot.message_handler(commands= ['signup'])
async def signup(msg):
    load_info()
    await bot.send_message(chat_id= msg.chat.id, text= 'Happy to have you here\nplease send any message to store in your main folder or send /newfolder to make your space more organized!')
    User.save_user_in_dataframe(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df)
    del_info()

@bot.message_handler(commands=["start"])
async def show_menu(msg):
    load_info()
    print('id: ' + str(msg.id) + ', from: ' + str(msg.from_user.id) + ', content type: ' + msg.content_type)

    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)

    if await user.has_signed_up(bot):
        chosen_folder = Folder(user.last_dir_id, user.user_id, user.folders, user.saved_msgs)
        await chosen_folder.forward_msgs_inside(bot)
    del_info()

@bot.message_handler(commands= ['back'])
async def go_back (msg):
    load_info()
    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)

    if await user.has_signed_up(bot):
        temp = user.folders.loc[user.folders['folder_id'] == user.last_dir_id, 'superfolder_id']
        if (pd.isna(temp.values[0])):
            superfolder_id = 0
        else:
            superfolder_id = temp.values[0]

        
        user.change_last_dir(current_folder_id= superfolder_id, df= users_df)

        chosen_folder = Folder(superfolder_id, user.user_id, user.folders, user.saved_msgs)
        await chosen_folder.forward_msgs_inside(bot)
    del_info()

@bot.message_handler(commands=['newfolder'])
async def newfolder_maker(msg):
    load_info()
    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)

    if await user.has_signed_up(bot):
        temp = user.folders.loc[user.folders['folder_id'] == user.last_dir_id, 'folder_name']
        folder_name = temp.values[0]
        btn1 = types.InlineKeyboardButton(text= 'yes', callback_data= 'makedir')
        btn2 = types.InlineKeyboardButton(text= 'no', callback_data= 'dontmakedir')
        keyb = types.InlineKeyboardMarkup(row_width= 2)
        keyb.add(btn1, btn2)
        await bot.send_message(chat_id=msg.chat.id, text= 'make a folder inside the folder ' + folder_name + '?',
        reply_markup= keyb, reply_to_message_id=msg.id)
    
        @bot.callback_query_handler(func=lambda call: call.data == 'makedir')
        async def handle_makedir(call):
            print('yes')
            await bot.edit_message_text(text='cool!', chat_id= msg.chat.id, message_id= call.message.id, reply_markup= None)
            pm = await bot.send_message(text='reply to this message with the folder name.', chat_id= msg.chat.id, reply_markup= types.ForceReply(input_field_placeholder= 'folder name? :)'))
        

            @bot.message_handler(func=lambda m: False if m.reply_to_message is None else m.reply_to_message.id == pm.id)
            async def get_foldername(m):
                print('here in get folder name')
                b1 = types.InlineKeyboardButton(text= 'yes', callback_data= 'fname_is_accepted')
                b2 = types.InlineKeyboardButton(text= 'no', callback_data= 'fname_not_accepted')
                accept_name = types.InlineKeyboardMarkup(row_width= 2)
                accept_name.add(b1, b2)
                
                await bot.send_message(chat_id=m.chat.id, text='make a folder called ' + m.text + '?',
                reply_markup= accept_name, reply_to_message_id=m.id)

            
                @bot.callback_query_handler(func=lambda call: call.data == 'fname_is_accepted')
                async def makedir(call):
                    print('yes do it')
                    await bot.edit_message_text(text='done!', chat_id= msg.chat.id, message_id= call.message.id,
                    reply_markup=None)
                    Folder.save_folder_in_dataframe(user.user_id, user.last_dir_id, m.text, folders_df)

                @bot.callback_query_handler(func=lambda call: call.data == 'fname_not_accepted')
                async def abort_makedir(call):
                    print('no dont do it')
                    await bot.edit_message_text(text='ok!', chat_id= msg.chat.id, message_id= call.message.id,
                    reply_markup=None)    


        @bot.callback_query_handler(func=lambda call: call.data == 'dontmakedir')
        async def handle_dontmakedir(call):
            print('nop')
            await bot.edit_message_text(text= 'got it!' , chat_id= msg.chat.id,
            message_id= call.message.id, reply_markup= None)
    del_info()

@bot.message_handler(regexp= '(/).*')
async def folder_opener(msg):
    load_info()
    input = msg.text.split("/", 1)[1]
    
    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)

    if await user.has_signed_up(bot):
        folder_id = Folder.find_folders_id(folder_name= input, user_current_folder= user.last_dir_id, folders_df= user.folders)

        if folder_id is not None:
            chosen_folder = Folder(folder_id, user.user_id, user.folders, user.saved_msgs)
            await chosen_folder.forward_msgs_inside(bot)
            user.change_last_dir(folder_id, users_df)
    del_info()

@bot.message_handler(func=lambda m: True if m.reply_to_message is None else m.reply_to_message.text != 'reply to this message with the folder name.', content_types= ['text', 'file', 'audio', 'photo', 'voice', 'video', 'document'])
async def save_message(msg):
    load_info()
    print('save msg func')
    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)
    
    if await user.has_signed_up(bot):
        last_folder_opened = user.folders.loc[user.folders['folder_id'] == user.last_dir_id, 'folder_name'].values[0]
        
        key1 = types.InlineKeyboardButton(text= 'yes', callback_data= 'savemsg')
        key2 = types.InlineKeyboardButton(text= 'no', callback_data= 'dontsaveit')
        keyboard = types.InlineKeyboardMarkup(row_width= 2)
        keyboard.add(key1, key2)
        await bot.send_message(chat_id= user.user_id, text= 'do you wish to save this message inside folder ' + last_folder_opened,
        reply_markup= keyboard, reply_to_message_id=msg.id)
    
        @bot.callback_query_handler(func=lambda call: call.data == 'savemsg')
        async def handle_savemsg(call):
            print('saving msg...')
            await bot.edit_message_text(text='sure!', chat_id= msg.chat.id, message_id= call.message.id, reply_markup= None)
            Folder.save_msg_in_dataframe(user.user_id, user.last_dir_id, msg.id, msg_df)
        
        @bot.callback_query_handler(func=lambda call: call.data == 'dontsaveit')
        async def handle_dontsave(call):
            print('abort saving...')
            await bot.edit_message_text(text='save cancelled', chat_id= msg.chat.id, message_id= call.message.id, reply_markup= None)
    del_info()


async def run():
    await bot.polling(non_stop=True)


asyncio.run(run())