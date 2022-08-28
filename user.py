from telebot import types
import pandas as pd

class User:
    
    def __init__(self, user_id, users_df, folders_df, msg_df):
        self.user_id = user_id
        self.last_dir_id = self.users_last_directory(chat_id= user_id, users_df= users_df)
        if (self.last_dir_id is not None):
            self.saved_msgs = self.find_users_msgs(msg_df= msg_df)
            self.folders = self.find_users_folders(folders_df= folders_df)
        else:
            self.saved_msgs = None
            self.folders = None


    def users_last_directory (self, chat_id, users_df):
        last_dir_of_user = users_df.loc[users_df['user_id'] == chat_id, 'current_folder_id']
        if (last_dir_of_user.empty):
            print('it''s a new user')
            return None   # for when user is not in db 
        return last_dir_of_user.values[0] 


    async def has_signed_up(self, bot):
        if self.last_dir_id is not None:
            return True
        await self.welcome_new_user(bot)
        return False


    async def welcome_new_user (self, bot):
        markup = types.ReplyKeyboardMarkup(row_width=2)
        btn1 = types.KeyboardButton("/help")
        btn2 = types.KeyboardButton("/signup")
        markup.add(btn1, btn2)
        await bot.send_message(chat_id=self.user_id, text= "choose from menu:", reply_markup= markup)
   

    def find_users_msgs(self, msg_df):
        return msg_df.loc[msg_df['user_id'] ==  self.user_id]


    def find_users_folders(self, folders_df):
        return folders_df.loc[folders_df['user_id'] ==  self.user_id]

    def find_superfolder_of_last_dir(self):
        print('let''s search for the current folder of user. it''s ')
        print(self.last_dir_id)
        temp = self.folders.loc[self.folders['folder_id'] == self.last_dir_id, 'superfolder_id']
        if (pd.isna(temp.values[0])):
            superfolder_id = 0
        else:
            superfolder_id = temp.values[0]
        return superfolder_id


    def change_last_dir(self, current_folder_id, df):
        self.last_dir_id = current_folder_id

        df.loc[df['user_id'] == self.user_id, 'current_folder_id'] = current_folder_id

        df.to_csv('user_data.csv', index=False)
        return df


    def save_user_in_userdf(user_id, users_df):
        
        insert_user = {
            "user_id": user_id,
            "current_folder_id": 0,
        }
        users_df = pd.concat([users_df, pd.DataFrame([insert_user])])
        
        users_df.to_csv('user_data.csv', index=False)
        return users_df

    def save_user_in_folderdf(user_id, folders_df):
        
        insert_folder = {
            "user_id": user_id,
            "folder_id": 0,
            "folder_name":"main"
        }
        folders_df = pd.concat([folders_df, pd.DataFrame([insert_folder])])

        folders_df.to_csv('folders.csv', index=False)
        return folders_df

    
    def delete_user_in_folderdf(user, folders_df):

        folders_df.drop(folders_df[folders_df.user_id == user.user_id].index, inplace=True)
        folders_df.to_csv('folders.csv', index=False)
        return folders_df


    def delete_user_in_userdf(user, user_df):

        user_df.drop(user_df[user_df.user_id == user.user_id].index, inplace=True)

        user_df.to_csv('user_data.csv', index=False)
        return user_df


    def delete_user_in_msgdf(user, msg_df):

        msg_df.drop(msg_df[msg_df.user_id == user.user_id].index, inplace=True)

        msg_df.to_csv('saved_messages_data.csv', index=False)
        return msg_df