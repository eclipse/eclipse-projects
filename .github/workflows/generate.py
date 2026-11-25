# *******************************************************************************
# Copyright (c) 2023 Eclipse Foundation and others.
# This program and the accompanying materials are made available
# under the terms of the MIT License
# which is available at https://spdx.org/licenses/MIT.html
# SPDX-License-Identifier: MIT
# *******************************************************************************

import os
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


BASE_URL = "https://projects.eclipse.org/api/projects"


def get_http_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def generate():
    session = get_http_session()
    page = 1
    projects = []

    while True:
        print(f"Getting page {page} from Eclipse API")
        params = {"github_only": 1, "pagesize": 100, "page": page}
        response = session.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        new_projects = response.json()
        if len(new_projects) > 0:
            projects.extend(new_projects)
            page += 1
        else:
            break

    if not projects:
        raise RuntimeError(
            "No projects retrieved from Eclipse API. "
            "Aborting to prevent overwriting catalog."
        )

    OUTPUT = './docs/projects.csv'
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    temp_output = OUTPUT + '.tmp'

    with open(temp_output, "w", encoding="utf-8") as out:
        out.write("| Project name | Eclipse Project | GitHub organization |\n")
        out.write("| :----------- | :-------------- | :------------------ |\n")

        for project in projects:
            name = escape(project.get("name") or "")
            project_id = escape(project.get("project_id") or "")

            github_data = project.get("github")
            github_id = (
                github_data.get("org")
                if isinstance(github_data, dict)
                else None
            )

            if not github_id:
                repos = project.get("github_repos") or []
                for repo in repos:
                    if isinstance(repo, dict) and "url" in repo:
                        m = re.search(
                            r"https://github\.com/([^/]+)/.*",
                            repo["url"]
                        )
                        if m is not None:
                            github_id = m.group(1)
                            break

            github_link = (
                f"[{github_id}](https://github.com/{github_id})"
                if github_id else ""
            )
            project_link = (
                f"[{project_id}]"
                f"(https://projects.eclipse.org/projects/{project_id})"
            )

            out.write(f"| {name} | {project_link} | {github_link} |\n")

    os.replace(temp_output, OUTPUT)
    print(f"Successfully generated {len(projects)} projects in {OUTPUT}")


def escape(s: str) -> str:
    if not s:
        return ""
    return s.replace("|", "&#9;")


if __name__ == "__main__":
    generate()
    exit(0)
