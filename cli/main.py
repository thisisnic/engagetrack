import argparse
import asyncio
from app.fetcher import fetch_metrics
from app.visualizer import generate_contributor_chart, generate_issue_response_chart

def parse_args():
    parser = argparse.ArgumentParser(description="EngageTrack CLI Tool")
    subparsers = parser.add_subparsers(dest='command')

    # Add repository command
    add_parser = subparsers.add_parser('add', help='Add a repository to track')
    add_parser.add_argument('repo_url', help='GitHub repository URL (e.g., owner/repo)')

    # Get metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Fetch engagement metrics for a repository')
    metrics_parser.add_argument('repo_url', help='GitHub repository URL (e.g., owner/repo)')

    return parser.parse_args()

async def main():
    args = parse_args()

    if args.command == 'add':
        from app.models import save_repo
        repo = save_repo(args.repo_url)
        print(f"Repository {repo.name} added successfully.")
    elif args.command == 'metrics':
        metrics = await fetch_metrics([args.repo_url])
        if metrics:
            repo_metrics = metrics[0]
            contributors = repo_metrics.get('contributors', [])
            issues = repo_metrics.get('issues', [])
            if contributors:
                generate_contributor_chart(repo_metrics['repo_url'], contributors)
                print(f"Contributor chart generated for {repo_metrics['repo_url']}.")
            if issues:
                generate_issue_response_chart(repo_metrics['repo_url'], issues)
                print(f"Issue response chart generated for {repo_metrics['repo_url']}.")
        else:
            print("No metrics available.")
    else:
        print("Invalid command. Use 'add' or 'metrics'.")

if __name__ == '__main__':
    asyncio.run(main())
