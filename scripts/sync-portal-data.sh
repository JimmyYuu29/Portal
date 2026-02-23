#!/bin/bash
# =============================================================
# sync-portal-data.sh
# Synchronize Portal data between DATA_DIR and repo runtime
# Ensures persistent data survives git pull / redeploy
# =============================================================
set -euo pipefail

# ---- Configuration ----
DATA_DIR="${DATA_DIR:-/home/rootadmin/data/portal}"
REPO_DIR="${REPO_DIR:-/home/rootadmin/Portal}"
PORTAL_DIR="${REPO_DIR}/portal"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[SYNC]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[SYNC]${NC} $*"; }
log_error() { echo -e "${RED}[SYNC]${NC} $*"; }

echo "================================================"
echo "Portal Data Sync Script"
echo "DATA_DIR : ${DATA_DIR}"
echo "REPO_DIR : ${REPO_DIR}"
echo "================================================"
echo ""

# ---- Step 1: Ensure DATA_DIR exists ----
log_info "Ensuring DATA_DIR exists..."
mkdir -p "${DATA_DIR}"
log_info "✓ DATA_DIR ready: ${DATA_DIR}"

# ---- Step 2: First-time init - copy default apps_config.json ----
if [ ! -f "${DATA_DIR}/apps_config.json" ]; then
    if [ -f "${PORTAL_DIR}/apps_config.json" ]; then
        log_warn "First install detected. Copying default apps_config.json to DATA_DIR..."
        cp "${PORTAL_DIR}/apps_config.json" "${DATA_DIR}/apps_config.json"
        log_info "✓ Default apps_config.json copied to DATA_DIR"
    else
        log_error "No apps_config.json found in repo or DATA_DIR!"
        exit 1
    fi
fi

# ---- Step 3: Create symlink for apps_config.json ----
log_info "Creating symlink: apps_config.json -> DATA_DIR..."
ln -sfn "${DATA_DIR}/apps_config.json" "${PORTAL_DIR}/apps_config.json"
log_info "✓ apps_config.json symlinked"

# ---- Step 4: Ensure data directory for DB exists in repo ----
mkdir -p "${PORTAL_DIR}/data"

# ---- Step 5: Create symlink for users.db (DB will be created by Flask if missing) ----
if [ -f "${DATA_DIR}/users.db" ]; then
    log_info "users.db found in DATA_DIR. Creating symlink..."
    ln -sfn "${DATA_DIR}/users.db" "${PORTAL_DIR}/data/users.db"
    log_info "✓ users.db symlinked"
else
    log_warn "users.db not yet in DATA_DIR. Will be initialized by Portal on first run."
    # Ensure the symlink target directory is correct so Flask writes to DATA_DIR
    # We set DATA_DIR env var in systemd, so Flask will use DATA_DIR directly
fi

# ---- Step 6: Set permissions ----
log_info "Setting permissions..."
chmod 755 "${DATA_DIR}"
if [ -f "${DATA_DIR}/apps_config.json" ]; then
    chmod 644 "${DATA_DIR}/apps_config.json"
fi
if [ -f "${DATA_DIR}/users.db" ]; then
    chmod 644 "${DATA_DIR}/users.db"
fi
log_info "✓ Permissions set"

# ---- Step 7: Verify ----
echo ""
echo "================================================"
echo "Sync Verification:"
echo "================================================"
if [ -L "${PORTAL_DIR}/apps_config.json" ]; then
    log_info "✓ apps_config.json is symlinked -> $(readlink -f "${PORTAL_DIR}/apps_config.json")"
else
    log_warn "⚠ apps_config.json is NOT a symlink (may be using direct file)"
fi

echo ""
log_info "✓ Data sync completed successfully."
echo "================================================"
