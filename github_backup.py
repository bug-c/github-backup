#!/usr/bin/env python3
"""
GitHub Repository Backup Script

This script backs up all repositories from specified GitHub organizations.
Designed to run on Synology NAS for automated backups.
"""

import os
import sys
import yaml
import logging
import argparse
import subprocess
import datetime
from github import Github, GithubException
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Setup argument parser
parser = argparse.ArgumentParser(description='Backup GitHub repositories')
parser.add_argument('--config', default='config.yaml', help='Path to config file')
parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
args = parser.parse_args()

# Load configuration
try:
    with open(args.config, 'r') as config_file:
        config = yaml.safe_load(config_file)
except Exception as e:
    print(f"Error loading configuration: {e}")
    sys.exit(1)

# Setup logging
log_dir = Path(config['backup'].get('path', '.')) / 'logs'
os.makedirs(log_dir, exist_ok=True)

log_file = log_dir / f"github_backup_{datetime.datetime.now().strftime('%Y%m%d')}.log"
log_level = logging.DEBUG if args.verbose else logging.INFO

# Configure logger
logger = logging.getLogger('github_backup')
logger.setLevel(log_level)

# File handler with rotation
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(log_level)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def cleanup_old_logs():
    """Remove log files older than the configured retention period."""
    retention_days = config['backup'].get('log_retention_days', 30)
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)

    for log_file in log_dir.glob('*.log*'):
        file_time = datetime.datetime.fromtimestamp(log_file.stat().st_mtime)
        if file_time < cutoff_date:
            try:
                logger.debug(f"Removing old log file: {log_file}")
                os.remove(log_file)
            except Exception as e:
                logger.error(f"Failed to remove old log file {log_file}: {e}")

def backup_repository(repo, backup_path):
    """Backup a single repository or update an existing backup."""
    repo_path = os.path.join(backup_path, repo.name)

    try:
        if os.path.exists(repo_path):
            # Update existing repository
            logger.info(f"Updating existing repository: {repo.name}")
            os.chdir(repo_path)

            # Fetch updates and reset to origin
            subprocess.run(["git", "fetch", "--all"], check=True, capture_output=True)
            subprocess.run(["git", "reset", "--hard", "origin/main"], check=True, capture_output=True)

            # Try with master if main fails
            if subprocess.run(["git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/main"]).returncode != 0:
                subprocess.run(["git", "reset", "--hard", "origin/master"], check=True, capture_output=True)

            # Pull all branches and tags
            subprocess.run(["git", "pull", "--all"], check=True, capture_output=True)
            subprocess.run(["git", "fetch", "--tags"], check=True, capture_output=True)

        else:
            # Clone new repository
            logger.info(f"Cloning new repository: {repo.name}")
            # Use mirror clone to get all branches and refs
            subprocess.run(
                ["git", "clone", "--mirror", repo.clone_url, repo_path],
                check=True, capture_output=True
            )

        logger.info(f"Successfully backed up: {repo.name}")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Git operation failed for {repo.name}: {e}")
        logger.error(f"Command output: {e.stdout.decode() if e.stdout else ''}")
        logger.error(f"Command error: {e.stderr.decode() if e.stderr else ''}")
        return False
    except Exception as e:
        logger.error(f"Failed to backup repository {repo.name}: {e}")
        return False

def main():
    """Main backup process."""
    start_time = datetime.datetime.now()
    logger.info("Starting GitHub repository backup")

    # Connect to GitHub API
    try:
        g = Github(config['github']['token'])

        # Test connection
        user = g.get_user()
        logger.info(f"Connected to GitHub as: {user.login}")

        # Keep track of stats
        total_repos = 0
        successful_backups = 0
        failed_backups = 0

        # Create backup directory if it doesn't exist
        backup_path = config['backup']['path']
        os.makedirs(backup_path, exist_ok=True)

        # Process each organization
        for org_name in config['organizations']:
            try:
                logger.info(f"Processing organization: {org_name}")

                # Get organization and its repositories
                org = g.get_organization(org_name)
                repos = org.get_repos()

                # Create organization directory
                org_path = os.path.join(backup_path, org_name)
                os.makedirs(org_path, exist_ok=True)

                # Backup each repository
                for repo in repos:
                    total_repos += 1

                    if backup_repository(repo, org_path):
                        successful_backups += 1
                    else:
                        failed_backups += 1

            except GithubException as e:
                logger.error(f"GitHub API error for organization {org_name}: {e}")
            except Exception as e:
                logger.error(f"Error processing organization {org_name}: {e}")

        # Log summary
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds() / 60  # in minutes

        logger.info("=" * 50)
        logger.info("Backup Summary")
        logger.info("=" * 50)
        logger.info(f"Total repositories found: {total_repos}")
        logger.info(f"Successfully backed up: {successful_backups}")
        logger.info(f"Failed backups: {failed_backups}")
        logger.info(f"Backup duration: {duration:.2f} minutes")
        logger.info("=" * 50)

        # Clean up old logs
        cleanup_old_logs()

    except GithubException as e:
        logger.error(f"GitHub API error: {e}")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")

    logger.info("Backup process complete")

if __name__ == "__main__":
    main()