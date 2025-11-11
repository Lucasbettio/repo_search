from gitlab_collector import GitLabCollector

collector = GitLabCollector(
    token="glpat-OHyUwYiGlpzDbgso6cFqRm86MQp1OndpCA.01.0y1f1mv2q",
    group_path="qa",
    base_url="https://gitlab.nelogica.com.br/"
)

repos = collector.get_group_repositories(prefix_filter="qa/plugins/")
print(f"Foram encontrados {len(repos)} repositórios QA:")
for r in repos:
    print(r)