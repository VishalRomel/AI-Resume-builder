import os
import requests
from flask import Flask, redirect, request, session, url_for
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

app = Flask(__name__)
app.secret_key = os.urandom(24)  

# Replace these with your GitHub OAuth App credentials
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# GitHub OAuth URLs
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com/user/repos"


@app.route("/")
def home():
    return '<a href="/login">Login with GitHub</a>'


@app.route("/login")
def login():
    return redirect(f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=repo")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No code returned from GitHub.", 400

    token_response = requests.post(
        GITHUB_TOKEN_URL,
        headers={"Accept": "application/json"},
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
        },
    )

    if token_response.status_code != 200:
        return (
            f"Error fetching token: {token_response.text}",
            token_response.status_code,
        )

    try:
        token_json = token_response.json()
    except ValueError:
        return f"Error parsing token response: {token_response.text}", 500

    access_token = token_json.get("access_token")
    with open("download_links.txt", "w") as file:
        file.write(access_token)

    if not access_token:
        return "Error: Access token not found.", 500

    session["access_token"] = access_token
    return redirect(url_for("repos"))


@app.route("/repos")
def repos():
    access_token = session.get("access_token")
    if not access_token:
        return redirect(url_for("login"))

    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    user_response = requests.get("https://api.github.com/user", headers=headers)
    if user_response.status_code != 200:
        return (
            f"Error fetching user data: {user_response.text}",
            user_response.status_code,
        )

    user_data = user_response.json()
    username = user_data.get("login")

    all_repos = []
    page = 1
    while True:
        response = requests.get(
            f"{GITHUB_API_URL}?page={page}&per_page=100", headers=headers
        )
        if response.status_code != 200:
            return f"Error fetching repositories: {response.text}", response.status_code

        repos = response.json()
        if not repos:
            break

        all_repos.extend(repos)
        if "Link" in response.headers and 'rel="next"' in response.headers["Link"]:
            page += 1
        else:
            break

    if not all_repos:
        return "<p>No repositories found, or the OAuth token doesn't have the required permissions.</p>"

    download_links = []
    repo_list = "<h2>User Repositories:</h2><ul>"
    for repo in all_repos:
        repo_name = repo["name"]
        default_branch = repo.get("default_branch", "main") 
        download_url = f"https://github.com/{username}/{repo_name}/archive/refs/heads/{default_branch}.zip"
        repo_list += f"<li><a href='{download_url}'>{repo_name}</a class='download'> (Download ZIP)</li>"
        download_links.append(repo["name"] + "\n" + download_url)
    repo_list += "</ul>"

    with open("download_links.txt", "w") as file:
        for link in download_links:

            file.write(link + "\n")  
    os._exit(0)
    return repo_list


if __name__ == "__main__":
    app.run(debug=True)
