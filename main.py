from ast import Lambda
from operator import truediv
from re import L
from telebot.async_telebot import AsyncTeleBot
import asyncio
from secret import API_KEY
import pandas as pd
from telebot import types
from folders import folder

bot = AsyncTeleBot(API_KEY)
msg_df = pd.read_csv('saved_messages_data.csv')
folders_df = pd.read_csv('folders.csv')
users_df = pd.read_csv('user_data.csv')


async def users_last_directory (msg):
    last_dir_of_user = users_df.loc[users_df['user_id'] == msg.chat.id, 'current_folder_id']
    if (last_dir_of_user.empty):
        print('it''s a new user')
        await welcome_new_user(msg)
        return -1   # for when user is not in db 
    return last_dir_of_user.values[0]

async def welcome_new_user (msg):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton("/help")
    btn2 = types.KeyboardButton("/signup")
    markup.add(btn1, btn2)

    await bot.send_message(chat_id=msg.chat.id, text= "choose from menu:", reply_markup= markup)

@bot.message_handler(commands= ['signup'])
async def signup(msg):
    pass

@bot.message_handler(commands=["start"])
async def show_menu(msg):
    print('id: ' + str(msg.id) + ', from: ' + str(msg.from_user.id) + ', content type: ' + msg.content_type)

    last_directory = await users_last_directory(msg)

    if (last_directory != -1):
        user_saved_msgs = msg_df.loc[msg_df['user_id'] ==  msg.chat.id]
        user_folders = folders_df.loc[folders_df['user_id'] ==  msg.chat.id]

        chosen_folder = folder(last_directory, msg.chat.id, user_folders, user_saved_msgs)
        await chosen_folder.forward_msgs_inside(bot)


@bot.message_handler(commands= ['back'])
async def go_back (msg):
    last_directory = await users_last_directory(msg)

    if (last_directory != -1):
        user_saved_msgs = msg_df.loc[msg_df['user_id'] ==  msg.chat.id]
        user_folders = folders_df.loc[folders_df['user_id'] ==  msg.chat.id]

        temp = user_folders.loc[user_folders['folder_id'] == last_directory, 'superfolder_id']
        if (pd.isna(temp.values[0])):
            superfolder_id = 0
        else:
            superfolder_id = temp.values[0]


        # change the last directory in database here


        #  uncompleted code!!!!!!!!!!!!!!

        chosen_folder = folder(superfolder_id, msg.chat.id, user_folders, user_saved_msgs)
        await chosen_folder.forward_msgs_inside(bot)


@bot.message_handler(commands=['newfolder'])
async def newfolder_maker(msg):
    last_directory = await users_last_directory(msg)

    if (last_directory != -1):
        user_saved_msgs = msg_df.loc[msg_df['user_id'] ==  msg.chat.id]
        user_folders = folders_df.loc[folders_df['user_id'] ==  msg.chat.id]

        temp = user_folders.loc[user_folders['folder_id'] == last_directory, 'folder_name']
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
        
            print(pm.text)
            
            

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
                    # makedir func

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

    


# @bot.message_handler(content_types= ['text', 'file', 'audio', 'photo', 'voice', 'video', 'document', 


async def run():
    await bot.polling(non_stop=True)


asyncio.run(run())