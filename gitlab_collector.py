import gitlab
from typing import List, Optional

class GitLabCollector:
    def __init__(self, token: str, base_url: str = "https://gitlab.nelogica.com.br/"):
        self.gl = gitlab.Gitlab(base_url, private_token=token)
        self.base_url = base_url

    def list_groups(self) -> List[dict]:
        groups = self.gl.groups.list(all=True, order_by="name", sort="asc")
        return [
            {
                "id": group.id,
                "name": group.name,
                "path": group.path,
                "full_path": group.full_path
            }
            for group in groups
        ]

    def get_group_repositories(self, group_path: str, prefix_filter: Optional[str] = None) -> List[str]:
        group = self.gl.groups.get(group_path)
        projects = group.projects.list(
            include_subgroups=True,
            archived=False,
            with_shared=False,
            all=True,
        )
        repo_list = [
            p.path_with_namespace
            for p in projects
            if not getattr(p, "forked_from_project", None)
        ]
        if prefix_filter:
            repo_list = [r for r in repo_list if r.startswith(prefix_filter)]
        return repo_list

    def get_multiple_groups_repositories(self, group_paths: List[str]) -> List[str]:
        all_repos = []
        seen = set()
        for group_path in group_paths:
            repos = self.get_group_repositories(group_path)
            for repo in repos:
                if repo not in seen:
                    seen.add(repo)
                    all_repos.append(repo)
        return all_repos