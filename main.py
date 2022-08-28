from glob import glob
from telebot.async_telebot import AsyncTeleBot
import asyncio
from secret import API_KEY
import pandas as pd
from telebot import types
from folders import Folder
from user import User

bot = AsyncTeleBot(API_KEY)

msg_df = pd.read_csv('saved_messages_data.csv')
folders_df = pd.read_csv('folders.csv')
users_df = pd.read_csv('user_data.csv')



@bot.message_handler(commands= ['signup'])
async def signup(msg):
    # msg_df = load_msgs()
    # folders_df = load_folders()
    # users_df = load_usrs()
        
    global msg_df
    global folders_df
    global users_df

    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)

    if not await user.has_signed_up(bot):
        users_df = User.save_user_in_userdf(user_id= msg.chat.id, users_df= users_df)
        folders_df = User.save_user_in_folderdf(user_id= msg.chat.id, folders_df= folders_df)
        await bot.send_message(chat_id= msg.chat.id, text= 'Happy to have you here\nplease send any message to store in your main folder or send /newfolder to make your space more organized!', reply_markup= types.ReplyKeyboardRemove())
        
    else:
        await bot.send_message(chat_id= msg.chat.id, text= 'you have already signed up. send /start to open your last folder!', reply_markup= types.ReplyKeyboardRemove())
        

@bot.message_handler(commands=["start"])
async def show_menu(msg):
    # msg_df = load_msgs()
    # folders_df = load_folders()
    # users_df = load_usrs()
     
    global msg_df
    global folders_df
    global users_df

    print('id: ' + str(msg.id) + ', from: ' + str(msg.from_user.id) + ', content type: ' + msg.content_type)

    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)

    if await user.has_signed_up(bot):
        chosen_folder = Folder(user.last_dir_id, user.user_id, user.folders, user.saved_msgs)
        msg_df = await chosen_folder.forward_msgs_inside(bot, msg_df)


@bot.message_handler(commands= ['back'])
async def go_back (msg):
    # msg_df = load_msgs()
    # folders_df = load_folders()
    # users_df = load_usrs()
     
    global msg_df
    global folders_df
    global users_df

    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)

    if await user.has_signed_up(bot):
        superfolder_id = user.find_superfolder_of_last_dir()
        
        users_df = user.change_last_dir(current_folder_id= superfolder_id, df= users_df)

        chosen_folder = Folder(superfolder_id, user.user_id, user.folders, user.saved_msgs)
        
        msg_df = await chosen_folder.forward_msgs_inside(bot, msg_df)


@bot.message_handler(commands=['newfolder'])
async def newfolder_maker(msg):
    # msg_df = load_msgs()
    # folders_df = load_folders()
    # users_df = load_usrs()
     
    global msg_df
    global folders_df
    global users_df


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
                                        
                    global msg_df
                    global folders_df
                    global users_df

                    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)
                    
                    print('yes do it')
                    await bot.edit_message_text(text='done!', chat_id= msg.chat.id, message_id= call.message.id,
                    reply_markup=None)
                    folders_df = Folder.save_folder_in_dataframe(user.user_id, user.last_dir_id, call.message.reply_to_message.text, folders_df)
                    print('last_dir_id', user.last_dir_id)
                    

                @bot.callback_query_handler(func=lambda call: call.data == 'fname_not_accepted')
                async def abort_makedir(call):
                                        
                    global msg_df
                    global folders_df
                    global users_df

                    print('no dont do it')
                    await bot.edit_message_text(text='ok!', chat_id= msg.chat.id, message_id= call.message.id,
                    reply_markup=None)   


        @bot.callback_query_handler(func=lambda call: call.data == 'dontmakedir')
        async def handle_dontmakedir(call):
            print('nop')
                        
            global msg_df
            global folders_df
            global users_df

            await bot.edit_message_text(text= 'got it!' , chat_id= msg.chat.id,
            message_id= call.message.id, reply_markup= None)


