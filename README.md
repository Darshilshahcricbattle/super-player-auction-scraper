# Super Player Auction Scraper

This project is set up to scrape tournament data from SuperPlayerAuction.com on a daily basis and update an Excel sheet via the Microsoft Graph API.

## GitHub Actions Automated Daily Scraping

This repository is configured to run the scraper automatically every day at 10:00 AM UTC using GitHub Actions. The scraper will:

1. Collect tournament data from SuperPlayerAuction.com
2. Save the data to JSON files in the `data` directory
3. Update an Excel sheet via Microsoft Graph API (if credentials are provided)
4. Store logs and screenshots for debugging

## Setup Instructions

### 1. Create a Private Repository

First, create a private GitHub repository:

1. Go to [GitHub](https://github.com/) and sign in with your account
2. Click on the "+" icon in the top-right corner and select "New repository"
3. Name your repository (e.g., "super-player-auction-scraper")
4. Set it to "Private"
5. Click "Create repository"

### 2. Push Your Code to the Repository

1. Initialize Git in your local project folder (if not already done)
2. Add your GitHub repository as a remote
3. Push your code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Darshilshahcricbattle/super-player-auction-scraper.git
git push -u origin main
```

### 3. Set up GitHub Secrets

To securely store your Microsoft Graph API credentials:

1. Go to your repository on GitHub
2. Click on "Settings" > "Secrets and variables" > "Actions"
3. Click "New repository secret"
4. Add the following secrets:
   - Name: `AZURE_CLIENT_ID` - Value: Your Azure application client ID
   - Name: `AZURE_TENANT_ID` - Value: Your Azure tenant ID
   - Name: `AZURE_CLIENT_SECRET` - Value: Your Azure client secret

### 4. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. You should see the "Daily Scraper" workflow listed
3. Click "Enable workflows" if prompted

## Testing the Setup

To test if everything is set up correctly:

1. Go to the "Actions" tab in your repository
2. Find the "Daily Scraper" workflow
3. Click "Run workflow" and select "Run workflow" from the dropdown
4. Wait for the workflow to complete and check the logs

## How It Works

- The scraper runs on GitHub's servers every day at 10:00 AM UTC
- It uses a headless Chrome browser to scrape data
- The scraped data is saved to the repository
- You don't need to have your computer on or connected to the internet
- All results are stored in your private GitHub repository

## Troubleshooting

If the scraper fails:

1. Check the workflow run logs in the GitHub Actions tab
2. Look at the screenshots in the logs directory (they're uploaded as artifacts)
3. Verify that your GitHub secrets are set up correctly
4. Ensure the website structure hasn't changed, which might require updating the scraper code

## Notes

- The data and logs are committed back to your repository, so you can see the history of all scraped data
- Make sure your repository remains private to protect any sensitive information
- GitHub Actions provides 2,000 free minutes per month on private repositories, which should be more than enough for daily runs