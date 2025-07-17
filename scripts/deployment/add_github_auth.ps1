# Add GitHub authentication to Ansible deploy.yml
$content = Get-Content "ansible/deploy.yml" -Raw

# Add GitHub token variable after docker_image
$dockerImageLine = "    docker_image: `"ghcr.io/{{ github_repository | default('your-username/super-app-backend') }}:latest`""
$githubTokenLine = "    github_token: `"{{ lookup('env', 'GITHUB_TOKEN') }}`""

$content = $content -replace $dockerImageLine, "$dockerImageLine`n    $githubTokenLine"

# Add Docker login task after Docker service start
$dockerServiceTask = "    - name: Enable and start Docker service"
$dockerLoginTask = @"

    - name: Login to GitHub Container Registry
      docker_login:
        registry: ghcr.io
        username: "{{ lookup('env', 'GITHUB_USERNAME', default='your-username') }}"
        password: "{{ github_token }}"
      when: github_token is defined

"@

$content = $content -replace $dockerServiceTask, "$dockerServiceTask$dockerLoginTask"

# Write updated content
$content | Out-File "ansible/deploy.yml" -Encoding UTF8

Write-Host "GitHub authentication added to ansible/deploy.yml" -ForegroundColor Green
