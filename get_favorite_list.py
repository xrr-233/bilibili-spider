import asyncio
import logging

from bilibili_api import Credential
from bilibili_api.exceptions import ResponseCodeException
from bilibili_api.video import Video
from login_gui import login_gui
from bilibili_api.user import get_toview_list, User
from bilibili_api.favorite_list import get_video_favorite_list, FavoriteList


class MyFavoriteList(FavoriteList):
    def __init__(self, media_id, credential):
        super().__init__(media_id=media_id, credential=credential)
        self.info = None
        self.videos = []

    async def my_get_info(self):
        self.info = await self.get_info()

    async def my_get_video_info(self, debug=False):
        favorite_list_info = await self.get_content_ids_info()
        for video_json in favorite_list_info:
            video = MyVideo(bvid=video_json['bvid'], credential=self.credential)
            await video.my_get_info()
            if debug:
                video.my_get_title()
            self.videos.append(video)

    def my_get_video_title(self):
        for video in self.videos:
            video.my_get_title()


class MyToViewList():
    def __init__(self, credential):
        self.credential = credential if credential else Credential()
        self.videos = []

    async def my_get_video_info(self, debug=False):
        toview_list = await get_toview_list(self.credential)
        for video_json in toview_list['list']:
            video = MyVideo(video_json['bvid'], self.credential)
            await video.my_get_info()
            if debug:
                video.my_get_title()
            self.videos.append(video)


class MyVideo(Video):
    def __init__(self, bvid, credential):
        super().__init__(bvid=bvid, credential=credential)
        self.info = None
        self.is_disappeared = False
    
    async def my_get_info(self):
        try:
            self.info = await self.get_info()
        except ResponseCodeException:
            self.is_disappeared = True

    def my_get_title(self):
        if self.is_disappeared:
            logging.warning('这个视频被ban了 ToT')
        else:
            print(self.info['title'])


async def get_favorite_list():
    credential = await login_gui()
    user = User(credential.dedeuserid, credential)
    favorite_lists_json = await get_video_favorite_list(user.get_uid(), credential=credential)
    favorite_lists = []
    for favorite_list_json in favorite_lists_json['list']:
        favorite_list = MyFavoriteList(media_id=favorite_list_json['id'], credential=credential)
        await favorite_list.my_get_info()
        print(f"***{favorite_list.info['title']}***")
        await favorite_list.my_get_video_info(debug=True)
        favorite_list.my_get_video_title()
        favorite_lists.append(favorite_list)
    toview_list = MyToViewList(credential)
    print("***稍后再看***")
    await toview_list.my_get_video_info(debug=True)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(get_favorite_list())
