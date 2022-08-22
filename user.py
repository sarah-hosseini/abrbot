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


    def change_last_dir(self, current_folder_id, df):
        self.last_dir_id = current_folder_id

        df.loc[df['user_id'] == self.user_id, 'current_folder_id'] = current_folder_id

        df.to_csv('user_data.csv', index=False)


    def save_user_in_dataframe(user_id, users_df, folders_df):
        
        insert_user = {
            "user_id": user_id,
            "current_folder_id": 0,
        }
        users_df = pd.concat([users_df, pd.DataFrame([insert_user])])
        
        insert_folder = {
            "user_id": user_id,
            "folder_id": 0,
            "folder_name":"main"
        }
        folders_df = pd.concat([folders_df, pd.DataFrame([insert_folder])])


        # users_df = users_df.append({'user_id':user_id, 'current_folder_id':0}, ignore_index=True)
        # folders_df = folders_df.append({'folder_id':0, 'user_id':user_id, 'folder_name':'main'})

        users_df.to_csv('user_data.csv', index=False)
        folders_df.to_csv('folders.csv', index=False)