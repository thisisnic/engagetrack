import matplotlib.pyplot as plt

def generate_contributor_chart(repo_name, contributors):
    names = [c['login'] for c in contributors if 'login' in c]
    contributions = [c['contributions'] for c in contributors if 'contributions' in c]
    plt.bar(names, contributions)
    plt.title(f"Top Contributors for {repo_name}")
    plt.xlabel("Contributors")
    plt.ylabel("Contributions")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"{repo_name}_contributors.png")
    plt.close()

def generate_issue_response_chart(repo_name, issues):
    response_times = []
    for issue in issues:
        if 'created_at' in issue and 'closed_at' in issue:
            created_at = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            closed_at = datetime.strptime(issue['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
            response_times.append((closed_at - created_at).total_seconds() / 3600)
    
    if response_times:
        plt.hist(response_times, bins=10, color='skyblue', edgecolor='black')
        plt.title(f"Issue Response Times for {repo_name}")
        plt.xlabel("Response Time (hours)")
        plt.ylabel("Number of Issues")
        plt.savefig(f"{repo_name}_issues.png")
        plt.close()
    else:
        print(f"No response time data available for {repo_name}")
