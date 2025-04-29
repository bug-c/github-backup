# GitHub Repository Backup

A Python-based solution for backing up GitHub repositories from multiple organizations to your local storage or Synology NAS.

## Features

- Backs up all repositories from specified GitHub organizations
- Supports incremental updates to existing backups
- Maintains organizational structure in backups
- Preserves all branches, tags, and refs
- Detailed logging with rotation and retention
- Designed for automation via cron or Synology Task Scheduler

## Requirements

- Python 3.6 or higher
- Git command-line tools
- GitHub Personal Access Token with appropriate permissions

## Installation

### Standard Installation

1. Clone this repository:
```
   git clone https://github.com/yourusername/github-backup.git
   cd github-backup
```
   
2. Install required dependencies:
```
pip install -r requirements.txt
```
   
3. Create and edit your configuration file:
```
cp config.yaml.example config.yaml
nano config.yaml
```
4. Test the script:
```
python github_backup.py --verbose
```

### Installation on Synology NAS

1. Install Python 3 from Synology Package Center
2. Connect to your Synology NAS via SSH:
```
ssh admin@your-nas-ip
```
3. Create a directory for the script:
```
mkdir -p /volume1/scripts/github-backup
```
4. Copy the script files to your NAS (using SCP, rsync, or the File Station UI)
5. Install required dependencies:
```
pip3 install -r requirements.txt
```
6. Make the script executable:
```
chmod +x /volume1/scripts/github-backup/github_backup.py
```
7. Edit the configuration file:
```
nano /volume1/scripts/github-backup/config.yaml
```
8. Test the script:
```
Test the script:
cd /volume1/scripts/github-backup
./github_backup.py --verbose
```

## Configuration

Create a config.yaml file with the following structure:

```
# GitHub API Configuration
github:
# Create a personal access token at https://github.com/settings/tokens
# Needs repo and read:org permissions
token: "your_github_personal_access_token"

# Organizations to backup
organizations:
- org_name1
- org_name2
# Add more organizations as needed

# Backup Configuration
backup:
# Path where repositories will be backed up
path: "/volume1/backups/github"
# How many days to keep backup logs
log_retention_days: 30

```

### GitHub Token Permissions

Create a personal access token at: https://github.com/settings/tokens

Required permissions:
- repo (Full control of private repositories)
- read:org (Read organization membership)

## Usage

### Manual Execution

Run the script manually:
```
python github_backup.py
```

With verbose logging:
```
With verbose logging:
```

Using a custom config file:
```
python github_backup.py --config /path/to/custom-config.yaml
```

### Automated Backup

Add a cron job to run the backup automatically:

```
# Edit crontab
crontab -e

# Add a line to run the script daily at 2 AM
0 2 * * * cd /path/to/github-backup && /usr/bin/python3 github_backup.py
```

### Synology Task Scheduler

1. Open Synology DSM and go to "Control Panel"
2. Open "Task Scheduler"
3. Click "Create" > "Scheduled Task" > "User-defined script"
4. Set up a schedule (e.g., daily at 2 AM)
5. In the "Task Settings" tab, enter the following command:
```
cd /volume1/scripts/github-backup && /usr/local/bin/python3 github_backup.py
```

## Backup Structure
The backup will be organized as follows:
```
/backup/path/
├── logs/
│   ├── github_backup_20230101.log
│   └── github_backup_20230102.log
├── org_name1/
│   ├── repo1/
│   └── repo2/
└── org_name2/
    ├── repo3/
    └── repo4/
```

## Troubleshooting

### Common Issues

1. API Rate Limits:
- GitHub API has rate limits that may impact large backups
- The script includes retry logic with exponential backoff
- Consider using a GitHub Enterprise account for higher limits
2. Authentication Errors:
- Verify your token has the correct permissions
- Check that your token hasn't expired
- Ensure the token is correctly entered in config.yaml
3. Git Errors:
- Ensure Git is installed and available in PATH
- Check disk space for large repositories
- Verify you have network access to GitHub

### Logs

Check the logs directory for detailed information about backup operations:
```
cat /backup/path/logs/github_backup_YYYYMMDD.log
```

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0) - see the LICENSE file for details.

GPL-3.0 is a strong copyleft license that requires that any derivative work is distributed under the same license terms. This means if you distribute this software or any modifications, you must make the source code available and license it under GPL-3.0.

For more information about the GPL-3.0 license, visit: https://www.gnu.org/licenses/gpl-3.0.en.html