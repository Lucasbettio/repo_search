import gitlab

class GitLabCollector:
    def __init__(self, token: str, group_path: str, base_url: str = "https://gitlab.nelogica.com.br/"):
        """
        token: Token pessoal com permissão read_api
        group_path: Caminho completo do grupo (ex: "empresa/devops")
        base_url: URL da instância GitLab (ex: "https://gitlab.seudominio.com")
        """
        self.gl = gitlab.Gitlab(base_url, private_token=token)
        self.group_path = group_path

    def get_group_repositories(self, prefix_filter: str | None = None):
        group = self.gl.groups.get(self.group_path)
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