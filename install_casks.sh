#!/bin/zsh

# List of apps to check and install
apps=(
    "fbreader"
    "brave-browser"
    "biglybt"
    "google-drive"
    "surfshark"
    "deepl"
    "libreoffice"
    "appcleaner"
    "iterm2"
    "visual-studio-code"
    "vlc"
    "anki"
    "telegram"
    "zoom"
    "grandperspective" 
    "keepassxc"
    "handbrake"
)

print_separator() {
    echo "\n=========================================="
    echo "$1"
    echo "==========================================\n"
}

print_status() {
    echo "→ $1"
}

# Make sure Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_separator "ERROR: Homebrew Not Found"
    echo "Homebrew is not installed. Please install it first by visiting:"
    echo "https://brew.sh"
    exit 1
fi

# Update Homebrew
print_separator "Updating Homebrew"
print_status "Checking for Homebrew updates..."
brew update

# Count for progress tracking
total_apps=${#apps[@]}
current_app=0

print_separator "Starting Installation Process"
echo "Total applications to process: $total_apps\n"

# For each app, check if it exists as a cask and install if found
for app in "${apps[@]}"; do
    ((current_app++))
    print_separator "Processing $app ($current_app of $total_apps)"
    
    print_status "Searching for $app in Homebrew Casks..."
    if brew search --casks "^${app}$" &> /dev/null; then
        if brew list --cask "${app}" &> /dev/null; then
            print_status "$app is already installed ✓"
        else
            print_status "Found $app in Homebrew Casks"
            print_status "Starting installation of $app..."
            brew install --cask "${app}"
            print_status "Installation of $app completed ✓"
        fi
    else
        print_status "⚠️  $app not found in Homebrew Casks - skipping"
    fi
done

print_separator "Installation Process Complete!"
echo "Summary:"
echo "- Attempted to process $total_apps applications"
echo "- Check the output above for any specific installation issues"
echo "- Some applications may require additional setup or configuration"