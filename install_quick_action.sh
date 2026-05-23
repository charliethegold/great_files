#!/usr/bin/env bash
#
# Installs the "Convert to Markdown" Quick Action into ~/Library/Services/.
# After running this, right-click any file in Finder -> Quick Actions ->
# Convert to Markdown. Output is written next to the original file.
#
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PY_SOURCE="$SCRIPT_DIR/convert_to_markdown.py"

if [[ ! -f "$PY_SOURCE" ]]; then
    echo "Error: convert_to_markdown.py not found next to this installer." >&2
    exit 1
fi

if [[ "$(uname)" != "Darwin" ]]; then
    echo "This installer is for macOS only." >&2
    exit 1
fi

INSTALL_DIR="$HOME/.local/share/convert-to-markdown"
SERVICE_DIR="$HOME/Library/Services/Convert to Markdown.workflow"

echo "Installing script to: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp "$PY_SOURCE" "$INSTALL_DIR/convert_to_markdown.py"
chmod +x "$INSTALL_DIR/convert_to_markdown.py"

# Optional dependency check (non-fatal).
echo
echo "Checking optional dependencies..."
for tool in pandoc tesseract pdftotext; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf "  found:   %s\n" "$tool"
    else
        printf "  missing: %s (install with: brew install %s)\n" "$tool" "$tool"
    fi
done
echo

echo "Creating Quick Action at: $SERVICE_DIR"
rm -rf "$SERVICE_DIR"
mkdir -p "$SERVICE_DIR/Contents"

cat > "$SERVICE_DIR/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSServices</key>
    <array>
        <dict>
            <key>NSMenuItem</key>
            <dict>
                <key>default</key>
                <string>Convert to Markdown</string>
            </dict>
            <key>NSMessage</key>
            <string>runWorkflowAsService</string>
            <key>NSRequiredContext</key>
            <dict>
                <key>NSApplicationIdentifier</key>
                <string>com.apple.finder</string>
            </dict>
            <key>NSSendFileTypes</key>
            <array>
                <string>public.item</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
PLIST

# The document.wflow is an Automator "Run Shell Script" action configured
# to receive files as arguments and pass them to our Python script.
SCRIPT_PATH_ESCAPED="${INSTALL_DIR//&/&amp;}/convert_to_markdown.py"
PYTHON_BIN="$(command -v python3 || echo /usr/bin/python3)"

cat > "$SERVICE_DIR/Contents/document.wflow" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AMApplicationBuild</key>
    <string>492</string>
    <key>AMApplicationVersion</key>
    <string>2.10</string>
    <key>AMDocumentVersion</key>
    <string>2</string>
    <key>actions</key>
    <array>
        <dict>
            <key>action</key>
            <dict>
                <key>AMAccepts</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Optional</key>
                    <true/>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.path</string>
                    </array>
                </dict>
                <key>AMActionVersion</key>
                <string>2.0.3</string>
                <key>AMApplication</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>AMParameterProperties</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <dict/>
                    <key>CheckedForUserDefaultShell</key>
                    <dict/>
                    <key>inputMethod</key>
                    <dict/>
                    <key>shell</key>
                    <dict/>
                    <key>source</key>
                    <dict/>
                </dict>
                <key>AMProvides</key>
                <dict>
                    <key>Container</key>
                    <string>List</string>
                    <key>Types</key>
                    <array>
                        <string>com.apple.cocoa.string</string>
                    </array>
                </dict>
                <key>ActionBundlePath</key>
                <string>/System/Library/Automator/Run Shell Script.action</string>
                <key>ActionName</key>
                <string>Run Shell Script</string>
                <key>ActionParameters</key>
                <dict>
                    <key>COMMAND_STRING</key>
                    <string>$PYTHON_BIN "$SCRIPT_PATH_ESCAPED" "\$@"</string>
                    <key>CheckedForUserDefaultShell</key>
                    <true/>
                    <key>inputMethod</key>
                    <integer>1</integer>
                    <key>shell</key>
                    <string>/bin/bash</string>
                    <key>source</key>
                    <string></string>
                </dict>
                <key>BundleIdentifier</key>
                <string>com.apple.RunShellScript</string>
                <key>CFBundleVersion</key>
                <string>2.0.3</string>
                <key>CanShowSelectedItemsWhenRun</key>
                <false/>
                <key>CanShowWhenRun</key>
                <true/>
                <key>Category</key>
                <array>
                    <string>AMCategoryUtilities</string>
                </array>
                <key>Class Name</key>
                <string>RunShellScriptAction</string>
                <key>InputUUID</key>
                <string>11111111-1111-1111-1111-111111111111</string>
                <key>Keywords</key>
                <array>
                    <string>Shell</string>
                    <string>Script</string>
                    <string>Command</string>
                </array>
                <key>OutputUUID</key>
                <string>22222222-2222-2222-2222-222222222222</string>
                <key>UUID</key>
                <string>33333333-3333-3333-3333-333333333333</string>
                <key>UnlocalizedApplications</key>
                <array>
                    <string>Automator</string>
                </array>
                <key>arguments</key>
                <dict/>
                <key>isViewVisible</key>
                <integer>1</integer>
                <key>location</key>
                <string>309.000000:253.000000</string>
                <key>nibPath</key>
                <string>/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib</string>
            </dict>
            <key>isViewVisible</key>
            <integer>1</integer>
        </dict>
    </array>
    <key>connectors</key>
    <dict/>
    <key>workflowMetaData</key>
    <dict>
        <key>serviceApplicationBundleID</key>
        <string>com.apple.finder</string>
        <key>serviceApplicationPath</key>
        <string>/System/Library/CoreServices/Finder.app</string>
        <key>serviceInputTypeIdentifier</key>
        <string>com.apple.Automator.fileSystemObject</string>
        <key>serviceOutputTypeIdentifier</key>
        <string>com.apple.Automator.nothing</string>
        <key>serviceProcessesInput</key>
        <integer>0</integer>
        <key>workflowTypeIdentifier</key>
        <string>com.apple.Automator.servicesMenu</string>
    </dict>
</dict>
</plist>
PLIST

# Tell macOS to rescan the Services directory so the new action shows up.
/System/Library/CoreServices/pbs -update >/dev/null 2>&1 || true

echo
echo "Done."
echo "Right-click any file in Finder -> Quick Actions -> 'Convert to Markdown'."
echo "If you don't see it immediately, open System Settings -> Keyboard ->"
echo "Keyboard Shortcuts -> Services, and tick 'Convert to Markdown'."
