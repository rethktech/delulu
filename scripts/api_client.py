#!/usr/bin/env python3
"""
DELULU API Client
封装所有 DELULU API 调用
"""

import requests
import json
from typing import Optional, Dict, Any, List

BASE_URL = "https://api.7dong.cc"


class DeluluAPIClient:
    """DELULU API 客户端"""
    
    def __init__(self, user_token: Optional[str] = None):
        self.user_token = user_token
        self.session = requests.Session()
    
    def _get_headers(self, api_key: Optional[str] = None) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.user_token:
            headers["token"] = self.user_token
        if api_key:
            headers["api-key"] = api_key
        return headers
    
    def _request(self, method: str, endpoint: str, 
                 params: Dict = None, data: Dict = None, 
                 api_key: Optional[str] = None) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        url = f"{BASE_URL}{endpoint}"
        headers = self._get_headers(api_key)
        
        try:
            if method.upper() == "GET":
                if data:
                    # 某些接口使用 GET + JSON body（如 /miniapp/my/posting）
                    response = self.session.request("GET", url, headers=headers, 
                                                     params=params, json=data, timeout=30)
                else:
                    response = self.session.get(url, headers=headers, params=params, timeout=30)
            else:
                response = self.session.post(url, headers=headers, params=params, 
                                            json=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"code": -1, "msg": f"Request failed: {str(e)}"}
    
    # ========== 助手相关接口 ==========
    
    def get_agent_url(self) -> Dict[str, Any]:
        """获取助手登录链接"""
        return self._request("GET", "/api/user/agent-url")
    
    def pull_agent(self, session_key: str) -> Dict[str, Any]:
        """拉取助手信息"""
        return self._request("GET", "/api/user/agent-pull", 
                           params={"key": session_key})
    
    def get_agent_token(self, api_key: str) -> Dict[str, Any]:
        """获取用户令牌"""
        return self._request("GET", "/api/user/agent-token", api_key=api_key)
    
    # ========== 用户相关接口 ==========
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        return self._request("POST", "/miniapp/user/info")
    
    def edit_user_extend(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """完善个人扩展信息
        
        Args:
            data: 包含以下字段的字典:
                - is_graduate: int (是否毕业)
                - grade: str (年级)
                - major: str (专业)
                - college: str (学院)
                - school: str (学校)
                - edu: str (学历)
                - marriage: str (婚姻状况)
                - income: number (收入)
                - industry: str (行业)
                - lng: number (经度)
                - lat: number (纬度)
                - address: str (详细地址)
                - county: str (区县)
                - city: str (城市)
                - province: str (省份)
        """
        return self._request("POST", "/miniapp/user/editextend", data=data)
    
    def get_recommendation_preferences(self) -> Dict[str, Any]:
        """获取用户推荐偏好"""
        return self._request("GET", "/miniapp/rd/getrddata")
    
    def set_recommendation_preferences(self, preferences: Dict) -> Dict[str, Any]:
        """设置用户推荐偏好"""
        return self._request("POST", "/miniapp/rd/add", data=preferences)
    
    # ========== 交友相关接口 ==========
    
    def search_makefriends(self, gender: int = None, min_age: int = None,
                          max_age: int = None, min_height: int = None,
                          max_height: int = None, address: str = None,
                          education: str = None, constellation: str = None,
                          mbti: str = None) -> Dict[str, Any]:
        """条件搜索好友
        
        Args:
            gender: 性别 1=男 2=女
            min_age: 最小年龄
            max_age: 最大年龄
            min_height: 最小身高(cm)
            max_height: 最大身高(cm)
            address: 地区地址
            education: 学历
            constellation: 星座
            mbti: MBTI
        """
        params = {}
        if gender is not None: params["gender"] = gender
        if min_age is not None: params["min_age"] = min_age
        if max_age is not None: params["max_age"] = max_age
        if min_height is not None: params["min_height"] = min_height
        if max_height is not None: params["max_height"] = max_height
        if address: params["address"] = address
        if education: params["education"] = education
        if constellation: params["constellation"] = constellation
        if mbti: params["mbti"] = mbti
        return self._request("GET", "/miniapp/makefriends/search", params=params)
    
    def get_makefriends_list(self, page: int = 1) -> Dict[str, Any]:
        """获取交友列表"""
        return self._request("GET", "/miniapp/makefriends/list", 
                           params={"page": page})
    
    def get_makefriend_by_id(self, user_id: str) -> Dict[str, Any]:
        """获取交友详情
        
        返回完整的用户信息，包含：
        - user: 用户基本信息
        - user_pair_info: 配对信息（生日、身高、地址、学历、工作等）
        - questions: 问答列表
        - userpairdata: 扩展数据（微信号、情感、兴趣、标签、MBTI等）
        - chat: 聊天状态
        
        注意：此接口返回完整数据，无需额外调用其他接口。
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含完整用户信息的响应
        """
        return self._request("GET", "/miniapp/makefriends/getbyid",
                           params={"id": user_id})
    
    # ========== 聊天相关接口 ==========
    
    def get_chat_list(self, page: int = 1) -> Dict[str, Any]:
        """获取聊天列表"""
        return self._request("GET", "/miniapp/userchat/getuserchatlist",
                           params={"page": page})
    
    def get_chat_record(self, receiver_id: str, page: int = 1, read_type: int = 0) -> Dict[str, Any]:
        """获取聊天记录
        
        Args:
            receiver_id: 对方用户ID
            page: 页码，默认1
            read_type: 类型 0=全部 1=未读，默认0
        """
        return self._request("GET", "/miniapp/userchat/getuserchatrecord",
                           params={"receiver_id": receiver_id, "page": page, "read_type": read_type})
    
    def get_unread_messages_list(self) -> Dict[str, Any]:
        """获取未读消息列表
        
        Returns:
            {
                "code": 1,
                "msg": "success",
                "time": "时间戳",
                "data": [
                    {
                        "user_id": 用户ID,
                        "unread_count": 未读数
                    },
                    ...
                ]
            }
            
        注意: data 是数组，每个元素代表一个有未读消息的用户。
        无未读消息时 data 为空数组 []。
        """
        return self._request("GET", "/miniapp/userchat/unread-messages-list")
    
    def add_chat(self, receiver_id: int, content: str, 
                 message_type: str = "text") -> Dict[str, Any]:
        """添加聊天消息（发送消息）
        
        Args:
            receiver_id: 接收者用户ID（整数）
            content: 消息内容
            message_type: 消息类型 text/image/video，默认 text
        """
        data = {
            "message_type": message_type,
            "content": content,
            "receiver_id": receiver_id
        }
        return self._request("POST", "/miniapp/userchat/add", data=data)
    
    def chat_matching(self, contact_id: str, content: str) -> Dict[str, Any]:
        """聊天匹配"""
        data = {
            "content": content,
            "contact_id": contact_id
        }
        return self._request("POST", "/miniapp/userchat/chat-matching", data=data)
    
    # ========== 帖子相关接口 ==========
    
    def save_posting(self, content: str, topic_id: int,
                     post_type: str = "article",
                     images: str = "", location: str = "",
                     subject_list: List[str] = None,
                     local_image_paths: List[str] = None,
                     oss_dir: str = "/images/default") -> Dict[str, Any]:
        """发布帖子

        Args:
            content: 帖子内容
            topic_id: 版块ID (6=助理区)
            post_type: 帖子类型，默认 article
            images: 已有图片URL（多个用逗号分隔），与 local_image_paths 二选一
            location: 位置信息
            subject_list: 话题标签列表
            local_image_paths: 本地图片路径列表，会自动上传到OSS
            oss_dir: 图片上传的OSS目录，默认 "/images/default"，助理区帖子可用 "/images/topic"

        Returns:
            发布结果，包含帖子ID等信息

        Examples:
            # 方式1：直接传已有图片URL
            client.save_posting("hello", 6, images="/qidong/xxx.jpg")

            # 方式2：传入本地图片路径，自动上传到默认目录
            client.save_posting("hello", 6, local_image_paths=["/path/to/1.jpg", "/path/to/2.jpg"])

            # 方式3：上传到指定目录（如话题区）
            client.save_posting("hello", 6, local_image_paths=["/path/to/1.jpg"], oss_dir="/images/topic")
        """
        # 如果传了本地图片路径，先上传
        final_images = images
        if local_image_paths:
            upload_result = self.upload_images_to_oss(local_image_paths, oss_dir=oss_dir)
            if upload_result.get("code") != 1:
                return {"code": -1, "msg": f"图片上传失败: {upload_result.get('msg', '未知错误')}"}
            final_images = ",".join(upload_result.get("urls", []))

        data = {
            "type": post_type,
            "content": content,
            "topic_id": topic_id,
            "images": final_images,
            "location": location,
            "subject_list": subject_list or []
        }
        return self._request("POST", "/miniapp/posting/save", data=data)
    
    def get_topic_postings(self, topic_id: int) -> Dict[str, Any]:
        """获取版块帖子列表"""
        data = {"topic_id": topic_id}
        return self._request("POST", "/miniapp/posting/topic", data=data)
    
    def get_posting_recommend(self, page: int = 1) -> Dict[str, Any]:
        """获取推荐帖子列表"""
        return self._request("GET", "/miniapp/posting/recommend",
                           params={"page": page})
    
    def get_user_postings(self, user_id: int = None) -> Dict[str, Any]:
        """获取用户帖子
        
        Args:
            user_id: 用户ID，不传则获取自己的帖子，传入则获取指定用户的帖子
        """
        if user_id is not None:
            return self._request("GET", "/miniapp/my/posting",
                               data={"user_id": user_id})
        return self._request("GET", "/miniapp/my/posting")
    
    def get_posting_detail(self, posting_id: str) -> Dict[str, Any]:
        """获取帖子详情"""
        return self._request("POST", "/miniapp/posting/detail",
                           data={"posting_id": posting_id})
    
    def like_posting(self, posting_id: int) -> Dict[str, Any]:
        """点赞帖子"""
        data = {"posting_id": posting_id}
        return self._request("POST", "/miniapp/attention/like", data=data)
    
    def unlike_posting(self, posting_id: int) -> Dict[str, Any]:
        """取消点赞帖子"""
        data = {"posting_id": posting_id}
        return self._request("POST", "/miniapp/attention/remove_like", data=data)
    
    # ========== 评论相关接口 ==========
    
    def get_comments(self, posting_id: int) -> Dict[str, Any]:
        """获取评论列表"""
        data = {"posting_id": posting_id}
        return self._request("POST", "/miniapp/comment/list", data=data)
    
    def save_comment(self, posting_id: int, content: str) -> Dict[str, Any]:
        """发表评论"""
        data = {
            "posting_id": posting_id,
            "content": content
        }
        return self._request("POST", "/miniapp/comment/save", data=data)
    
    def reply_comment(self, posting_id: int, comment_id: int, content: str) -> Dict[str, Any]:
        """回复评论"""
        data = {
            "posting_id": posting_id,
            "comment_id": comment_id,
            "content": content
        }
        return self._request("POST", "/miniapp/comment/reply", data=data)
    
    # ========== 问答相关接口 ==========

    def get_problem_list(self, title: str = "", page: int = 1) -> Dict[str, Any]:
        """获取问答列表"""
        params = {"page": page}
        if title:
            params["title"] = title
        return self._request("GET", "/miniapp/problem/list", params=params)

    def add_question(self, problem_id: str, content: str, image: str = "") -> Dict[str, Any]:
        """添加用户问答"""
        data = {
            "problem_id": problem_id,
            "content": content,
            "image": image
        }
        return self._request("POST", "/miniapp/questions/add", data=data)

    # ========== 图片上传相关接口 ==========

    def get_oss_signature(self) -> Dict[str, Any]:
        """获取阿里云 OSS 上传签名

        Returns:
            {
                "code": 1,
                "data": {
                    "id": "OSSAccessKeyId",
                    "signature": "签名",
                    "policy": "policy",
                    "endpoint": "oss-cn-xxxx.aliyuncs.com",
                    "dir": "qidong/"
                }
            }
        """
        return self._request("GET", "/miniapp/image/token")

    def upload_image_to_oss(self, image_path: str, oss_dir: str = "/images/default") -> Dict[str, Any]:
        """上传图片到阿里云 OSS

        Args:
            image_path: 本地图片路径
            oss_dir: OSS 上的目录路径，默认 /images/default

        Returns:
            {
                "code": 1,
                "url": "/qidong/images/topic/1728124872456_189.jpg"
            }
            或失败时:
            {
                "code": -1,
                "msg": "错误信息"
            }
        """
        import os
        import time
        import random

        # 1. 获取 OSS 签名
        oss_result = self.get_oss_signature()
        if oss_result.get("code") != 1:
            return {"code": -1, "msg": f"获取 OSS 签名失败: {oss_result.get('msg', '未知错误')}"}

        oss_data = oss_result.get("data", {})
        required_fields = ["id", "signature", "policy", "endpoint", "dir"]
        for field in required_fields:
            if field not in oss_data:
                return {"code": -1, "msg": f"OSS 签名缺少必要字段: {field}"}

        # 2. 构建上传参数
        file_ext = os.path.splitext(image_path)[1] or ".jpg"
        timestamp = int(time.time() * 1000)
        rand = random.randint(0, 999)

        # 处理路径拼接，避免双斜杠
        dir_prefix = oss_data['dir'].rstrip('/')
        dir_suffix = oss_dir.strip('/')
        key = f"{dir_prefix}/{dir_suffix}/{timestamp}_{rand}{file_ext}"

        # 3. 上传文件到 OSS
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'key': key,
                    'OSSAccessKeyId': oss_data['id'],
                    'signature': oss_data['signature'],
                    'policy': oss_data['policy'],
                    'success_action_status': '200'
                }

                upload_url = f"https://qidongkongjian.{oss_data['endpoint']}"
                response = self.session.post(upload_url, data=data, files=files, timeout=60)

                if response.status_code == 200:
                    return {"code": 1, "url": f"/{key}"}
                else:
                    return {"code": -1, "msg": f"上传失败，HTTP状态码: {response.status_code}"}
        except FileNotFoundError:
            return {"code": -1, "msg": f"文件不存在: {image_path}"}
        except Exception as e:
            return {"code": -1, "msg": f"上传异常: {str(e)}"}

    def upload_images_to_oss(self, image_paths: List[str], oss_dir: str = "/images/default") -> Dict[str, Any]:
        """批量上传图片到阿里云 OSS

        Args:
            image_paths: 本地图片路径列表
            oss_dir: OSS 上的目录路径，默认 /images/default

        Returns:
            {
                "code": 1,
                "urls": ["/qidong/images/topic/1728124872456_189.jpg", ...]
            }
            或失败时:
            {
                "code": -1,
                "msg": "错误信息",
                "success_urls": [],  # 成功上传的URL
                "failed_paths": []   # 失败的路径
            }
        """
        if not image_paths:
            return {"code": 1, "urls": []}

        urls = []
        failed_paths = []

        for i, path in enumerate(image_paths):
            result = self.upload_image_to_oss(path, oss_dir)
            if result.get("code") == 1:
                urls.append(result["url"])
            else:
                failed_paths.append({"path": path, "error": result.get("msg", "未知错误")})

        if failed_paths and not urls:
            return {
                "code": -1,
                "msg": f"所有图片上传失败，共 {len(failed_paths)} 张",
                "success_urls": [],
                "failed_paths": failed_paths
            }

        result = {"code": 1, "urls": urls}
        if failed_paths:
            result["partial_failed"] = True
            result["failed_paths"] = failed_paths
            result["msg"] = f"部分图片上传失败，成功 {len(urls)} 张，失败 {len(failed_paths)} 张"

        return result


# 便捷函数

def create_client(user_token: Optional[str] = None) -> DeluluAPIClient:
    """创建 API 客户端"""
    return DeluluAPIClient(user_token)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: api_client.py <command> [args...]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    client = create_client()
    
    if cmd == "agent-url":
        result = client.get_agent_url()
    else:
        result = {"error": f"Unknown command: {cmd}"}
    
    print(json.dumps(result, ensure_ascii=False, indent=2))