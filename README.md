# Cricfy Decrypted API Setup

This repository automatically downloads, decrypts, and hosts Cricfy's live channels, event configurations, and stream paths.

## How it works
1. **GitHub Actions** runs the python script `fetch_fresh.py` every **5 minutes** (via `.github/workflows/fetch.yml`).
2. The script requests the encrypted Cricfy data using a fresh Unix timestamp HMAC, decrypts it using the hardcoded AES key (`WT1sdkEvUlR4ckd2`) and IV (`Q7sKcm9LR4VaX2pN`).
3. The decrypted data is saved as raw JSON files in the `decrypted_output/` directory.
4. The workflow automatically commits and pushes the updated JSON files back to the repository.

## Setup Instructions (How to Host)
1. **Create a new Repository** on GitHub (can be public or private, but public is easier for direct API access).
2. **Upload all the files** from this folder directly to your repository:
   - `fetch_fresh.py`
   - `requirements.txt`
   - `.github/` (including `.github/workflows/fetch.yml`)
3. **Configure Workflow Permissions**:
   - Go to your repository **Settings** -> **Actions** -> **General**.
   - Scroll down to **Workflow permissions**.
   - Select **Read and write permissions**.
   - Click **Save**.
4. **Enable GitHub Pages (to get the API links)**:
   - Go to **Settings** -> **Pages**.
   - Under **Build and deployment** -> **Source**, select **Deploy from a branch**.
   - Under **Branch**, select `main` (or `master`) and folder `/ (root)`.
   - Click **Save**.
   - Once deployment completes (takes 1-2 minutes), GitHub will give you a public URL (e.g., `https://<your-username>.github.io/<repo-name>/`).

## Decrypted API Links for Developers
You can give these links directly to your app developer:

- **Config API:** `https://<your-username>.github.io/<repo-name>/decrypted_output/genzdev_config.json`
- **Categories API:** `https://<your-username>.github.io/<repo-name>/decrypted_output/event_cats.json`
- **Events API:** `https://<your-username>.github.io/<repo-name>/decrypted_output/events.json`
- **Channels API:** `https://<your-username>.github.io/<repo-name>/decrypted_output/channels.json`
"# dudetvappapi" 
"# api" 
