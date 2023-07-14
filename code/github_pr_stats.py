from github import Github
from github import Auth
import sys
import csv

"""
This script gets the recent pull request and reviews that your team has issued since some date.

For PRs it saves the following into a csv file:
    'id', 'repo', 'pull_number', 'author', 'state', 'create_time', 'merge_time', 'additions', 'deletions', 'url'
For Reviews it saves the following into a csv file:
    'id', 'pr_id', 'reviewer', 'state', 'submit_time'   

These csv files can be uploaded to your own personal table in BQ to be joined and collect stats such as:
    * Avg merge time
    * Num prs_issued by team member
    * Num reveiws provided by team member
    * Avg PR size
    * Time to first approval
    * Etc.
    
Usage: python3 github_pr_stats.py GH_AUTH_TOKEN GH_TEAM_SLUGNAME START_DATE REPO_LIST
GH_AUTH_TOKEN: see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
GH_TEAM_SLUGNAME: Find it here https://github.com/orgs/etsy/teams
START_DATE: YYYY-MM-DD
REPO_LIST: comma-separated list of all the repos you want to collect stats from.  Ex: repo1,repo2,etc
"""


TEAM_LOGINS = []


def write_to_csv(file_path, data):
    with open(file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)


def get_team_member_logins(github, slug_name):
    global TEAM_LOGINS
    if not TEAM_LOGINS:
        # find all members of our team
        team = []
        gh_team = github.get_organization("etsy").get_team_by_slug(slug_name)
        for team_member in gh_team.get_members():
            team.append(team_member.login)
        TEAM_LOGINS = team

    return TEAM_LOGINS


def get_prs_for_team(github, repo, slug_name, pr_start_date):
    # author:dossett author: bgreenlee author: bmcgonigle etc.
    author_query = ' '.join(['author:'+s for s in get_team_member_logins(github, slug_name)])
    print(f"Getting PRs for {repo} from GitHub")
    return github.search_issues(query=f"is:pr is:merged created:>{pr_start_date} repo:etsy/{repo} " + author_query, sort='created', order='asc')


def get_pr_data(repo, prs):
    pr_rows = []
    for pr in prs:
        additions = 0
        deletions = 0
        # collect size stats on this PR
        for commit in pr.get_commits():
            stats = commit.stats
            additions += stats.additions
            deletions += stats.deletions

        pr_rows.append([pr.id, repo, pr.number, pr.user.login, pr.state, pr.created_at, pr.merged_at,
                        additions, deletions, pr.html_url])
    return pr_rows


def get_reviews_data(prs):
    review_rows = []
    # record all reviews received on this PR
    for pr in prs:
        for review in pr.get_reviews():
            review_rows.append([review.id, pr.id, review.user.login, review.state, review.submitted_at])
    return review_rows


def main():
    # configurations
    gh_auth_token = sys.argv[1]
    pr_out_file = '../outputs/github_pr_stats/pr_rows.csv'
    reviews_out_file = '../outputs/github_pr_stats/reviews_rows.csv'
    gh_team_slugname = sys.argv[2]
    pr_start_date = sys.argv[3]
    team_repos = sys.argv[4].split(',')

    auth = Auth.Token(gh_auth_token)
    g = Github(auth=auth)

    prs = []
    pr_data = [['id', 'repo', 'pull_number', 'author', 'state', 'create_time', 'merge_time', 'additions', 'deletions', 'url']]
    review_data = [['id', 'pr_id', 'reviewer', 'state', 'submit_time']]

    for repo in team_repos:
        repo_prs = [x.as_pull_request() for x in get_prs_for_team(g, repo, gh_team_slugname, pr_start_date)]
        pr_data.extend(get_pr_data(repo, repo_prs))
        prs.extend(repo_prs)

    print("Writing prs to file")
    write_to_csv(pr_out_file, pr_data)

    print("Writing reviews to file")
    review_data.extend(get_reviews_data(prs))
    write_to_csv(reviews_out_file, review_data)


main()
