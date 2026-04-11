#!/bin/bash
#
# Install Feynman Legal Skills
#
# Installs legal citation checking, brief auditing, and court decision
# analysis skills into your local Feynman installation.
#
# Usage:
#   bash install.sh
#   bash install.sh --uninstall
#

set -e

FEYNMAN_SKILLS_DIR="$HOME/.feynman/agent/skills"
FEYNMAN_PROMPTS_DIR="$HOME/.feynman/prompts"
FEYNMAN_CONFIG_DIR="$HOME/.feynman"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}==>${NC} $1"; }
warn()  { echo -e "${YELLOW}==>${NC} $1"; }
error() { echo -e "${RED}==>${NC} $1"; }

SKILLS=(
    "legal-cite-check"
    "legal-brief-audit"
    "legal-court-decision"
)

install_skills() {
    info "Installing Feynman Legal Skills..."

    # Check if Feynman is installed
    if [ ! -d "$FEYNMAN_CONFIG_DIR" ]; then
        error "Feynman config directory not found at $FEYNMAN_CONFIG_DIR"
        echo "  Install Feynman first: curl -fsSL https://feynman.is/install | bash"
        exit 1
    fi

    # Create directories if they don't exist
    mkdir -p "$FEYNMAN_SKILLS_DIR"
    mkdir -p "$FEYNMAN_PROMPTS_DIR"

    # Install each skill
    for skill in "${SKILLS[@]}"; do
        if [ -d "$SCRIPT_DIR/$skill" ]; then
            info "Installing skill: $skill"
            # Copy skill directory
            cp -r "$SCRIPT_DIR/$skill" "$FEYNMAN_SKILLS_DIR/"
            # Make scripts executable
            if [ -d "$FEYNMAN_SKILLS_DIR/$skill/scripts" ]; then
                chmod +x "$FEYNMAN_SKILLS_DIR/$skill/scripts/"*.py 2>/dev/null || true
            fi
        else
            warn "Skill directory not found: $skill (skipping)"
        fi
    done

    # Install prompt workflow
    if [ -d "$SCRIPT_DIR/prompts" ]; then
        info "Installing workflow prompts..."
        cp "$SCRIPT_DIR/prompts/"*.md "$FEYNMAN_PROMPTS_DIR/" 2>/dev/null || true
    fi

    # Check for CourtListener API token
    if [ -z "$COURTLISTENER_API_TOKEN" ] && [ ! -f "$FEYNMAN_CONFIG_DIR/courtlistener_token" ]; then
        echo ""
        warn "No CourtListener API token found."
        echo "  The legal skills work best with a free API token from CourtListener."
        echo "  1. Create a free account at https://www.courtlistener.com/sign-in/"
        echo "  2. Get your API token from https://www.courtlistener.com/profile/api/"
        echo "  3. Save it:"
        echo "     echo 'YOUR_TOKEN' > ~/.feynman/courtlistener_token"
        echo "  Or set the environment variable:"
        echo "     export COURTLISTENER_API_TOKEN='YOUR_TOKEN'"
        echo ""
    fi

    echo ""
    info "Installation complete!"
    echo ""
    echo "  Installed skills:"
    for skill in "${SKILLS[@]}"; do
        if [ -d "$FEYNMAN_SKILLS_DIR/$skill" ]; then
            echo "    - $skill"
        fi
    done
    echo ""
    echo "  Usage:"
    echo "    feynman \"check citations in my_brief.txt\""
    echo "    feynman \"audit the citations in motion_to_dismiss.pdf\""
    echo "    feynman \"analyze the court decision at 347 U.S. 483\""
    echo "    feynman legal-audit my_document.txt"
    echo ""
    echo "  For more info, see the SKILL.md file in each skill directory."
}

uninstall_skills() {
    info "Uninstalling Feynman Legal Skills..."

    for skill in "${SKILLS[@]}"; do
        if [ -d "$FEYNMAN_SKILLS_DIR/$skill" ]; then
            info "Removing skill: $skill"
            rm -rf "$FEYNMAN_SKILLS_DIR/$skill"
        fi
    done

    if [ -f "$FEYNMAN_PROMPTS_DIR/legal-audit.md" ]; then
        info "Removing workflow prompt: legal-audit.md"
        rm -f "$FEYNMAN_PROMPTS_DIR/legal-audit.md"
    fi

    echo ""
    info "Uninstall complete."
}

# Parse arguments
case "${1:-}" in
    --uninstall|-u)
        uninstall_skills
        ;;
    --help|-h)
        echo "Usage: bash install.sh [--uninstall]"
        echo ""
        echo "Install Feynman legal skills for citation checking,"
        echo "brief auditing, and court decision analysis."
        echo ""
        echo "Options:"
        echo "  --uninstall  Remove installed legal skills"
        echo "  --help       Show this help message"
        ;;
    *)
        install_skills
        ;;
esac
