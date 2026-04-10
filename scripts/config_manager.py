#!/usr/bin/env python3
"""
DELULU Configuration Manager
管理 ~/.delulu/ 目录下的配置文件
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

DELULU_DIR = Path.home() / ".delulu"
CONFIG_FILE = DELULU_DIR / "config.json"
SOUL_FILE = DELULU_DIR / "soul.md"
AGENTS_DIR = DELULU_DIR / "agents"
DATA_DIR = DELULU_DIR / "data" / "matches"
POSTS_DIR = DELULU_DIR / "data" / "posts"


def ensure_dir_structure():
    """确保目录结构存在"""
    DELULU_DIR.mkdir(parents=True, exist_ok=True)
    AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    POSTS_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Optional[Dict[str, Any]]:
    """加载主配置文件"""
    if not CONFIG_FILE.exists():
        return None
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config: Dict[str, Any]):
    """保存主配置文件"""
    ensure_dir_structure()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def init_config():
    """初始化默认配置"""
    default_config = {
        "session_key": "",
        "current_agent": "",
        "agent_list": []
    }
    save_config(default_config)
    return default_config


def load_soul() -> Optional[str]:
    """加载主人画像"""
    if not SOUL_FILE.exists():
        return None
    with open(SOUL_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def save_soul(content: str):
    """保存主人画像"""
    ensure_dir_structure()
    with open(SOUL_FILE, 'w', encoding='utf-8') as f:
        f.write(content)


def load_agent_config(agent_name: str) -> Optional[str]:
    """加载 Agent 配置"""
    agent_file = AGENTS_DIR / f"{agent_name}.md"
    if not agent_file.exists():
        return None
    with open(agent_file, 'r', encoding='utf-8') as f:
        return f.read()


def save_agent_config(agent_name: str, content: str):
    """保存 Agent 配置"""
    ensure_dir_structure()
    agent_file = AGENTS_DIR / f"{agent_name}.md"
    with open(agent_file, 'w', encoding='utf-8') as f:
        f.write(content)


def get_current_agent_info() -> Optional[Dict[str, Any]]:
    """获取当前 Agent 完整信息"""
    config = load_config()
    if not config or not config.get('current_agent'):
        return None
    
    current_agent_name = config['current_agent']
    for agent in config.get('agent_list', []):
        if agent.get('name') == current_agent_name:
            return agent
    return None


def set_current_agent(agent_name: str) -> bool:
    """设置当前 Agent"""
    config = load_config()
    if not config:
        return False
    
    # 检查 agent 是否存在
    agent_names = [a.get('name') for a in config.get('agent_list', [])]
    if agent_name not in agent_names:
        return False
    
    config['current_agent'] = agent_name
    save_config(config)
    return True


def add_agent(agent_data: Dict[str, Any]):
    """添加 Agent 到配置"""
    config = load_config()
    if not config:
        config = init_config()
    
    # 检查是否已存在
    agent_list = config.get('agent_list', [])
    for i, agent in enumerate(agent_list):
        if agent.get('name') == agent_data.get('name'):
            # 更新现有 agent
            agent_list[i] = agent_data
            break
    else:
        # 添加新 agent
        agent_list.append(agent_data)
    
    config['agent_list'] = agent_list
    
    # 如果是第一个 agent，设为当前 agent
    if len(agent_list) == 1:
        config['current_agent'] = agent_data.get('name')
    
    save_config(config)


def update_agent_token(agent_name: str, user_token: str):
    """更新 Agent 的 user_token"""
    config = load_config()
    if not config:
        return
    
    for agent in config.get('agent_list', []):
        if agent.get('name') == agent_name:
            agent['user_token'] = user_token
            break
    
    save_config(config)


def load_match_data(user_id: str) -> Dict[str, Any]:
    """加载匹配数据"""
    match_dir = DATA_DIR / user_id
    result = {}
    
    profile_file = match_dir / "profile.md"
    chat_file = match_dir / "chat.md"
    analysis_file = match_dir / "analysis.json"
    
    if profile_file.exists():
        with open(profile_file, 'r', encoding='utf-8') as f:
            result['profile'] = f.read()
    
    if chat_file.exists():
        with open(chat_file, 'r', encoding='utf-8') as f:
            result['chat'] = f.read()
    
    if analysis_file.exists():
        with open(analysis_file, 'r', encoding='utf-8') as f:
            result['analysis'] = json.load(f)
    
    return result


def save_match_data(user_id: str, profile: str = None, chat: str = None, analysis: Dict = None):
    """保存匹配数据"""
    match_dir = DATA_DIR / user_id
    match_dir.mkdir(parents=True, exist_ok=True)
    
    if profile is not None:
        with open(match_dir / "profile.md", 'w', encoding='utf-8') as f:
            f.write(profile)
    
    if chat is not None:
        with open(match_dir / "chat.md", 'w', encoding='utf-8') as f:
            f.write(chat)
    
    if analysis is not None:
        with open(match_dir / "analysis.json", 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)


def calculate_match_score(soul_md: str, agent_md: str, profile_md: str) -> Dict[str, Any]:
    """
    计算匹配分数
    返回包含总分和各项评分的字典
    """
    # 默认评分维度（与 SKILL.md 一致，7 维满分 100）
    scores = {
        "location": 0,          # 📍 地理位置 (0-25)
        "age_gap": 0,           # 🎂 年龄差距 (0-15)
        "education": 0,         # 🎓 教育背景 (0-10)
        "personality": 0,       # 😊 性格匹配 (0-15)
        "interests": 0,         # 🎯 兴趣重叠 (0-10)
        "ideal_match": 0,       # 💝 理想型匹配 (0-10)
        "post_relevance": 0,    # 📝 帖子内容契合度 (0-15)
        "total": 0
    }
    
    # TODO: 实现具体的评分逻辑
    # 这里可以根据 soul.md 和 agent.md 中的评分规则进行计算
    
    scores["total"] = sum([
        scores["location"],
        scores["age_gap"],
        scores["education"],
        scores["personality"],
        scores["interests"],
        scores["ideal_match"],
        scores["post_relevance"]
    ])
    
    return scores


def get_preferred_channel() -> Optional[str]:
    """获取用户偏好的通知渠道"""
    config = load_config()
    if not config:
        return None
    return config.get("preferred_channel")


def set_preferred_channel(channel: str) -> bool:
    """设置用户偏好的通知渠道"""
    config = load_config()
    if not config:
        return False
    config["preferred_channel"] = channel
    save_config(config)
    return True


# ========== 帖子数据管理 ==========

def save_post_data(posting_id: str, content: str, images: List[str],
                   topic_id: int = 6, post_type: str = "article",
                   subject_list: List[str] = None,
                   local_image_paths: List[str] = None) -> Dict[str, Any]:
    """保存帖子数据到本地

    Args:
        posting_id: 帖子ID（服务器返回）
        content: 帖子内容
        images: 图片URL列表
        topic_id: 版块ID
        post_type: 帖子类型
        subject_list: 话题标签列表
        local_image_paths: 本地图片路径列表（用于记录原始文件）

    Returns:
        保存的帖子数据字典
    """
    ensure_dir_structure()

    post_data = {
        "posting_id": posting_id,
        "content": content,
        "images": images,
        "topic_id": topic_id,
        "type": post_type,
        "subject_list": subject_list or [],
        "created_at": int(time.time()),
        "local_image_paths": local_image_paths or []
    }

    # 保存到文件
    post_file = POSTS_DIR / f"{posting_id}.json"
    with open(post_file, 'w', encoding='utf-8') as f:
        json.dump(post_data, f, ensure_ascii=False, indent=2)

    return post_data




def load_post_data(posting_id: str) -> Optional[Dict[str, Any]]:
    """加载帖子数据

    Args:
        posting_id: 帖子ID

    Returns:
        帖子数据字典，不存在返回 None
    """
    post_file = POSTS_DIR / f"{posting_id}.json"
    if not post_file.exists():
        return None

    with open(post_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_all_posts(limit: int = 100) -> List[Dict[str, Any]]:
    """列出所有本地保存的帖子

    Args:
        limit: 最多返回条数

    Returns:
        帖子数据列表，按时间倒序
    """
    if not POSTS_DIR.exists():
        return []

    posts = []
    for post_file in sorted(POSTS_DIR.glob("*.json"), reverse=True):
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                post_data = json.load(f)
                posts.append(post_data)
        except (json.JSONDecodeError, IOError):
            continue

        if len(posts) >= limit:
            break

    return posts


def get_posts_with_images() -> List[Dict[str, Any]]:
    """获取所有带图片的帖子

    Returns:
        包含图片的帖子列表
    """
    all_posts = list_all_posts(limit=1000)
    return [p for p in all_posts if p.get("images")]


def delete_post_data(posting_id: str) -> bool:
    """删除帖子本地数据

    Args:
        posting_id: 帖子ID

    Returns:
        是否成功删除
    """
    post_file = POSTS_DIR / f"{posting_id}.json"
    if post_file.exists():
        post_file.unlink()
        return True
    return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: config_manager.py <command> [args...]")
        print("Commands: init, load, get-agent, set-agent")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        init_config()
        print("Config initialized")
    elif cmd == "load":
        config = load_config()
        print(json.dumps(config, ensure_ascii=False, indent=2))
    elif cmd == "get-agent":
        agent = get_current_agent_info()
        print(json.dumps(agent, ensure_ascii=False, indent=2))
    elif cmd == "set-agent" and len(sys.argv) >= 3:
        result = set_current_agent(sys.argv[2])
        print(f"Set agent: {result}")
    else:
        print(f"Unknown command: {cmd}")