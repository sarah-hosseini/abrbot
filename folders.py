import pandas as pd
from telebot import types

class Folder:
    
    def __init__(self, folder_id, user_id, folders_df, saved_msgs_df):
        self.user_id = user_id
        self.folder_id = folder_id
        self.markup = self.init_markup()
        self.msgs = self.find_msgs_inside(saved_msgs_df = saved_msgs_df)
        self.subfolders = self.find_subfolders_and_add_to_markup(folders_df= folders_df)
        

    def init_markup(self):
        markup = types.ReplyKeyboardMarkup(row_width=1)
        btn1 = types.KeyboardButton("/help")
        btn2 = types.KeyboardButton("/back")
        btn3 = types.KeyboardButton("/newfolder")
        markup.add(btn1, btn2, btn3)
        return markup

    def find_subfolders_and_add_to_markup (self, folders_df):
        print('finding subfolders in this folder...')

        subfolders = list(folders_df.loc[folders_df['superfolder_id'] == self.folder_id]['folder_id'])
        for i in subfolders:
            folder_name = folders_df.loc[folders_df['folder_id'] == i, 'folder_name'].values[0]
            btn = types.KeyboardButton('/' + folder_name)
            self.markup.add(btn)
        return subfolders


    def find_msgs_inside (self, saved_msgs_df):
        print('finding messages in folder with id: ' + str(self.folder_id))

        return list(saved_msgs_df.loc[saved_msgs_df['folder_id'] == self.folder_id]['message_id']) 


    async def forward_msgs_inside (self, bot):
        print('sending msgs inside...')

        for i in self.msgs:
            await bot.forward_message(self.user_id, self.user_id, i)
        await bot.send_message(chat_id=self.user_id, text= "choose from menu:", reply_markup= self.markup)

        
    def find_folders_id(folder_name, user_current_folder, folders_df):
        df = folders_df.loc[(folders_df['folder_name'] == folder_name) & (folders_df['superfolder_id'] == user_current_folder)]

        if (df.empty):
            print('invalid folder name')
            return None
        else:
            print('found the folder...returning the id...')
            return df.values[0][1]


    def save_folder_in_dataframe(user_id, superfolder_id, folder_name, folders_df):
        
        temp = folders_df.loc[(folders_df['user_id'] == user_id), 'folder_id'].values
        max_id = max(temp)

        insert_folder = {
            "user_id": user_id,
            "folder_id": max_id + 1,
            "folder_name":folder_name,
            "superfolder_id": superfolder_id
        }
        folders_df = pd.concat([folders_df, pd.DataFrame([insert_folder])])

        # folders_df = folders_df.append({'folder_id':max_id + 1, 'user_id':user_id, 'folder_name':folder_name, 'superfolder_id':superfolder_id})

        folders_df.to_csv('folders.csv', index=False)


    def save_msg_in_dataframe(user_id, folder_id, msg_id, msg_df):

        insert_msg = {
            "message_id":msg_id,
            "user_id": user_id,
            "folder_id": folder_id
        }
        msg_df = pd.concat([msg_df, pd.DataFrame([insert_msg])])

        msg_df.to_csv('saved_messages_data.csv', index=False)