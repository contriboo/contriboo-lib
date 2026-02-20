from pydantic import BaseModel, Field


class GitHubUserDTO(BaseModel):
    login: str | None = None
    id: int | None = None
    node_id: str | None = None
    avatar_url: str | None = None
    gravatar_id: str | None = None
    url: str | None = None
    html_url: str | None = None
    followers_url: str | None = None
    following_url: str | None = None
    gists_url: str | None = None
    starred_url: str | None = None
    subscriptions_url: str | None = None
    organizations_url: str | None = None
    repos_url: str | None = None
    events_url: str | None = None
    received_events_url: str | None = None
    type: str | None = None
    user_view_type: str | None = None
    site_admin: bool | None = None


class GitHubLicenseDTO(BaseModel):
    key: str | None = None
    name: str | None = None
    spdx_id: str | None = None
    url: str | None = None
    node_id: str | None = None


class GitHubPermissionsDTO(BaseModel):
    admin: bool | None = None
    maintain: bool | None = None
    push: bool | None = None
    triage: bool | None = None
    pull: bool | None = None


class GitHubRepositoryDTO(BaseModel):
    id: int | None = None
    node_id: str | None = None
    name: str | None = None
    full_name: str | None = None
    private: bool | None = None
    owner: GitHubUserDTO | None = None
    html_url: str | None = None
    description: str | None = None
    fork: bool | None = None
    url: str | None = None
    archive_url: str | None = None
    assignees_url: str | None = None
    blobs_url: str | None = None
    branches_url: str | None = None
    collaborators_url: str | None = None
    comments_url: str | None = None
    commits_url: str | None = None
    compare_url: str | None = None
    contents_url: str | None = None
    contributors_url: str | None = None
    deployments_url: str | None = None
    downloads_url: str | None = None
    events_url: str | None = None
    forks_url: str | None = None
    git_commits_url: str | None = None
    git_refs_url: str | None = None
    git_tags_url: str | None = None
    git_url: str | None = None
    issue_comment_url: str | None = None
    issue_events_url: str | None = None
    issues_url: str | None = None
    keys_url: str | None = None
    labels_url: str | None = None
    languages_url: str | None = None
    merges_url: str | None = None
    milestones_url: str | None = None
    notifications_url: str | None = None
    pulls_url: str | None = None
    releases_url: str | None = None
    ssh_url: str | None = None
    stargazers_url: str | None = None
    statuses_url: str | None = None
    subscribers_url: str | None = None
    subscription_url: str | None = None
    tags_url: str | None = None
    teams_url: str | None = None
    trees_url: str | None = None
    clone_url: str | None = None
    mirror_url: str | None = None
    hooks_url: str | None = None
    svn_url: str | None = None
    homepage: str | None = None
    language: str | None = None
    forks_count: int | None = None
    stargazers_count: int | None = None
    watchers_count: int | None = None
    size: int | None = None
    default_branch: str | None = None
    open_issues_count: int | None = None
    is_template: bool | None = None
    topics: list[str] = Field(default_factory=list)
    has_issues: bool | None = None
    has_projects: bool | None = None
    has_wiki: bool | None = None
    has_pages: bool | None = None
    has_downloads: bool | None = None
    has_discussions: bool | None = None
    archived: bool | None = None
    disabled: bool | None = None
    visibility: str | None = None
    pushed_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    permissions: GitHubPermissionsDTO | None = None
    allow_rebase_merge: bool | None = None
    template_repository: dict[str, object] | None = None
    temp_clone_token: str | None = None
    allow_squash_merge: bool | None = None
    allow_merge_commit: bool | None = None
    allow_auto_merge: bool | None = None
    delete_branch_on_merge: bool | None = None
    allow_update_branch: bool | None = None
    use_squash_pr_title_as_default: bool | None = None
    squash_merge_commit_title: str | None = None
    squash_merge_commit_message: str | None = None
    merge_commit_title: str | None = None
    merge_commit_message: str | None = None
    allow_forking: bool | None = None
    web_commit_signoff_required: bool | None = None
    forks: int | None = None
    open_issues: int | None = None
    watchers: int | None = None
    license: GitHubLicenseDTO | None = None


class GitCommitTreeDTO(BaseModel):
    sha: str | None = None
    url: str | None = None


class GitCommitIdentityDTO(BaseModel):
    name: str | None = None
    email: str | None = None
    date: str | None = None


class GitCommitVerificationDTO(BaseModel):
    verified: bool | None = None
    reason: str | None = None
    signature: str | None = None
    payload: str | None = None
    verified_at: str | None = None


class GitCommitDTO(BaseModel):
    url: str | None = None
    author: GitCommitIdentityDTO | None = None
    committer: GitCommitIdentityDTO | None = None
    message: str | None = None
    tree: GitCommitTreeDTO | None = None
    comment_count: int | None = None
    verification: GitCommitVerificationDTO | None = None


class GitCommitParentDTO(BaseModel):
    url: str | None = None
    html_url: str | None = None
    sha: str | None = None


class GitHubCommitSearchItemDTO(BaseModel):
    url: str | None = None
    sha: str | None = None
    node_id: str | None = None
    html_url: str | None = None
    comments_url: str | None = None
    commit: GitCommitDTO | None = None
    author: GitHubUserDTO | None = None
    committer: GitHubUserDTO | None = None
    parents: list[GitCommitParentDTO] = Field(default_factory=list)
    repository: GitHubRepositoryDTO | None = None
    score: float | None = None


class GitHubCommitSearchResponseDTO(BaseModel):
    total_count: int | None = None
    incomplete_results: bool | None = None
    items: list[GitHubCommitSearchItemDTO] = Field(default_factory=list)
