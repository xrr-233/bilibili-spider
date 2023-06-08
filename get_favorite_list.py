import asyncio
import json
import logging
import os
import time

from bilibili_api import Credential
from bilibili_api.exceptions import ResponseCodeException
from bilibili_api.video import Video
from login_gui import login_gui
from bilibili_api.user import get_toview_list, User
from bilibili_api.favorite_list import get_video_favorite_list, FavoriteList


class MyFavoriteList(FavoriteList):
    def __init__(self, media_id, credential):
        super().__init__(media_id=media_id, credential=credential)
        self.path = None
        self.info = None
        self.videos = []

    def set_path(self, path):
        self.path = path

    async def fetch_info(self):
        self.info = await self.get_info()

    async def fetch_video_info(self):
        favorite_list_info = await self.get_content_ids_info()
        for video_json in favorite_list_info:
            MyVideo.write_my_video_json(self.path, video_json)

    # async def pull_video_info(self, debug=False):
    #     for video_json in favorite_list_info:
    #         video = MyVideo(bvid=video_json['bvid'], credential=self.credential)
    #         await video.pull_info()
    #         if debug:
    #             video.debug_info_title()
    #         self.videos.append(video)


class MyToViewList():
    def __init__(self, credential):
        self.path = None
        self.credential = credential if credential else Credential()
        self.videos = []

    def set_path(self, path):
        self.path = path

    async def fetch_video_info(self):
        toview_list = await get_toview_list(self.credential)
        for video_json in toview_list['list']:
            MyVideo.write_my_video_json(self.path, video_json)

    # async def pull_video_info(self, debug=False):
    #     for video_json in toview_list['list']:
    #         video = MyVideo(video_json['bvid'], self.credential)
    #         await video.pull_info()
    #         if debug:
    #             video.debug_info_title()
    #         self.videos.append(video)


class MyVideo(Video):
    def __init__(self, bvid, credential):
        super().__init__(bvid=bvid, credential=credential)
        self.last_modified = None
        self.status = None
        self.info = None

    @staticmethod
    def write_my_video_json(path, info):
        last_modified = int(time.time())
        status = 'fetched'
        json_dict = {
            'last_modified': last_modified,
            'status': status,
            'info': info
        }
        with open(os.path.join(path, f"{info['bvid']}.json"), "w", encoding="utf-8") as f:
            json.dump(json_dict, f, indent=4, ensure_ascii=False)
            # 时间戳以内无需更新

    async def pull_info(self):
        try:
            self.info = await self.get_info()
            self.status = 'pulled'
        except ResponseCodeException as e:
            self.info = e.raw
            if e.code == -412:
                self.status = 'blocked'
            elif e.code == -404:
                self.status = 'banned'

    def debug_info_title(self):
        if self.status == 'pulled':
            print(self.info['title'])
        elif self.status == 'fetched':
            logging.warning('尚未获取视频具体信息，请执行pull')
        else:
            logging.warning(self.info['message'])


async def get_favorite_list():
    credential = await login_gui()
    user = User(credential.dedeuserid, credential)

    user_root = f'./data/user/{user.get_uid()}'
    os.makedirs(user_root, exist_ok=True)
    os.makedirs(os.path.join(user_root, 'favorite'), exist_ok=True)
    os.makedirs(os.path.join(user_root, 'toview'), exist_ok=True)

    favorite_lists_json = await get_video_favorite_list(user.get_uid(), credential=credential)
    favorite_lists = []
    for favorite_list_json in favorite_lists_json['list']:
        favorite_list = MyFavoriteList(media_id=favorite_list_json['id'], credential=credential)
        favorite_list.set_path(os.path.join(user_root, 'favorite', str(favorite_list.get_media_id())))
        os.makedirs(favorite_list.path, exist_ok=True)
        await favorite_list.fetch_info()
        print(f"***{favorite_list.info['title']}***")
        await favorite_list.fetch_video_info()
        # await favorite_list.pull_video_info(debug=True)
        favorite_lists.append(favorite_list)

    toview_list = MyToViewList(credential)
    toview_list.set_path(os.path.join(user_root, 'toview'))
    print("***稍后再看***")
    await toview_list.fetch_video_info()
    # await toview_list.pull_video_info(debug=True)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(get_favorite_list())
