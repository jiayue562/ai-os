"""
AI OS WorkBuddy技能发现模块
自动发现WorkBuddy技能目录中的所有技能，读取配置并注册到AI OS中
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class SkillDiscovery:
    """WorkBuddy技能发现器"""
    
    def __init__(self, workbuddy_skills_path: str = None):
        """
        初始化技能发现器
        
        Args:
            workbuddy_skills_path: WorkBuddy技能目录路径
               默认: ~/.workbuddy/skills/
        """
        if workbuddy_skills_path is None:
            self.workbuddy_skills_path = os.path.expanduser("~/.workbuddy/skills")
        else:
            self.workbuddy_skills_path = workbuddy_skills_path
            
        # 验证目录是否存在
        if not os.path.exists(self.workbuddy_skills_path):
            logger.warning(f"WorkBuddy技能目录不存在: {self.workbuddy_skills_path}")
            self.workbuddy_skills_path = None
            
        self.skills_registry = {}  # 技能注册表
        self.skill_categories = {}  # 按分类组织的技能
        
    def discover_all_skills(self) -> Dict[str, Dict]:
        """
        发现所有WorkBuddy技能
        
        Returns:
            技能注册表字典
        """
        if self.workbuddy_skills_path is None:
            logger.error("WorkBuddy技能目录未设置")
            return {}
            
        logger.info(f"开始扫描WorkBuddy技能目录: {self.workbuddy_skills_path}")
        
        # 重置注册表
        self.skills_registry = {}
        self.skill_categories = {
            "core": [],      # 核心系统技能
            "cognitive": [], # 认知增强技能
            "execution": [], # 执行技能
            "tool": [],      # 工具技能
            "extension": [], # 扩展技能
            "system": [],    # 系统技能
            "traditional": [], # 传统文化技能
            "spiritual": [], # 精神/能量技能
            "other": []      # 其他分类
        }
        
        # 扫描技能目录
        skill_dirs = []
        try:
            for item in os.listdir(self.workbuddy_skills_path):
                item_path = os.path.join(self.workbuddy_skills_path, item)
                if os.path.isdir(item_path):
                    skill_dirs.append((item, item_path))
        except Exception as e:
            logger.error(f"扫描技能目录失败: {e}")
            return {}
            
        logger.info(f"发现 {len(skill_dirs)} 个技能目录")
        
        # 处理每个技能目录
        for skill_name, skill_path in skill_dirs:
            self._process_skill_directory(skill_name, skill_path)
            
        # 统计结果
        total_skills = len(self.skills_registry)
        categorized_skills = sum(len(skills) for skills in self.skill_categories.values())
        
        logger.info(f"技能发现完成: 共发现 {total_skills} 个技能")
        for category, skills in self.skill_categories.items():
            if skills:
                logger.info(f"  - {category}: {len(skills)} 个技能")
                
        return self.skills_registry
    
    def _process_skill_directory(self, skill_name: str, skill_path: str):
        """处理单个技能目录"""
        
        # 查找skill.yaml文件
        skill_yaml_path = os.path.join(skill_path, "skill.yaml")
        skill_yml_path = os.path.join(skill_path, "skill.yml")
        
        skill_config_path = None
        if os.path.exists(skill_yaml_path):
            skill_config_path = skill_yaml_path
        elif os.path.exists(skill_yml_path):
            skill_config_path = skill_yml_path
            
        if not skill_config_path:
            # 检查是否有SKILL.md但没有skill.yaml
            skill_md_path = os.path.join(skill_path, "SKILL.md")
            if os.path.exists(skill_md_path):
                logger.debug(f"技能 {skill_name} 有SKILL.md但没有skill.yaml，尝试自动生成配置")
                skill_config = self._generate_skill_config(skill_name, skill_path, skill_md_path)
                if skill_config:
                    self._register_skill(skill_name, skill_path, skill_config)
            return
            
        # 读取skill.yaml配置
        try:
            with open(skill_config_path, 'r', encoding='utf-8') as f:
                skill_config = yaml.safe_load(f)
                
            if not skill_config:
                logger.warning(f"技能 {skill_name} 的skill.yaml为空")
                return
                
            self._register_skill(skill_name, skill_path, skill_config)
            
        except yaml.YAMLError as e:
            logger.error(f"解析技能 {skill_name} 的skill.yaml失败: {e}")
        except Exception as e:
            logger.error(f"读取技能 {skill_name} 配置失败: {e}")
    
    def _generate_skill_config(self, skill_name: str, skill_path: str, skill_md_path: str) -> Optional[Dict]:
        """
        基于SKILL.md文件自动生成技能配置
        
        对于没有skill.yaml但有SKILL.md的技能，提取基本信息
        """
        try:
            with open(skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 尝试从SKILL.md中提取基本信息
            config = {
                "name": skill_name,
                "description": f"从SKILL.md自动生成的技能配置: {skill_name}",
                "category": "other",
                "version": "1.0.0",
                "author": "未知",
                "tags": [skill_name],
                "files": [
                    {"path": "SKILL.md", "description": "主技能文档", "required": True}
                ],
                "auto_generated": True  # 标记为自动生成
            }
            
            # 尝试从SKILL.md的前几行提取更多信息
            lines = content.split('\n')
            for i, line in enumerate(lines[:50]):  # 只检查前50行
                line_lower = line.lower()
                
                # 提取描述
                if "description:" in line_lower and len(line) > len("description:"):
                    desc_start = line.find(":") + 1
                    config["description"] = line[desc_start:].strip()
                    
                # 提取版本
                elif "version:" in line_lower and len(line) > len("version:"):
                    version_start = line.find(":") + 1
                    config["version"] = line[version_start:].strip()
                    
                # 提取作者
                elif "author:" in line_lower and len(line) > len("author:"):
                    author_start = line.find(":") + 1
                    config["author"] = line[author_start:].strip()
                    
                # 提取标签
                elif "tags:" in line_lower and len(line) > len("tags:"):
                    tags_start = line.find(":") + 1
                    tags_str = line[tags_start:].strip()
                    if tags_str.startswith("[") and tags_str.endswith("]"):
                        tags_str = tags_str[1:-1]
                        config["tags"] = [tag.strip() for tag in tags_str.split(",")]
            
            return config
            
        except Exception as e:
            logger.error(f"生成技能 {skill_name} 的自动配置失败: {e}")
            return None
    
    def _register_skill(self, skill_name: str, skill_path: str, skill_config: Dict):
        """注册技能到注册表中"""
        
        # 确保有基本字段
        if "name" not in skill_config:
            skill_config["name"] = skill_name
            
        if "display_name" not in skill_config:
            skill_config["display_name"] = skill_config.get("name", skill_name)
            
        if "description" not in skill_config:
            skill_config["description"] = f"技能: {skill_name}"
            
        if "category" not in skill_config:
            skill_config["category"] = "other"
            
        if "version" not in skill_config:
            skill_config["version"] = "1.0.0"
            
        # 添加路径信息
        skill_config["path"] = skill_path
        skill_config["discovered_at"] = os.path.getmtime(skill_path) if os.path.exists(skill_path) else None
        
        # 确定分类
        category = skill_config["category"].lower()
        if category not in self.skill_categories:
            category = "other"
            
        # 注册技能
        skill_id = f"{skill_name}_{skill_config['version'].replace('.', '_')}"
        self.skills_registry[skill_id] = skill_config
        
        # 添加到分类
        if skill_id not in self.skill_categories[category]:
            self.skill_categories[category].append(skill_id)
            
        logger.info(f"注册技能: {skill_config['display_name']} ({skill_config['version']}) - 分类: {category}")
    
    def get_skill_by_id(self, skill_id: str) -> Optional[Dict]:
        """根据ID获取技能配置"""
        return self.skills_registry.get(skill_id)
    
    def get_skills_by_category(self, category: str) -> List[Dict]:
        """根据分类获取技能列表"""
        skill_ids = self.skill_categories.get(category, [])
        return [self.skills_registry[skill_id] for skill_id in skill_ids if skill_id in self.skills_registry]
    
    def search_skills(self, query: str, search_fields: List[str] = None) -> List[Dict]:
        """
        搜索技能
        
        Args:
            query: 搜索查询
            search_fields: 要搜索的字段，默认 ["name", "display_name", "description", "tags"]
            
        Returns:
            匹配的技能列表
        """
        if search_fields is None:
            search_fields = ["name", "display_name", "description", "tags"]
            
        query_lower = query.lower()
        results = []
        
        for skill_id, skill_config in self.skills_registry.items():
            for field in search_fields:
                if field in skill_config:
                    field_value = skill_config[field]
                    
                    # 处理不同类型的字段值
                    if isinstance(field_value, str):
                        if query_lower in field_value.lower():
                            results.append(skill_config)
                            break
                    elif isinstance(field_value, list):
                        # 对于列表（如tags），检查每个元素
                        for item in field_value:
                            if isinstance(item, str) and query_lower in item.lower():
                                results.append(skill_config)
                                break
        
        return results
    
    def export_registry(self, output_path: str = None) -> str:
        """
        导出技能注册表
        
        Args:
            output_path: 输出文件路径，如果为None则返回JSON字符串
            
        Returns:
            如果output_path为None则返回JSON字符串，否则返回文件路径
        """
        registry_data = {
            "total_skills": len(self.skills_registry),
            "discovery_time": os.path.getmtime(__file__) if os.path.exists(__file__) else None,
            "workbuddy_path": self.workbuddy_skills_path,
            "skills": self.skills_registry,
            "categories": self.skill_categories
        }
        
        if output_path is None:
            return json.dumps(registry_data, ensure_ascii=False, indent=2)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, ensure_ascii=False, indent=2)
            return output_path
    
    def load_registry(self, registry_path: str) -> bool:
        """
        从文件加载技能注册表
        
        Args:
            registry_path: 注册表文件路径
            
        Returns:
            是否加载成功
        """
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
                
            self.skills_registry = registry_data.get("skills", {})
            self.skill_categories = registry_data.get("categories", {})
            
            logger.info(f"从 {registry_path} 加载技能注册表，共 {len(self.skills_registry)} 个技能")
            return True
            
        except Exception as e:
            logger.error(f"加载技能注册表失败: {e}")
            return False


# 工具函数
def get_workbuddy_skills_path() -> str:
    """获取WorkBuddy技能目录路径"""
    default_path = os.path.expanduser("~/.workbuddy/skills")
    
    # 检查环境变量
    env_path = os.environ.get("WORKBUDDY_SKILLS_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
        
    # 检查常见位置
    common_paths = [
        default_path,
        os.path.join(os.path.expanduser("~"), ".workbuddy", "skills"),
        os.path.join(os.getcwd(), ".workbuddy", "skills"),
        "C:\\Users\\jia'yue\\.workbuddy\\skills"  # Windows特定路径
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
            
    return default_path


def discover_and_export(output_dir: str = None):
    """
    发现技能并导出注册表
    
    Args:
        output_dir: 输出目录，如果为None则使用当前目录
    """
    if output_dir is None:
        output_dir = os.path.dirname(__file__)
        
    workbuddy_path = get_workbuddy_skills_path()
    logger.info(f"使用WorkBuddy技能目录: {workbuddy_path}")
    
    discovery = SkillDiscovery(workbuddy_path)
    skills = discovery.discover_all_skills()
    
    if not skills:
        logger.warning("未发现任何技能")
        return
        
    # 导出注册表
    output_path = os.path.join(output_dir, "skills_registry.json")
    exported_path = discovery.export_registry(output_path)
    
    logger.info(f"技能注册表已导出到: {exported_path}")
    
    # 生成摘要报告
    report_path = os.path.join(output_dir, "skills_report.md")
    generate_skills_report(discovery, report_path)
    
    return discovery


def generate_skills_report(discovery: SkillDiscovery, report_path: str):
    """生成技能报告"""
    report_lines = [
        "# AI OS WorkBuddy技能发现报告",
        "",
        f"**发现时间**: {os.path.getmtime(__file__) if os.path.exists(__file__) else '未知'}",
        f"**WorkBuddy目录**: {discovery.workbuddy_skills_path}",
        f"**总技能数**: {len(discovery.skills_registry)}",
        "",
        "## 技能分类统计",
        ""
    ]
    
    # 分类统计
    for category, skill_ids in discovery.skill_categories.items():
        if skill_ids:
            report_lines.append(f"- **{category}**: {len(skill_ids)} 个技能")
    
    report_lines.append("")
    report_lines.append("## 核心技能列表")
    report_lines.append("")
    
    # 按分类列出技能
    for category in ["core", "system", "cognitive", "execution", "tool", "traditional"]:
        skills = discovery.get_skills_by_category(category)
        if skills:
            report_lines.append(f"### {category.upper()} 分类")
            report_lines.append("")
            
            for skill in skills:
                display_name = skill.get("display_name", skill.get("name", "未知"))
                version = skill.get("version", "1.0.0")
                description = skill.get("description", "无描述")
                
                report_lines.append(f"#### {display_name} (v{version})")
                report_lines.append(f"**ID**: {list(discovery.skills_registry.keys())[list(discovery.skills_registry.values()).index(skill)]}")
                report_lines.append(f"**描述**: {description}")
                report_lines.append(f"**路径**: {skill.get('path', '未知')}")
                report_lines.append("")
    
    # 写入报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
        
    logger.info(f"技能报告已生成: {report_path}")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 执行技能发现
    discovery = discover_and_export()
    
    if discovery and discovery.skills_registry:
        print(f"技能发现完成! 共发现 {len(discovery.skills_registry)} 个技能")
        
        # 显示核心技能
        core_skills = discovery.get_skills_by_category("core")
        if core_skills:
            print("\n核心技能:")
            for skill in core_skills:
                print(f"  - {skill.get('display_name')} (v{skill.get('version')})")
                
        # 显示系统技能
        system_skills = discovery.get_skills_by_category("system")
        if system_skills:
            print("\n系统技能:")
            for skill in system_skills:
                print(f"  - {skill.get('display_name')} (v{skill.get('version')})")