@bot.message_handler(commands=['delete'], func=lambda m: False if m.reply_to_message is None else True)
async def msg_deleter(msg):
    # msg_df = load_msgs()
    # folders_df = load_folders()
    # users_df = load_usrs()

     
    global msg_df
    global folders_df
    global users_df


    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)

    if await user.has_signed_up(bot):
        
        # print(msg.reply_to_message)
        # print(list(user.saved_msgs['message_id']))

        if (msg.reply_to_message.id in list(user.saved_msgs['message_id'])):
            print ('yes it is a saved one')

            deleted = msg.reply_to_message.id
            btn1 = types.InlineKeyboardButton(text= 'yuppp', callback_data= 'deletemsg' + str(deleted))
            btn2 = types.InlineKeyboardButton(text= 'nvm', callback_data= 'dontdeletemsg')
            keyb = types.InlineKeyboardMarkup(row_width= 2)
            keyb.add(btn1, btn2)
            
            await bot.send_message(chat_id= msg.chat.id, text= 'delete this message?', reply_to_message_id= msg.id, reply_markup= keyb)


            @bot.callback_query_handler(func=lambda call: call.data.startswith('deletemsg'))
            async def handle_deletemsg(call):
                print('deleting')
                                
                global msg_df
                global folders_df
                global users_df

                deleted = int(call.data.split("deletemsg", 1)[1])
                print(deleted)

                await bot.edit_message_text(text='done!', chat_id= msg.chat.id, message_id= call.message.id,
                reply_markup=None)

                msg_df = Folder.delete_msg_in_dataframe(user.user_id, deleted, msg_df)

            @bot.callback_query_handler(func=lambda call: call.data == 'dontdeletemsg')
            async def handle_dontdeletemsg(call):
                print('no dont delete lol jk')
                await bot.edit_message_text(text= 'got it!' , chat_id= msg.chat.id,
                message_id= call.message.id, reply_markup= None)

        else:
            print('not a saved msg')

@bot.message_handler(regexp= '(/).*')
async def folder_opener(msg):
    # msg_df = load_msgs()
    # folders_df = load_folders()
    # users_df = load_usrs()
     
    global msg_df
    global folders_df
    global users_df


    input = msg.text.split("/", 1)[1]
    
    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)

    if await user.has_signed_up(bot):
        folder_id = Folder.find_folders_id(folder_name= input, user_current_folder= user.last_dir_id, folders_df= user.folders)

        if folder_id is not None:
            chosen_folder = Folder(folder_id, user.user_id, user.folders, user.saved_msgs)
            msg_df = await chosen_folder.forward_msgs_inside(bot, msg_df)
            users_df = user.change_last_dir(folder_id, users_df)


@bot.message_handler(func=lambda m: True if m.reply_to_message is None else m.reply_to_message.text != 'reply to this message with the folder name.', content_types= ['text', 'sticker', 'gif', 'file', 'audio', 'photo', 
'voice', 'video', 'document', 'animation'])
async def save_message(msg):
    # msg_df = load_msgs()
    # folders_df = load_folders()
    # users_df = load_usrs()
     
    global msg_df
    global folders_df
    global users_df


    print('save msg func')
    user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)
    
    print('saving msg...', msg.text)

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
                        
            global msg_df
            global folders_df
            global users_df

            print('saving msg...', call.message.reply_to_message.text)
            await bot.edit_message_text(text='sure!', chat_id= msg.chat.id, message_id= call.message.id, reply_markup= None)
            user = User(user_id= msg.chat.id, users_df= users_df, folders_df= folders_df, msg_df= msg_df)
            print(user.user_id, user.last_dir_id, call.message.reply_to_message.id, '\n')
            msg_df = Folder.save_msg_in_dataframe(user.user_id, user.last_dir_id, call.message.reply_to_message.id, msg_df)
            user.saved_msgs = user.find_users_msgs(msg_df)
        
        @bot.callback_query_handler(func=lambda call: call.data == 'dontsaveit')
        async def handle_dontsave(call):
            print('abort saving...')
            await bot.edit_message_text(text='save cancelled', chat_id= msg.chat.id, message_id= call.message.id, reply_markup= None)
    

async def run():
    await bot.polling(non_stop=True)


asyncio.run(run())